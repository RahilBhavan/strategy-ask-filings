# Strategy ask filings: answer supported filing questions with exact evidence

[![Offline verification](https://github.com/RahilBhavan/strategy-ask-filings/actions/workflows/ci.yml/badge.svg)](https://github.com/RahilBhavan/strategy-ask-filings/actions/workflows/ci.yml)

A local natural-language CLI maps nine explicit question intents to Strategy filing fields. Each answer includes its value, units, dates, accession, source URL, original-byte hash and numbered normalized source sections. This is a deterministic grammar over structured facts; it calls no LLM or embedding model.

## What it does

- Answers holdings, purchases, purchase cost, USD Reserve/Cash, basic shares, issuance, remaining capacity and sourced sats/basic share.
- Reads 97 weekly observations, 432 program/action rows and 8 quarterly/annual cover-page anchors from the frozen ledger snapshot, through the October 19, 2026 weekly filing.
- Keeps separate ATM agreements separate and applies a filing-date knowledge cutoff.
- Refuses unsupported questions, invalid dates, ambiguous records and missing data. Current sats/share is unavailable without a same-date filed denominator.
- Saved real-source examples: [848,517 BTC as of October 18](examples/holdings.json) and [384,225,751 basic shares as of July 24](examples/shares.json), with exact evidence and different filing dates.

## How it works

`ask_filings/fields.py` defines semantic fields, units and full-match intent templates. `engine.py` filters exact dates and filing cutoffs, then delegates citation construction to the ledger's source evidence module. Derived ratios require both sourced inputs. There is no unrestricted document retrieval or generated answer prose.

## Run it

Python 3.11 or 3.14 and Git. No package dependencies, credentials or model API.
First setup clones the reviewed [ledger](https://github.com/RahilBhavan/strategy-8k-ledger)
commit into `~/scratch/strategy-ask-filings/`; it restores hashed source bytes
from this repository. GitHub access is needed once. Tests and answers then run offline.

```bash
git clone https://github.com/RahilBhavan/strategy-ask-filings.git
cd strategy-ask-filings
python scripts/setup_ledger.py
PYTHONPATH=tests/offline_guard python -m unittest discover -s tests -v
python -m ask_filings --fields
python -m ask_filings 'bitcoin holdings on 2026-10-18'
python -m ask_filings 'remaining capacity STRC on 2026-10-18'
python -m ask_filings 'basic shares on 2026-07-24'
```

Observed: **28 tests pass**, including a [56-case checked benchmark](docs/benchmark.md), on Python 3.14.7. The suite checks real source values/lines, cutoffs, absent denominators, multiple
programs, table/source tampering, missing cache and repeatable CLI output.
See [verification](docs/verification.md) for the executed count and environment.
For a custom checkout, use `--ledger` or `ASK_FILINGS_LEDGER`; see the
[dependency contract](docs/dependency.md).

Expected non-answer commands (exit 2):

```bash
python -m ask_filings 'bitcoin holdings on 2026-10-18' --as-of 2026-10-18
python -m ask_filings 'sats per basic share on 2026-10-18'
python -m ask_filings 'are daily dividends enacted'
```

## Repository layout

- `ask_filings/`: field catalog, deterministic routing, evidence answers and CLI.
- `examples/`: saved outputs from actual SEC sources.
- `tests/`: answers, refusals, time boundaries and CLI checks.
- `docs/`: scope, grammar, sources and verification.
- `fixtures/`: frozen SEC source archive, original manifest and dependency lock.
- `scripts/`: verified setup of the pinned public ledger.

## Documentation

- [Public design system](DESIGN.md): Rahil Design 3.3.0, shared tokens and visual review rules.

- [Spec](docs/spec.md): accepted v1 and criteria.
- [Benchmark](docs/benchmark.md): fixed expectations, category failures and five-minute replay.
- [Method](docs/method.md): exact templates and evidence contract.
- [Sources](docs/sources.md): primary source review and corpus limits.
- [Verification](docs/verification.md): executed commands and limits.
- [Dependency](docs/dependency.md): pinned v1 contract and offline restoration.

## Sources

SEC EDGAR CIK 1050446, via the commit-pinned ledger. Primary [October 19 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm) and [Q2 2026 10-Q cover](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm) were manually reopened October 21, 2026. This repository bundles 101 cited source documents and three table hashes; the full upstream corpus includes additional resources. [Source coverage](docs/sources.md) distinguishes spot checks from corpus parser tests.

## Scope and limits

- Independent local work, not affiliated with Strategy. No AI/LLM claim or account access.
- Nine supported intents, not general filing QA. Quarterly/annual mapping covers share counts only.
- Line numbers refer to deterministic normalized paragraphs/table rows, not original HTML lines. Evidence selects source sections, not individual-cell locators.
- Latest means latest in the frozen corpus filed by cutoff, not a live completeness promise. Printed values inherit filing rounding.
- Unsupported dividend-enactment queries refuse. The October 28 proposal remains pending as of October 21.

## License

No license file yet. No license has been selected; third-party filings retain their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
