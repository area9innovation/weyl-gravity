# Coupled Berger cyclicity-repair acceptance

The corrected coupled gravity--Maxwell (q_2) has not yet been supplied.
This rail is therefore `INPUT_BLOCKED`, not a repair verdict. It is ready to
consume one committed classical candidate by content hash and return one of
two outcomes: exact acceptance or an exact rejection diagnostic.

The real negative-control fixture is classical commit
`744383f2a21a05a1464f3a25b6569e2b001b4f20`. Independent replay establishes:

- full 64-row (q_1q_2) defects: 0;
- full 64-row cyclicity defects: 1,234;
- transfer coefficients missing/extra/changed: 0/0/0;
- retained 36-row (q_1q_2) defects: 0;
- retained 36-row cyclicity defects: 953.

Thus exact transfer and (L_\infty) arity-two closure do not imply cyclicity.
The defect atlas further splits the retained obstruction into 800 physical
metric--potential--potential terms, 138 ghost/potential-antifield terms, and
15 Maxwell ghost-density terms. Uniformly doubling Maxwell-output (q_2)
coefficients removes the first 938 while preserving (q_1q_2), but it is not
a complete repair because the final 15 remain.

A candidate passes only if strict Draft 2020-12 validation and hashes pass;
both full and retained (q_1q_2) and cyclicity defects vanish; the transferred
payload equals a fresh coefficientwise transfer; causal unary flags remain
true; and the producer's claim flags match those computations. Until then no
cyclic mixed vertex, gravitational dressing, mixed (q_3), residual quantum
transfer, QME statement, Lorentzian result, or particle claim is authorized.

Dependency boundary: `LOCAL-ALGEBRAIC` classical-import acceptance only.
