# Berger localized detector-record contribution submission

The closed-universe observer team submits

`d_quotient_programme/contributions/classical-berger-localized-detector-records-preflight.json`

for integration into the next programme status refresh.  The contribution
references the immutable evidence commit `5b08869dd3fd74c95d63e2189029a6d47f377b79`
and certificate SHA-256
`09f723df60cd4e1bee3efa86f0c9319baee5f539ae2008d9d03230eb42398f23`.

This is a partial `LORENTZIAN-CAUSAL` contribution.  It registers local
standard-sign probe rods, two support-distinguished clock-labelled spacetime
smearings, exact central no-wrap incidences, and persistent probe memories.
It now also registers two predeclared conserved polarization currents and the
exact physical response `M=diag(C_00,C_11)` with both entries positive.  The
two causal memory records are therefore distinguishable.  The emitters remain
homogeneous over the compact `S3`; spatially localized emitter worldtubes,
raw-`D` descent with sources, rods, and memories, `K_Berger` compatibility,
backreaction, and a quantum observer algebra remain open.

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
