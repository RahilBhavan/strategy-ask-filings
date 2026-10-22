# Ask filings v1 scope and acceptance

Agreed 2026-10-21. Local deterministic natural-language CLI; no LLM, model or network service. Public source publication authorized after v1; the deterministic scope remains unchanged.

- Provide documented semantic fields over weekly 8-K economic data and 10-Q/10-K cover-page share counts from the pinned ledger snapshot.
- Support a small explicit grammar for holdings, purchases, USD reserve/cash, issuance/capacity, and basic shares, with date/ticker filters and a filing-date cutoff.
- Return exact values, units, period/as-of dates, accession, URL, SHA-256 and numbered normalized source blocks/rows. Derived values name their formula; ambiguous, unsupported, missing and future-only data produce refusal/uncertainty, never guessed prose.
- Export a human-readable semantic field catalog. Prove answers against real source rows, date cutoff, unsupported query refusal, malicious/unknown text, missing fields, invalid dates and reproducibility.

Scope is structured facts, not unrestricted document QA or a full financial-statement parser. Dividend enactment is unsupported; Oct 28 proposal is not enacted as of Oct 21.
