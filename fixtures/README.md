# Frozen ledger v1 source contract

Purpose: make every supported answer reproducible without SEC access.

`ledger-lock.json` pins the reviewed public ledger code commit, v1 schema,
three exact CSV hashes, the source manifest hash and the SHA-256 of `frozen-ledger.zip`. The archive
contains all 97 weekly observations, 432 instrument/action rows, 8 cover-page
anchors and the 101 original SEC HTML documents referenced by those tables.
It includes the corresponding original retrieval manifest rows. It does not
contain the ledger's submissions index or unrelated exhibits.

The snapshot is as of October 21, 2026; weekly coverage ends with the October
19 filing. Economic dates, filing dates and UTC fetch dates are distinct.
UTC fetch times can be October 22 during October 21 in America/Detroit.
The archive retains the original bytes, URL, retrieval time, size and hash;
setup verifies all source hashes before extraction. Each answer verifies its
table hash and the ledger verifies the cited source hash before normalization.
Hashes ensure consistency with this repository's snapshot, not authenticity
independent of the cited SEC sources or a security certification.

Source: SEC EDGAR, Strategy CIK 1050446. These are public corporate filings,
not account or identity records from a private workspace. Third-party filing
text remains attributed to its issuer and SEC location; no license over that
material is claimed. See [source review](../docs/sources.md).

The archive is generated data, not manually authored source. Do not edit it
in place. A deliberate snapshot update requires review of upstream code,
tables and source provenance, a new pin and hashes, and passing regressions.
`--ledger` runs trusted local Python code from that checkout. Never point it
at an untrusted directory. Updated ledger tables outside this frozen snapshot
are refused until their hashes have been reviewed here.
