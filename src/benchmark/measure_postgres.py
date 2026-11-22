import argparse
import csv
import os
import re
import subprocess
import sys
import time

TABELE = ['PATIENTS', 'ORGANIZATIONS', 'PROVIDERS', 'PAYERS', 'ENCOUNTERS', 'ALLERGIES', 'CONDITIONS',
          'OBSERVATIONS', 'PROCEDURES', 'MEDICATIONS', 'CLAIMS', 'CLAIMS_TRANSACTIONS']
LISTA = ','.join(f"'{t}'" for t in TABELE)

DOMYSLNY_PLIK = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'sql', 'postgres', '04_scenariusze_postgres.sql'))

SQL_METRYKI = f"""
SELECT
  (SELECT sum(pg_total_relation_size(c.oid)) FROM pg_class c
     WHERE c.relnamespace = 'public'::regnamespace AND c.relname IN ({LISTA})),
  (SELECT sum(pg_relation_size(c.oid)) FROM pg_class c
     WHERE c.relnamespace = 'public'::regnamespace AND c.relname IN ({LISTA})),
  (SELECT sum(n_dead_tup) FROM pg_stat_user_tables WHERE relname IN ({LISTA})),
  pg_current_wal_lsn(),
  (SELECT wal_records FROM pg_stat_wal),
  (SELECT wal_fpi FROM pg_stat_wal);
"""

SQL_SUMA_LOGICZNA = ' UNION ALL '.join(
    f"SELECT '{t}', count(*), coalesce(sum(hashtext(t::text)::bigint),0) FROM public.\"{t}\" t" for t in TABELE)

NAGLOWEK = ['scenariusz', 'proba', 'czas_ms', 'wal_bajty', 'wal_rekordy', 'wal_pelne_strony',
            'delta_rozmiar_calk_bajty', 'delta_rozmiar_sterty_bajty', 'delta_martwe_krotki',
            'wal_przywrocenia_bajty', 'logika_ok']


def psql(db, sql, quiet=True):
    cmd = ['psql', '-d', db, '-X', '-v', 'ON_ERROR_STOP=1', '-A', '-t', '-F', '|']
    if quiet:
        cmd.append('-q')
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def metryki(db):
    psql(db, 'SELECT pg_stat_clear_snapshot();')
    total, heap, dead, lsn, rec, fpi = psql(db, SQL_METRYKI).split('|')
    return int(total), int(heap), int(dead or 0), lsn, int(rec), int(fpi)


def wal_diff(db, lsn_a, lsn_b):
    return int(float(psql(db, f"SELECT pg_wal_lsn_diff('{lsn_b}', '{lsn_a}');")))


def wczytaj_bloki(plik):
    bloki, biezacy, nazwa = {}, [], None
    with open(plik, encoding='utf-8') as f:
        for linia in f:
            m = re.match(r'--\s*@@\s*(\S+)(\s+przywrocenie)?\s*$', linia)
            if m:
                if nazwa:
                    bloki[nazwa] = ''.join(biezacy)
                nazwa = m.group(1) + (':P' if m.group(2) else '')
                biezacy = []
            elif nazwa:
                biezacy.append(linia)
    if nazwa:
        bloki[nazwa] = ''.join(biezacy)
    return bloki


