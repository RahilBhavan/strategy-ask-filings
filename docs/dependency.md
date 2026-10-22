# Portable ledger dependency

Purpose: define the reviewed v1 boundary and reproducible setup.

Ask Filings imports `ledger.build.read(name)` and `ledger.evidence.cite(row,
field)` from the exact commit in [ledger-lock.json](../fixtures/ledger-lock.json).
It consumes `weekly.csv`, `instrument_weekly.csv` and `share_anchors.csv` with
unchanged v1 column names. The CLI does not rebuild or hydrate from SEC.
The default checkout is `~/scratch/strategy-ask-filings/ledger-<commit>`.

```bash
python scripts/setup_ledger.py
python scripts/setup_ledger.py --offline
PYTHONPATH=tests/offline_guard python -m unittest discover -s tests -v
```

First setup needs GitHub access and Git, but no SEC credentials or dependencies
from a package index. Subsequent setup, answers and tests are offline. Setup
verifies the pinned checkout commit and entire local source archive. Repeating
it restores identical data and repairs interrupted or altered cache writes.
A directory already at another commit is refused rather than reset. To use
another location, pass `--ledger` to setup and CLI, and export
`ASK_FILINGS_LEDGER` for the tests. Use a disk-backed scratch directory.

The bundle contains the complete three query tables and all their cited source
documents, not synthetic fixtures. `tests/offline_guard/sitecustomize.py` blocks
socket connections in the test process and CLI subprocesses. CI downloads the
pinned code once, then runs real offline answers, refusals and tamper tests.
There is no static type checker configured for this unannotated Python v1;
CI also compiles all Python modules to check syntax.

Only reviewed, trusted ledger code is executable input. Table and source hashes
protect the frozen evidence contract; they do not sandbox Python or validate an
arbitrary upstream parser. Separate programs remain separate rows. No storage
service or user-state persistence exists; retry behavior means deterministic
reads and repeatable snapshot restoration.
