# Strategy ask filings: no LLM, every answer cites the filing

Ask a plain question about how much bitcoin Strategy (MSTR) holds or bought, or how many shares it has, and get the number from its SEC filing with the exact lines it came from.

[![Offline verification](https://github.com/RahilBhavan/strategy-ask-filings/actions/workflows/ci.yml/badge.svg)](https://github.com/RahilBhavan/strategy-ask-filings/actions/workflows/ci.yml)

![Terminal recording: the question "bitcoin holdings on 2026-10-18" returns 848,517 BTC with the October 19, 2026 8-K's URL, accession number, hash and source lines; "what is the mNAV" is refused because the filings state no market prices.](docs/demo.gif)

A local CLI maps nine question types, asked in plain phrasings, to fields in Strategy's SEC filings. No language model is involved. A fixed grammar picks the field, and the engine reads it from a frozen, hashed copy of the filings. Every answer prints its value, units, dates, accession number, source URL, source-file hash and the numbered source lines. A question it cannot answer from a filing is refused with a reason, and a refusal carries no citation.

## What it does

- Answers holdings, purchases, purchase cost, USD Reserve/Cash, basic shares, issuance, remaining capacity and sourced sats/basic share.
- Reads 97 weekly observations, 432 program/action rows and 8 quarterly/annual cover-page anchors from the frozen ledger snapshot, through the October 19, 2026 weekly filing.
- Keeps separate ATM agreements separate and applies a filing-date knowledge cutoff.
- Refuses unsupported questions, invalid dates, ambiguous records and missing data. Sats per basic share needs a share count filed for the same date, so the current value is unavailable.
- Saved real-source examples: [848,517 BTC as of October 18](examples/holdings.json) and [384,225,751 basic shares as of July 24](examples/shares.json), with exact evidence and different filing dates.

## How it works

`ask_filings/fields.py` defines the fields, units and full-match question templates. `engine.py` filters exact dates and filing cutoffs, then builds citations with the ledger's source evidence module. A derived ratio cites both of its inputs. There is no free-text retrieval and no generated answer prose. The only network code is the pinned ledger's SEC downloader, which answering never calls; the tests block network connections.

## Run it

Python 3.11 or 3.14 and Git. No package dependencies, credentials or model API.
First setup clones the reviewed [ledger](https://github.com/RahilBhavan/strategy-8k-ledger)
commit into `.ask-filings/` inside this repository (git-ignored; set
`ASK_FILINGS_HOME` to use another directory); it restores hashed source bytes
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

Each answer prints one line first, then any note and the numbered source lines. Add `--json` for the full result with hashes:

```text
Answer: bitcoin holdings: 848,517 BTC, as of 2026-10-18 (period 2026-10-12 to 2026-10-18), filed 2026-10-19
Evidence:
  btc_held from https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm
    accession 0001193125-26-424688, filed 2026-10-19, sha256 758fffb5bae0...
    normalized lines 50-57, 77-78, 82
      ...
      55: 267 | 22.1 | 82,900 | 848,517 | 64.02 | 75,446
```

Example phrasings (all in the benchmark):

| Ask | Answer |
|---|---|
| `latest bitcoin holdings` | 848,517 BTC as of 2026-10-18 |
| `bitcoin purchased on 2026-03-12` | 22,337 BTC for the period 2026-03-09 to 2026-03-15 that contains the date, with a note saying so |
| `bitcoin purchased week of 2026-03-09` | the same period total |
| `bitcoin purchased between 2026-03-02 and 2026-03-22` | three weekly values and a 41,362 BTC total |
| `issuance MSTR on 2026-10-18` | $22,000,000 USD net proceeds (MSTR Stock) |
| `remaining capacity STRC on 2026-10-18` | $17,510,800,000 USD |
| `How much bitcoin did Strategy hold for 2026-10-18?` | 848,517 BTC |
| `bitcoin holdings on 2026-10-17` | unavailable: balances are filed only at period end; ask for 2026-10-18 |

Templates: `python -m ask_filings --fields`. Dates may follow `on`, `for`, `at`, `as of` or `week of`; ranges use `between A and B` or `from A to B`. Ranges include only whole periods inside the range and total only flow fields (purchases, cost, issuance).

Observed: **34 tests pass**, including a [75-case checked benchmark](docs/benchmark.md), on Python 3.14.7. In that benchmark, all 47 answered cases cite an accession, URL and source lines; the other 28 cases are refusals or unavailable results. The suite also checks cutoffs, absent denominators, multiple programs, table and source tampering, a missing cache and repeatable CLI output. See [verification](docs/verification.md).
For a custom checkout, use `--ledger` or `ASK_FILINGS_LEDGER`; see the
[dependency contract](docs/dependency.md).

Expected non-answer commands (exit 2):

```bash
python -m ask_filings 'bitcoin holdings on 2026-10-18' --as-of 2026-10-18
python -m ask_filings 'sats per basic share on 2026-10-18'
python -m ask_filings 'are daily dividends enacted'
python -m ask_filings 'what is the mNAV'
```

mNAV refuses because it needs market prices (MSTR share price and bitcoin price) that the filings do not state.

To regenerate the terminal recording at the top from fresh CLI runs (needs Pillow and a monospace TTF font; pass `--font` if none is found):

```bash
python scripts/render_demo_gif.py
```

## Repository layout

- `ask_filings/`: field catalog, deterministic routing, evidence answers and CLI.
- `examples/`: saved outputs from actual SEC sources.
- `tests/`: answers, refusals, time boundaries and CLI checks.
- `docs/`: scope, grammar, sources and verification.
- `fixtures/`: frozen SEC source archive, original manifest and dependency lock.
- `scripts/`: verified setup of the pinned public ledger, and `render_demo_gif.py`, which regenerates `docs/demo.gif` from real CLI runs.

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

- Independent local work, not affiliated with Strategy. No account access.
- Nine supported intents, not general filing QA. Quarterly/annual mapping covers share counts only.
- Line numbers refer to deterministic normalized paragraphs/table rows, not original HTML lines. Evidence selects source sections, not individual-cell locators.
- "Latest" means latest in the frozen corpus filed by the cutoff date, not a live feed. Printed values keep the filing's rounding.
- Unsupported dividend-enactment queries refuse. The October 28 proposal remains pending as of October 21.

## License

[MIT](LICENSE). The license covers this project's code only. Third-party filings retain their own terms.

Part of [Rahil Bhavan's projects](https://github.com/RahilBhavan).
