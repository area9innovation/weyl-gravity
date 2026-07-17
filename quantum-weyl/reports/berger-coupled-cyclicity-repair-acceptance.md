# Coupled Berger cyclicity-repair acceptance

The corrected coupled gravity--Maxwell (q_2) at classical commit
`e4f5c46fd7a04088e78e0374853b1f122ea223b1` is independently accepted. The
quantum-side consumer returns `ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR`, and the
classical mixed (q_3) input is unblocked.

For the accepted candidate, independent exact replay establishes:

- full 64-row (q_1q_2) defects: 0;
- full 64-row cyclicity defects: 0;
- transfer coefficients missing/extra/changed: 0/0/0;
- retained 36-row (q_1q_2) defects: 0;
- retained 36-row cyclicity defects: 0;
- full/retained coefficient counts: 1,890/1,474;
- causal unary flags preserved and producer cyclicity flags consistent.

The repair has the convention-derived form

\[
q_2^{\mathrm{repaired}}
=2q_{2,\mathrm{Maxwell\text{-}output}}+[q_1,F_2],
\qquad F_2:\ c_M\mapsto c_M-2\,\iota_cA,
\]

including its full BV-canonical cotangent lift. It is support-local rather
than fitted to the defect list.

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
true; and the producer's claim flags match those computations. The landed
candidate satisfies all of these conditions. This authorizes the repaired
classical cyclic mixed vertex and the next mixed (q_3) calculation. It does
not authorize residual quantum transfer, a QME statement, Lorentzian result,
or particle claim.

Dependency boundary: `LOCAL-ALGEBRAIC` classical-import acceptance only.

Tier-2 rerun on 2026-07-17: certificate replay passed in 4.64 seconds,
independent verification in 13.54 seconds, and five mutation/unit tests in
27.38 seconds. Strict Draft 2020-12 validation passed for the baseline input,
accepted input, and acceptance certificate in 1.20, 2.63, and 2.14 seconds.
Tier 3 was not run because no shared algebra engine, freeze, quantum lifecycle,
QME state, Lorentzian certification, or release boundary changed.