def run(db='ztb', plik=None, scenariusze=None, powtorzenia=1, sprawdz_logike=False,
        wynik='wyniki_pg.csv', bez_checkpoint=False):
    bloki = wczytaj_bloki(plik or DOMYSLNY_PLIK)
    ids = [k for k in bloki if not k.endswith(':P')]
    if scenariusze:
        ids = [s.strip() for s in scenariusze.split(',')]
        brak = [s for s in ids if s not in bloki]
        if brak:
            raise ValueError(f"Nieznane scenariusze: {brak}")

    suma0 = psql(db, SQL_SUMA_LOGICZNA) if sprawdz_logike else None
    nowy = not os.path.exists(wynik)
    with open(wynik, 'a', newline='') as f:
        w = csv.writer(f)
        if nowy:
            w.writerow(NAGLOWEK)
        for sid in ids:
            for proba in range(1, powtorzenia + 1):
                if not bez_checkpoint:
                    psql(db, 'CHECKPOINT;')
                t0_total, t0_heap, t0_dead, lsn0, rec0, fpi0 = metryki(db)
                t = time.perf_counter()
                psql(db, bloki[sid])
                ms = (time.perf_counter() - t) * 1000
                t1_total, t1_heap, t1_dead, lsn1, rec1, fpi1 = metryki(db)
                wal = wal_diff(db, lsn0, lsn1)
                wal_p = ''
                if sid + ':P' in bloki:
                    psql(db, bloki[sid + ':P'])
                    _, _, _, lsn2, _, _ = metryki(db)
                    wal_p = wal_diff(db, lsn1, lsn2)
                ok = ''
                if sprawdz_logike:
                    ok = psql(db, SQL_SUMA_LOGICZNA) == suma0
                row = [sid, proba, round(ms, 1), wal, rec1 - rec0, fpi1 - fpi0, t1_total - t0_total,
                       t1_heap - t0_heap, t1_dead - t0_dead, wal_p, ok]
                w.writerow(row)
                f.flush()
                print(' | '.join(str(x) for x in row), flush=True)
                if sprawdz_logike and not ok:
                    raise RuntimeError(f'Po cyklu {sid} zawartość logiczna różni się od wyjściowej')


def run_call(db, scenariusz, params, wynik='wyniki_pg_python.csv', bez_checkpoint=False):
    from benchmark.database import postgres as bck
    fn = getattr(bck, scenariusz, None)
    if fn is None or scenariusz.startswith('_'):
        raise ValueError(f"Nieznana funkcja: {scenariusz}")
    if not bez_checkpoint:
        psql(db, 'CHECKPOINT;')
    t0_total, t0_heap, t0_dead, lsn0, rec0, fpi0 = metryki(db)
    t = time.perf_counter()
    wynik_funkcji = fn(**params)
    ms = (time.perf_counter() - t) * 1000
    t1_total, t1_heap, t1_dead, lsn1, rec1, fpi1 = metryki(db)
    row = [scenariusz, 1, round(ms, 1), wal_diff(db, lsn0, lsn1), rec1 - rec0, fpi1 - fpi0,
           t1_total - t0_total, t1_heap - t0_heap, t1_dead - t0_dead, '', '']
    nowy = not os.path.exists(wynik)
    with open(wynik, 'a', newline='') as f:
        w = csv.writer(f)
        if nowy:
            w.writerow(NAGLOWEK)
        w.writerow(row)
    print(' | '.join(str(x) for x in row), flush=True)
    return wynik_funkcji


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='ztb')
    ap.add_argument('--plik', default=DOMYSLNY_PLIK)
    ap.add_argument('--scenariusze', default=None, help='np. C1,C2,U4 (domyślnie wszystkie)')
    ap.add_argument('--powtorzenia', type=int, default=1)
    ap.add_argument('--sprawdz-logike', action='store_true')
    ap.add_argument('--wynik', default='wyniki_pg.csv')
    ap.add_argument('--bez-checkpoint', action='store_true',
                    help='nie wykonuj CHECKPOINT przed scenariuszem (domyślnie wykonuje, '
                         'żeby każdy pomiar startował z tego samego stanu zapisu pełnych stron do WAL)')
    a = ap.parse_args(argv)
    try:
        run(db=a.db, plik=a.plik, scenariusze=a.scenariusze, powtorzenia=a.powtorzenia,
            sprawdz_logike=a.sprawdz_logike, wynik=a.wynik, bez_checkpoint=a.bez_checkpoint)
    except (RuntimeError, ValueError) as e:
        sys.exit(f'BŁĄD: {e}')


if __name__ == '__main__':
    main()
