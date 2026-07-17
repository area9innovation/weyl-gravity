# Berger localized detector-record contribution submission

The closed-universe observer team submits

`d_quotient_programme/contributions/classical-berger-localized-detector-records-preflight.json`

for integration into the next programme status refresh.  The contribution
references the immutable evidence commit `9118807f69d8cfd8960abd2fece52e1bbd993b5a`
and certificate SHA-256
`a77eb1cd8abeee608ee02ce52a0a35f0fdb84531946ef78cc5e36145afc14b6d`.

This is a partial `LORENTZIAN-CAUSAL` contribution.  It registers local
standard-sign probe rods, two support-distinguished clock-labelled spacetime
smearings, exact central no-wrap incidences, and persistent probe memories.
It does not register a rank-two physical retarded transfer matrix, full
support-to-window incidence, raw-`D` descent with rods and memories,
`K_Berger` compatibility, backreaction, or a quantum observer algebra.

Verification:

```bash
python3 -m json.tool d_quotient_programme/contributions/classical-berger-localized-detector-records-preflight.json >/dev/null
python3 - <<'PY'
import json
import jsonschema

schema = json.load(open("d_quotient_programme/schema/team-contribution-v1.schema.json"))
payload = json.load(open("d_quotient_programme/contributions/classical-berger-localized-detector-records-preflight.json"))
jsonschema.Draft202012Validator(schema).validate(payload)
print("classical Berger detector-record contribution schema: PASS")
PY
```

The contribution is submitted but not yet folded into
`D_QUOTIENT_PROGRAMME_STATUS`; that integration belongs to the programme
status owner and must not change the fail-closed verdicts above.
