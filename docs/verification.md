# Verification receipt

Purpose: record real answers, refusal behavior and replay. Executed 2026-10-21 America/Detroit, Python 3.14.7.

```bash
python -m unittest discover -s tests -v
python -m ask_filings --fields
python -m ask_filings 'bitcoin holdings on 2026-10-18'
python -m ask_filings 'remaining capacity STRC on 2026-10-18'
python -m ask_filings 'basic shares on 2026-07-24'
```

14 tests pass. Values, source lines and hashes are checked against actual cached SEC 8-K and 10-Q content. Tests cover purchases, cost, USD Reserve/Cash, MSTR issuance, STRC capacity, cover-page class A+B shares, multiple ATM programs, exact dates and filing cutoffs. The July 24 share count remains unavailable before its August 3 filing; October 18 holdings remain unavailable on October 18. The latest selector respects the filing cutoff.

Expected non-answers were also executed, all exit 2:

```bash
python -m ask_filings 'bitcoin holdings on 2026-10-18' --as-of 2026-10-18
python -m ask_filings 'sats per basic share on 2026-10-18'
python -m ask_filings 'are daily dividends enacted'
```

Tests reject invalid dates, arbitrary/injected text, unsupported tickers, forecasts and compound questions. Sourced early-2025 sats/share is calculated from two cited fields; the current denominator refuses instead of using the inherited model. Repeat CLI processes return byte-identical saved holdings evidence. Sources are not interpreted as instructions.

This is a tested nine-intent structured-fact interface, not an unrestricted natural-language benchmark, LLM system or full quarterly financial-statement extraction. Human question coverage outside the documented templates, OCR/PDFs, unseen layouts, historical amendments and fresh SEC network hydration are not proven here. The upstream ledger documents parser/cache checks and the local corpus.
