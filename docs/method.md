# Supported questions and evidence

Purpose: describe the deterministic grammar and its refusal boundary.

`ask_filings/fields.py` is the semantic field layer: name, source column, units, table and accepted intent expression. `--fields` exports it as JSON. Each template accepts an optional `on YYYY-MM-DD`, `for YYYY-MM-DD` or `at YYYY-MM-DD` suffix and an optional question mark. Whitespace runs (spaces, tabs and line breaks) normalize to one space before matching; the 500-character limit applies to the original input. Matching is case-insensitive and anchored to the entire question. Multiple questions or arbitrary trailing instructions refuse.

Examples of accepted base templates:

- `bitcoin holdings` / `how much bitcoin did strategy hold`
- `bitcoin purchased` / `how much bitcoin did strategy buy`
- `bitcoin purchase cost` / `how much did strategy spend on bitcoin`
- `usd reserve` / `what was the usd reserve`
- `usd cash` / `what was the usd cash`
- `basic shares` / `how many basic shares were outstanding`
- `issuance MSTR` / `how much did strategy issue in MSTR`
- `remaining capacity STRC` / `how much capacity remained for STRC`
- `sats per basic share` / `what were sats per basic share`

Issuance/capacity accept MSTR, STRC, STRD, STRF, STRK or STRE. A recognized ticker with no matching data is unavailable, not zero. Separate ATM programs stay separate. Dates specify exact observation dates, not a nearest-date lookup. Without a date, choose the latest observation **in the frozen corpus** filed by `--as-of` (default October 21, 2026). The latest cover-page basic-share observation differs from the latest weekly holdings date. A known observation after the filing cutoff remains unavailable even if its economic date is earlier.

Answers include the semantic field, units, period/as-of date, filing date, accession, SEC URL, original-byte SHA-256 and numbered normalized paragraph/table-row lines. The ledger's evidence module supplies source sections, keeping header units and dates beside values. These are not original HTML line numbers or claims of individual-cell attribution. Repeat the command to replay the same source lines; use `ledger.evidence.source_lines(url)` to inspect the full numbering.

The only ratios supported are sats/basic share with both BTC holdings and a same-date denominator printed in the weekly filing. The five early-2025 denominators are rounded in thousands. Current-week queries refuse because no such denominator is disclosed. No cover-page roll-forward is substituted. Cover-page `basic` is class A + class B, with that formula labeled. It is not an assumed-diluted KPI.

Purchase-cost questions in sale weeks refuse: the inherited USD field then represents sale proceeds. Queries verify table and source-manifest hashes against the frozen contract. Citations verify source bytes against the ledger manifest before returning evidence. A missing source cache refuses; asking never triggers network hydration.

Unsupported questions return `refused`; supported questions with missing data return `unavailable`; competing filings for the same observation/program return `ambiguous`. All exit 2. Answers exit 0. This is a structured-fact query interface, not unrestricted semantic retrieval, an LLM, AI or financial advice. It does not answer accounting-policy, revenue, legal, forecast or dividend-enactment questions.

Explicit empty questions return structured JSON refusal; omitting the question entirely remains an argparse usage error. Invalid question/cutoff dates use the stable reason `date must be ISO YYYY-MM-DD`.
