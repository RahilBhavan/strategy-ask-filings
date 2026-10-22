# Checked question benchmark

This is a developer-authored regression set, reviewed October 22, 2026. Its
questions model plausible supported requests and refusal boundaries; they are
not collected user questions, a user study or a statistical accuracy sample.

## Five-minute replay

From this repository, with Python 3.11 or 3.14 and Git:

```bash
python scripts/setup_ledger.py
PYTHONPATH=tests/offline_guard python -m ask_filings.benchmark
PYTHONPATH=tests/offline_guard python -m unittest discover -s tests -v
python -m ask_filings 'How much bitcoin did Strategy hold  on 2026-10-18?'
python -m ask_filings ''
```

The last command intentionally exits 2 with JSON `status: refused`. Setup needs
GitHub once; subsequent runs are offline. On Python 3.14.7 the standalone
56-case benchmark took **4.367 seconds** locally (one observed run, no latency
promise). Two fresh benchmark processes emitted byte-identical reports.
The entire 28-test suite took about 5.3 seconds locally. No package install,
credentials, SEC download or model is needed after setup.

## Contract and failure reports

[The fixed set](../benchmarks/cases.json) has 56 cases and 29 shared expectation
files. Every intent has a canonical, documented paraphrase and whitespace
variant. Additional cases exercise latest-in-snapshot selection, filing cutoff,
future observation dates, missing fields/denominators/programs, disclosed zero,
two ATM programs, sale-cost refusal, invalid input, unsupported questions and
trailing hostile instructions. Missing/altered source cases run with isolated
copies of code/tables/manifest under disk-backed scratch; they never alter the
configured checkout or the archive. Scratch fault copies are deleted afterward.

The report includes the suite SHA-256, pinned ledger commit, counts by **intent**
and **category**, and each failing case's ID, question and exact JSON mismatch
paths. It exits 0 only with no mismatches, 1 for mismatches, and 2 for invalid
suite configuration. Unexpected CLI output, timeout or source-read errors count
as failures. For example a deliberately wrong holdings expectation yields
`$.result.facts[0].value` and a failure in both `canonical` and `bitcoin holdings`.
The tests execute that negative example and check the nonzero exit.

Expectations compare all response metadata, exact decimal strings, units,
dates, formulas, program/currency identity, status, reason and exit code.
Each citation retains accession, URL, original-byte hash, derivation and line
numbers. To avoid adding filing prose, normalized sections are represented by
SHA-256 over UTF-8 canonical JSON (`sort_keys=True`, `ensure_ascii=True`, compact
separators) of the full ordered line objects. Local source bytes are independently
re-hashed and compared too. Missing/extra facts or citations fail. There is no
runtime golden update option; changes to expectations require review in Git.

## Oracle provenance and checks

The oracle records were initially captured from the pinned deterministic engine,
then answer values were cross-checked against exact rows in the frozen tables.
The automated oracle-consistency test independently joins expected dates,
programs, tickers, actions and accessions to those rows, checks units and cutoff,
recomputes the ratio from its two inputs, joins citations to the source manifest
and re-hashes local bytes. Golden normalized-section fingerprints freeze the
existing selector; they are regression evidence, not independent proof that
every selected section is the best financial citation.

Ledger commit remains `94c70044aaf14eea2ffb53deffd1a1f36bdec52e`; the three table
hashes, original manifest and 101 bundled documents are unchanged. See
[lock](../fixtures/ledger-lock.json) and [source provenance](sources.md).
Primary sources reopened with the browser on October 22, 2026:

- [October 19 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm): checked the BTC table, MSTR issuance, and reserve/cash balances against canonical expectations. The frozen table values and byte hashes remain authoritative for replay.
- [Q2 2026 10-Q cover](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm): checked the July 24 class A/B counts supporting the basic-share sum.

No new vendor text or source documents were copied into Git. Historical ratio,
cutoff and multiple-program cases rely on the frozen source/table contract;
this pass does not claim a new manual review of every historical filing.

## Proven changes and limits

Baseline `2722b79` passes the original 23 tests. Running the new benchmark in an
isolated copy with that baseline's engine/CLI yields **44/56 passing**, exit 1.
The 12 differences are nine whitespace variants, explicit empty input producing
usage text instead of JSON, and two platform-specific date-error reasons.
After the fixes, **56/56 pass across 12 categories**, and all **28 tests pass**.
Wrong answer values, source hashes, local-byte hashes and source-section
fingerprints each produce a failing mismatch path in mutation checks.

Whitespace normalizes only after the original 500-character limit; the full
question still must match a documented template. Empty supplied questions now
refuse as JSON, while an omitted question remains a usage error. Dates now have
one stable ISO-date refusal reason across supported Python versions.

This is nine-intent structured lookup, with no LLM, semantic retrieval or general
QA. The set does not measure production question prevalence or unseen-layout
accuracy. A post-snapshot cutoff still returns frozen-corpus answers with the
existing freshness warning; it never establishes live completeness. Source
sections remain normalized blocks, not cell locators; financial rounding and
same-date denominator limits remain. Duplicate-identity ambiguity and altered
table/manifest safeguards remain covered by the original behavior tests rather
than synthetic data migrations in the question set.
