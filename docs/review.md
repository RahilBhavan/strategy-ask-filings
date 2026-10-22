# Correctness and publication review

Purpose: record proven failures and their regression evidence.

Scope: this repository, starting at `897667f`; sibling ledger read only.
Baseline: 14 tests passed, clean working tree. Reviewed correctness, error
handling, security, accessibility (CLI only), performance, dead code and local
conventions. No measured performance issue or dead-code removal survived review.

## Fixed and proven

- `ask_filings/engine.py`: changing `btc_held` in the CSV to `123` returned
  `123` while citations still hashed the original HTML. The query now checks
  the frozen table hash before reading rows. The altered-table CLI regression
  fails before the change and passes after it. This is consistency checking,
  not a claim that a hash alone proves financial truth.
  Altering both source bytes and their mutable manifest also previously passed;
  the manifest itself is now pinned, with a failing-then-passing CLI regression.
- `ask_filings/engine.py`: missing cache previously entered the SEC fetch path;
  absent an identifying User-Agent it reported a hydration error. Queries now
  refuse a missing cache before citation, so they cannot fetch implicitly.
  Missing-source and altered-source subprocess tests verify exit 2 and a
  structured reason. CI blocks sockets in parent and CLI subprocesses.
- Denominator-date regression: four early ratios omitted their source column
  dates (`1/12/2025`, `1/20/2025`, `1/26/2025`, `2/23/2025`) from the citation.
  Independent review reproduced this against the inherited ledger selector.
  The ledger owner fixed the selector in `94c7004`; Ask pins that reviewed
  code and its regression now passes across all five source-count weeks.

## Reproducibility

The original tests required a mutable adjacent checkout and untracked cache.
The portable v1 contract pins upstream code and checks the bundled original
sources, table hashes and archive hash. Setup replay repairs a corrupted table;
symlink restoration is refused without writing through it. No user-state
service exists, so persistence/retry testing covers snapshot restoration and
byte-identical repeated CLI answers.

The focused independent T3 review was read only. Its task ID was
`node:delegated-task:command%3Amcp%3Ab634ded8-f925-45df-a4d6-781cbe8b13a3%3Adelegate-task%3Aask-filings-correctness-review-1`.
It exercised 1,312 historical queries without exceptions and returned the
citation-date finding. This does not establish a financial accuracy benchmark
or manual review of every underlying filing.

## Limits retained

Nine full-match intents only; no LLM or embeddings. Evidence is a source
section, not a cell locator. No unsourced share roll-forward, no enactment
inference, no live completeness promise, no market calibration or security
certification. Fresh unseen layouts and filing amendments remain outside the
verified corpus. No license selected.

Checks after fixes: 23 tests pass against the pinned ledger, with network
connections blocked. Syntax compilation and staged size hook pass.
