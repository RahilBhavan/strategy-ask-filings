# Strategy ask filings: answer supported filing questions with exact evidence

A local natural-language CLI maps nine explicit question intents to Strategy filing fields. Each answer includes its value, units, dates, accession, source URL, original-byte hash and numbered normalized source sections. This is a deterministic grammar over structured facts; it calls no LLM or embedding model.

## What it does

- Answers holdings, purchases, purchase cost, USD Reserve/Cash, basic shares, issuance, remaining capacity and sourced sats/basic share.
- Reads 97 weekly observations, 432 program/action rows and 8 quarterly/annual cover-page anchors from the adjacent ledger, through the October 19, 2026 weekly filing.
- Keeps separate ATM agreements separate and applies a filing-date knowledge cutoff.
- Refuses unsupported questions, invalid dates, ambiguous records and missing data. Current sats/share is unavailable without a same-date filed denominator.
- Saved real-source examples: [848,517 BTC as of October 18](examples/holdings.json) and [384,225,751 basic shares as of July 24](examples/shares.json), with exact evidence and different filing dates.

## How it works

`ask_filings/fields.py` defines semantic fields, units and full-match intent templates. `engine.py` filters exact dates and filing cutoffs, then delegates citation construction to the ledger's source evidence module. Derived ratios require both sourced inputs. There is no unrestricted document retrieval or generated answer prose.

## Run it

Python 3.11+; tested with Python 3.14.7. No dependencies, credentials or model API. Keep the ledger adjacent, or pass `--ledger /path/to/strategy-8k-ledger`.

```bash
cd /home/rahil/projects/strategy-8k-ledger
python -m ledger restore
python -m ledger hydrate
cd /home/rahil/projects/strategy-ask-filings
python -m unittest discover -s tests -v
python -m ask_filings --fields
python -m ask_filings 'bitcoin holdings on 2026-10-18'
python -m ask_filings 'remaining capacity STRC on 2026-10-18'
python -m ask_filings 'basic shares on 2026-07-24'
```

Observed: **14 tests pass**, including actual source values/lines, historical knowledge cutoffs, invalid/unsupported text, absent denominators, multiple programs and repeatable CLI output. Tests and answers are offline with the existing local cache; a fresh copy needs the ledger's verified source hydration.

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

## Documentation

- [Spec](docs/spec.md): accepted v1 and criteria.
- [Method](docs/method.md): exact templates and evidence contract.
- [Sources](docs/sources.md): primary source review and corpus limits.
- [Verification](docs/verification.md): executed commands and limits.

## Sources

SEC EDGAR CIK 1050446, via `../strategy-8k-ledger`. Primary [October 19 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm) and [Q2 2026 10-Q cover](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm) were manually reopened October 21, 2026. The ledger stores SHA-256 hashes for all 184 resources, including indexes and exhibits. [Source coverage](docs/sources.md) distinguishes spot checks from corpus parser tests.

## Scope and limits

- Independent local work, not affiliated with Strategy. No AI/LLM claim, account access or publication.
- Nine supported intents, not general filing QA. Quarterly/annual mapping covers share counts only.
- Line numbers refer to deterministic normalized paragraphs/table rows, not original HTML lines. Evidence selects source sections, not individual-cell locators.
- Latest means latest in the frozen corpus filed by cutoff, not a live completeness promise. Printed values inherit filing rounding.
- Unsupported dividend-enactment queries refuse. The October 28 proposal remains pending as of October 21.

## License

No license file yet. No license has been selected; third-party filings retain their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
