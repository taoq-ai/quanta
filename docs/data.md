# Dataset & provenance

Quanta's read-only analytics replica is built from a **real, public** dataset so
the demo runs on believable numbers rather than hand-waved fixtures.

## Source

**Online Retail II** — UCI Machine Learning Repository (dataset ID 502).

- Real transactions for a UK-based online retailer, 01/12/2009 – 09/12/2011.
- ~1,000,000 rows: invoices, stock codes, product descriptions, quantities,
  prices, customer IDs, and countries.
- Download (used by `quanta-load-data`):
  `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip`

### Citation

> Chen, D. (2019). *Online Retail II* [Dataset]. UCI Machine Learning Repository.
> https://doi.org/10.24432/C5CG6D
>
> Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail
> industry: A case study of RFM model-based customer segmentation using data
> mining. *Journal of Database Marketing & Customer Strategy Management*, 19(3),
> 197–208.

Licensed under CC BY 4.0 (per the UCI repository). No personal data of *your*
users is involved; within the demo's narrative these customer rows stand in for
"sensitive data that must not leave."

## Replica schema

`quanta-load-data` builds a single denormalised `invoices` table (the read-only
analytics replica):

| column | type | notes |
|---|---|---|
| `invoice_no` | TEXT | invoice identifier |
| `stock_code` | TEXT | product code |
| `description` | TEXT | product description |
| `quantity` | INTEGER | units on the line |
| `invoice_date` | TEXT | ISO timestamp |
| `price` | REAL | unit price |
| `customer_id` | TEXT | customer identifier (the "sensitive" field) |
| `country` | TEXT | customer country |
| `month` | TEXT | `YYYY-MM`, derived for grouping |

Indexed on `country`, `customer_id`, and `month` to keep the allowlisted metric
queries fast.

## Offline / CI mode

`quanta-load-data --synthetic` generates a deterministic, Online-Retail-II-shaped
sample (no download), used by the test suite and for environments without
network access. The real loader is the default; it falls back to synthetic if the
download fails.
