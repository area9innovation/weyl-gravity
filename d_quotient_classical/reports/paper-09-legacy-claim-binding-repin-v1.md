# Paper 9 legacy ten-claim source-binding repin

Disposition: `REPIN_CURRENT_PUBLICATION_SOURCES`.

The deterministic classical producer differed from its persisted certificate
only in the hashes of the publication-current main paper and computational
supplement.  All ten `P09-C1`--`P09-C10` rows, their wording and sections,
certificate identities and hashes, required true/false fields, two independent
cross-checks, two team signoffs, exclusions and claim boundary were unchanged.

The source binding moved from:

```text
main       817771965e1f32120743214a87124cc3e70ea2f46cc136a6caeada21e333f919
supplement c18235ff2e41372949e2d63a7f3ec30a7ae0df497b92e4eb9a540656e7b997ce
```

to:

```text
main       5124f7b093cae6b0b84be981e621fc231c6d37427997af92d0c108f9751dcf8b
supplement ec2533c734b15a9d650679793388a9f791aa7dd78d8e6c5f34db241a0e19c6dd
```

The certificate now hash-imports the `DRAFT_ALLOWED` report, the current
22-claim map `PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1`, and its
tier receipt.  It verifies that the superset begins with the same ten legacy
claim identities.  Mutations using an old paper hash, dropping a legacy
claim, widening a claim scope, or silently changing a certificate hash are
all rejected.

The 22-claim map still pins the pre-repin legacy certificate by design.  Its
independent verifier now stops at exactly that hash, so the final Paper 9
owner must regenerate the superset import after this commit.  This is an
explicit downstream evidence handoff, not a pass and not a scientific defect.
Paper 9 itself was not edited.

EVIDENCE: d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json and d_quotient_classical/receipts/PAPER_09_LEGACY_CLAIM_BINDING_REPIN_V1_TIER_RECEIPT.json

CLOSE-OUT: DONE — the legacy ten-claim source-binding gate is reproducibly repinned with no scientific claim change; the final publication owner must regenerate the 22-claim map import.
