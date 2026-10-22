# Publication receipt

Purpose: record the reviewed GitHub publication and reproducibility evidence.

Status: reviewed source published; clean GitHub clone and implementation CI verified.
Persistent goal: creation confirmed by `create_goal` in this project thread; final status is recorded in the thread.
Starting commit: `897667f` on `main`; original history retained.
Repository: https://github.com/RahilBhavan/strategy-ask-filings (public).
Authenticated owner: `RahilBhavan`; origin set to this new repository.
About text and five topics match the deterministic CLI scope.

## Publication audit

Tracked files and every reachable historical blob were inspected before push.
The initial reachable history contained 22 blobs and no credential-pattern
matches or blobs above 5 MB. No databases, caches, private hub files, node
keys, account records or untracked workspace material are included. Existing
author metadata is retained. The new 3.46 MB frozen archive contains public
SEC corporate filings only, with provenance and original retrieval manifest;
its 105 entries expand to 53,330,238 bytes. A scan of every expanded entry
found no private-key or credential-token pattern. Public issuer contacts in
SEC filings are source material, not private workspace contacts.

No license was selected. No web deployment, account actions, messages to third
parties, scheduled tasks or market transactions were performed. Coordination
with the ledger owner and one independent T3 reviewer was authorized.

## Final verification

Published implementation commit: `f3958ef86908df9ece82f0512936a840b8f97647`.
Default branch: `main`; GitHub branch SHA matched the intended local source
commit. Reviewed ledger pin:
`94c70044aaf14eea2ffb53deffd1a1f36bdec52e`, public and confirmed by its owner.
The receipt and Node 24 action-pin update follow the source commit without
rewriting its history. The final branch SHA is available in Git and the thread.

Fresh clones of both repositories were obtained from GitHub under
`~/scratch/strategy-ask-filings/`. Setup downloaded no SEC data and restored all
101 original documents after archive, manifest and table verification. Repeating
setup with `--offline` succeeded. The following passed in the published clone:

```bash
python scripts/setup_ledger.py --ledger <scratch-ledger>
python scripts/setup_ledger.py --ledger <scratch-ledger> --offline
ASK_FILINGS_LEDGER=<scratch-ledger> PYTHONPATH=tests/offline_guard python -m unittest discover -s tests -v
python -m compileall -q ask_filings scripts tests
```

Observed **23 tests passed** on local Python 3.14.7. `--fields` exported all nine
intents. Holdings and share commands matched `examples/holdings.json` and
`examples/shares.json` byte for byte; STRC capacity returned 17,510,800,000 USD.
Cutoff holdings and absent denominator commands returned `unavailable`, exit 2;
dividend enactment returned `refused`, exit 2. All relative documentation links
resolved and the published clone stayed clean.

[Implementation CI run](https://github.com/RahilBhavan/strategy-ask-filings/actions/runs/39718779988)
passed on Python **3.11.14** and **3.14.0** with connections blocked during tests,
including CLI subprocesses. Its deprecated action runtimes were replaced with
full-SHA Node 24 action pins; the final run is checked separately before goal
completion. CI has read-only repository permissions and no schedule or paid
service. There is no configured static type checker for this Python v1.

Proven repairs: edited normalized tables and edited source manifests now refuse;
missing source cache cannot trigger a network fetch; the reviewed upstream pin
retains denominator date headers. Tamper, duplicate, zero, restore/retry and
symlink negative cases pass. Financial values and source bytes are unchanged.

Limits: nine deterministic intents; frozen October 21, 2026 corpus; section
locators rather than per-cell attestation; no current share denominator; no
LLM, live-feed, amendment-resolution, financial-accuracy certification or
security-certification claim. The October 28 proposal remains pending at the
snapshot. No license file yet. Verification scratch clones are disposable;
run setup to restore the default dependency after cleanup.
