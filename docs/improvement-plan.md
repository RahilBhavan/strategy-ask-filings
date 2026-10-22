# Checked deterministic question benchmark

Scope accepted October 22, 2026: improve evaluation of the existing nine-intent
CLI without changing the pinned ledger or bundled public documents. There is no
project glossary or ADR directory; `docs/spec.md`, `docs/method.md` and
`docs/dependency.md` define the vocabulary and decisions.

Done conditions:

1. Version a developer-authored question set covering canonical questions and
   paraphrases for every intent, exact dates, filing cutoffs, stale snapshot
   boundaries, missing fields/denominators, unsupported and hostile questions.
2. Check exact answer values, units, dates, program identity, formulas, citation
   accession/URL/hash and normalized source-section fingerprints against fixed
   expectations. Re-hash cited local bytes; never update expectations at runtime.
3. Report pass/fail counts by intent and boundary category, plus named failing
   cases and mismatch paths. Exit nonzero for any mismatch; prove this with
   deliberate wrong-value and wrong-hash expectations.
4. Fix reproducible parsing/answer/refusal defects exposed by the set; preserve
   full-match refusal, exact-date semantics and all existing tests.
5. Run offline baseline/new tests and compilation, document a five-minute replay
   and measured scope/limits, commit and push scoped changes, inspect CI.

Non-goals: LLMs, general retrieval, genuine user-testing claims, live filing
completeness, ledger/schema migrations, paid sources, UI, license changes.
