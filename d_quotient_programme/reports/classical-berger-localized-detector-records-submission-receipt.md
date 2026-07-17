# Berger localized detector-record contribution submission

The closed-universe observer team submits

`d_quotient_programme/contributions/classical-berger-localized-detector-records-preflight.json`

for integration into the next programme status refresh.  The contribution
references the immutable evidence commit `99e12bbb41f3dd83096c03889a6dfcaa653a237b`
and certificate SHA-256
`f18427cb14a8e377484a5b1e39d4481a1107a29a42923a5b78fc95ece9f8a429`.

This is a partial `LORENTZIAN-CAUSAL` contribution.  It registers two
localized clock-labelled probe record generators and the well-defined
source-to-record map.  It does not register two nonzero detector clicks,
raw-`D` descent with rods, `K_Berger` compatibility, backreaction, or a
quantum observer algebra.

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
