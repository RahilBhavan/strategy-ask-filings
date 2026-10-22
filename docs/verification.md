# Verification receipt

Purpose: record actual behavior, refusal boundaries and reproducibility.

Starting baseline: 14 tests passed at `897667f`, Python 3.14.7. Publication
verification: **23 tests pass** on Python 3.14.7 against ledger
`94c70044aaf14eea2ffb53deffd1a1f36bdec52e`. It adds frozen-data integrity, missing-cache refusal, source-byte
tampering, restore replay, symlink refusal, duplicate-identity ambiguity,
disclosed zero and the four denominator-date citation regressions.

```bash
python scripts/setup_ledger.py
python scripts/setup_ledger.py --offline
PYTHONPATH=tests/offline_guard python -m unittest discover -s tests -v
python -m compileall -q ask_filings scripts tests
python -m ask_filings --fields
python -m ask_filings 'bitcoin holdings on 2026-10-18'
python -m ask_filings 'remaining capacity STRC on 2026-10-18'
python -m ask_filings 'basic shares on 2026-07-24'
```

The saved holdings and shares examples were regenerated and compared byte for
byte. The latest STRC capacity command returns 17,510,800,000 USD. Separate CLI
processes produce identical holdings evidence. Tests use actual frozen SEC
bytes, not generated filing text, and block network connections including in
subprocesses. Setup initially downloads only pinned code from GitHub; no SEC
request, credential, package dependency or paid service is required.

Expected non-answers executed with exit 2:

```bash
python -m ask_filings 'bitcoin holdings on 2026-10-18' --as-of 2026-10-18
python -m ask_filings 'sats per basic share on 2026-10-18'
python -m ask_filings 'are daily dividends enacted'
```

The July 24 cover-page share observation is unavailable before its August 3
filing. The latest selector respects the filing cutoff. An absent same-date
weekly denominator never uses a cover-page roll-forward. Sale proceeds never
answer purchase-cost questions. Invalid dates, forecasts, arbitrary/injected
text, unsupported tickers and compound questions refuse. Early-2025 ratios
cite both inputs and retain rounded-in-thousands denominator context.

This verifies a nine-intent structured-fact interface. Human question coverage
outside documented templates, PDF/OCR, unseen layouts, historical amendments,
fresh SEC network hydration and comprehensive manual source interpretation
are not proven. See [publication](publication.md) for final clone and CI evidence.

Public-clone verification and GitHub CI passed; exact commit and run evidence
are recorded in [publication](publication.md). CI tests Python 3.11.14 and
3.14.0; local verification used Python 3.14.7.
