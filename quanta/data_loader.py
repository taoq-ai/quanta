"""Build the read-only analytics replica from the UCI Online Retail II dataset.

Dataset: Online Retail II, UCI Machine Learning Repository (ID 502).
Provenance: Chen, D. (2019). *Online Retail II*. Real transactions for a UK
online retailer, 2009-2011. See docs/data.md for citation and licence.

Usage:
    quanta-load-data                 # download real UCI data, build analytics.db
    quanta-load-data --synthetic     # offline: deterministic sample (tests/CI)
    quanta-load-data --rows 50000    # cap rows for a faster demo build
"""

from __future__ import annotations

import argparse
import sqlite3
import urllib.request
from pathlib import Path

from quanta.config import DEFAULT_DB_PATH

UCI_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
_CACHE = Path(__file__).resolve().parent / "data" / "online_retail_II.zip"

_SCHEMA = """
CREATE TABLE invoices (
    invoice_no   TEXT,
    stock_code   TEXT,
    description  TEXT,
    quantity     INTEGER,
    invoice_date TEXT,
    price        REAL,
    customer_id  TEXT,
    country      TEXT,
    month        TEXT
);
CREATE INDEX idx_country ON invoices(country);
CREATE INDEX idx_customer ON invoices(customer_id);
CREATE INDEX idx_month ON invoices(month);
"""


def _create_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript(_SCHEMA)
    return conn


def _insert(conn: sqlite3.Connection, rows: list[tuple]) -> None:
    conn.executemany(
        "INSERT INTO invoices (invoice_no, stock_code, description, quantity, "
        "invoice_date, price, customer_id, country, month) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def load_real(db_path: Path, row_cap: int | None) -> int:
    """Download + parse the real UCI Online Retail II workbook."""
    import zipfile

    import pandas as pd  # local import; only needed for the real loader

    if not _CACHE.exists():
        _CACHE.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading UCI Online Retail II -> {_CACHE} ...")
        urllib.request.urlretrieve(UCI_URL, _CACHE)  # noqa: S310 - fixed UCI URL

    with zipfile.ZipFile(_CACHE) as zf:
        xlsx_name = next(n for n in zf.namelist() if n.lower().endswith(".xlsx"))
        with zf.open(xlsx_name) as fh:
            frames = pd.read_excel(fh, sheet_name=None, engine="openpyxl")
    df = pd.concat(frames.values(), ignore_index=True)
    df = df.dropna(subset=["Invoice", "Quantity", "Price"])
    if row_cap:
        df = df.head(row_cap)

    conn = _create_db(db_path)
    rows = [
        (
            str(r.Invoice),
            str(r.StockCode),
            str(r.Description),
            int(r.Quantity),
            str(r.InvoiceDate),
            float(r.Price),
            "" if pd.isna(getattr(r, "_7", None)) else str(getattr(r, "Customer ID", "")),
            str(r.Country),
            str(r.InvoiceDate)[:7],
        )
        for r in df.itertuples(index=False)
    ]
    _insert(conn, rows)
    conn.close()
    return len(rows)


def load_synthetic(db_path: Path, n: int = 5000) -> int:
    """Deterministic, offline sample shaped like Online Retail II."""
    countries = [
        ("United Kingdom", 0.50),
        ("Germany", 0.12),
        ("France", 0.10),
        ("EIRE", 0.08),
        ("Spain", 0.05),
        ("Netherlands", 0.05),
        ("Belgium", 0.04),
        ("Portugal", 0.03),
        ("Australia", 0.02),
        ("Norway", 0.01),
    ]
    products = [
        ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.55),
        ("71053", "WHITE METAL LANTERN", 3.39),
        ("84406B", "CREAM CUPID HEARTS COAT HANGER", 2.75),
        ("22423", "REGENCY CAKESTAND 3 TIER", 12.75),
        ("47566", "PARTY BUNTING", 4.95),
        ("84879", "ASSORTED COLOUR BIRD ORNAMENT", 1.69),
        ("22720", "SET OF 3 CAKE TINS PANTRY DESIGN", 4.95),
    ]
    cum: list[tuple[str, float]] = []
    acc = 0.0
    for name, w in countries:
        acc += w
        cum.append((name, acc))

    def pick_country(x: float) -> str:
        for name, edge in cum:
            if x <= edge:
                return name
        return cum[-1][0]

    conn = _create_db(db_path)
    rows: list[tuple] = []
    for i in range(n):
        country = pick_country(((i * 2654435761) % 1000) / 1000.0)
        stock, desc, price = products[i % len(products)]
        qty = 1 + (i % 12)
        month = f"2010-{1 + (i % 12):02d}"
        date = f"{month}-{1 + (i % 27):02d} 1{i % 2}:30:00"
        customer = f"{12000 + (i % 900)}"  # ~900 customers — customer-level PII
        invoice = f"5{36000 + (i % 4000)}"
        rows.append((invoice, stock, desc, qty, date, price, customer, country, month))
    _insert(conn, rows)
    conn.close()
    return len(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Build Quanta's read-only analytics replica.")
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--synthetic", action="store_true", help="offline deterministic sample")
    p.add_argument("--rows", type=int, default=None, help="row cap for the real loader")
    args = p.parse_args()

    if args.synthetic:
        n = load_synthetic(args.db)
        print(f"Built SYNTHETIC analytics replica: {n} rows -> {args.db}")
    else:
        try:
            n = load_real(args.db, args.rows)
            print(f"Built analytics replica from UCI Online Retail II: {n} rows -> {args.db}")
        except Exception as exc:  # noqa: BLE001
            print(f"Real loader failed ({exc}); falling back to synthetic sample.")
            n = load_synthetic(args.db)
            print(f"Built SYNTHETIC analytics replica: {n} rows -> {args.db}")


if __name__ == "__main__":
    main()
