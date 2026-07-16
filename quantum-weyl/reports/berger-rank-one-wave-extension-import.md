# Berger rank-one scalar-wave extension import

The quantum consumer pins classical commit
`34c184591956aafe97b0728f065b7d044b729f46` and independently replays the
support-local prolongation of the raw 10+2 endpoint by one scalar `y`.
The defining equation is `y-F2(h)=0`, while the modulus equation becomes
`R-Box_0 y=source_R`. Exact triangular shears verify

\[
E_{13}L_{13}U_{13}^{-1}=L_{12}\oplus I_1.
\]

Thus the apparent order-six Schur term is represented by an order-four
13-row system with an explicit scalar-wave channel.  The consumer also
replays the fixed-incidence obstruction: erasing the complete
metric-to-clock block while retaining `K12`, `Pghost`, and the
clock identity leaves the nonzero eight-entry defect
`Kclock(Pghost-I5)`.

This is tagged `LOCAL-ALGEBRAIC` and `LORENTZIAN-CAUSAL`, but it is not a Green
theorem. Advanced/retarded operators, the retained 26-row causal homotopy,
causal D-Cartan realization, Hadamard state, QME, and quantum theory remain
open.

Scoped verification:

```text
PYTHONPATH=quantum-weyl python -m lorentzian.rank_one_wave_extension_import_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_rank_one_wave_extension_import.py -v
```

The three exact and mutation-sensitive tests complete in 20.83 seconds. Tier
0 and the affected Tier 1/2 certificate chain were run. Tier 3 was not
required because the imported classical artifacts are content-addressed and
no Green, causal-homotopy, or quantum lifecycle state is promoted.
