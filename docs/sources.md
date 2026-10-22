# Source coverage and review

Purpose: bound the claims supported by the field layer. As-of review: 2026-10-21.

This tool reads a commit-pinned `strategy-8k-ledger` snapshot: 97 weekly 8-K observations through the October 19, 2026 filing, 432 program/action rows and 8 10-Q/10-K cover-page anchors filed October 31, 2024 through August 3, 2026. Quarterly/annual support is limited to cover-page share counts; financial statement tables are not mapped. It uses actual cached SEC HTML, no generated filing text. The ledger keeps original-byte hashes and deterministic normalized evidence lines; `python -m ledger hydrate` verifies all 184 cached resources.

Primary pages manually reopened October 21:

- [October 19 8-K](https://www.sec.gov/Archives/edgar/data/1050446/000119312526424688/mstr-20261019.htm): 848,517 BTC held as of October 18; 267 BTC bought in the October 12–18 period; MSTR ATM net proceeds $22M.
- [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1050446/000105044626000044/mstr-20260630.htm): cover reports 364,585,501 class A and 19,640,250 class B shares as of July 24, filed August 3. Sum: 384,225,751 basic shares.
- [Strategy dividend proposal FAQ](https://www.strategy.com/it/mstr/vote) and [October 16 SEC filing](https://www.sec.gov/Archives/edgar/data/1050446/000119312526423400/mstr-20261015.htm): the October 28 vote and conditional November daily dividends do not establish enactment as of October 21. The CLI refuses that unsupported intent.

Other historical rows are covered by the ledger's real-source parser/rebuild tests, not an assertion of manual browser review of every filing. Freshness is the frozen corpus, not a live feed. UTC retrieval dates can be October 22 while the local review date is October 21. No external model, account, paid API or embeddings are used.

Publication adds a portable bundle of the three query tables and 101 cited original-byte SEC HTML sources, with original manifest rows and hashes. It does not hydrate mutable SEC indexes. See [dependency](dependency.md) and [fixture provenance](../fixtures/README.md).
