# Field-theoretic BV identification

This package addresses the remaining classical claim boundary in
`paper/conformal-residual-cohomology.tex`: whether the certified algebraic
metric-BV model is the complete gauge-fixed strict-pure-Weyl BV complex in
the selected finite-energy cylinder window.

The work is intentionally staged.  The first completed milestone starts
from the quadratic minimal master action and proves an exact chain
isomorphism

```text
minimal BV tangent chain  <---->  raw G -> M -> E -> I chain
```

in the complete centered energy buffer.  It keeps both conventional BV
ghost number and the suspended local tangent degree explicit.  The maps use

```text
Omega    = omega + (partial.c)/4
tau      = tr(h)/8
tau_star = 2 tr(h_star)
i_star   = -(c_star + partial(omega_star)/4)/2
```

and obey `F Q_BV = Q_raw F`, `G Q_raw = Q_BV G`, and `FG=GF=1` with exact
rational matrices.  An explicit projector and homotopy additionally prove
`Q_raw s_tr + s_tr Q_raw = P_tr`, so the raw object is the direct sum of the
trace-free detour chain and two trace/Weyl contractible pairs.  On the
inhomogeneous low-mode block the same transformation proves
`T(ker K_BV)=ker K_raw=so(4,2)`.  The generated TSV contains one row for
every raw basis vector at energies 2--5.

Run:

```bash
python3 symbolic/verify_conformal_field_bv_dictionary.py --emit
```

Outputs:

- `certificates/minimal_bv_chain.json`
- `certificates/minimal_bv_dictionary.tsv`
- `generated_latex/minimal_bv_dictionary.tex`

This milestone does **not** yet prove the full field-domain theorem.  The
remaining phases are:

1. derive a concrete gauge-fixed/nonminimal extension and contract every
   removed field explicitly;
2. split and replace the fifteen local conformal-Killing ghost modes and
   their genuine dual sector without double counting;
3. inventory every local BV row capable of entering or leaving the centered
   spectral-sequence term;
4. compare the field residual action, HPL transfer, and cyclic BV/BFV
   pairing with the already certified raw operators;
5. rerun the residual cohomology from the field variables.

Analytic completions, interactions, anomalies, and quantum nilpotency are
out of scope.
