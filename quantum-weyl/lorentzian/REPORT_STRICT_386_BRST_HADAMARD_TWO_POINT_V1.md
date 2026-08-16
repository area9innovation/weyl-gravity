# Strict 386-row BRST Hadamard two-point function

**Result:** `STRICT_386_BRST_HADAMARD_TWO_POINT_V1`

**Lifecycle:** `LORENTZIAN_CERTIFIED`

**Hadamard snapshot:** `5fea44144688a1ea13e82cb1d730731fd4ba396e35cb2ae2e9d1ec653a60af22`
**Classical snapshot:** `STRICT_PURE_WEYL_BV_SNAPSHOT_07dc7271b95b263a`

## Result

A BRST-compatible Hadamard two-point pair is now constructed on the complete
386-row strict pure-Weyl off-shell BV complex.  This is not a pullback of the
existing reduced E/A/L state and imports no Berger data.

The construction starts from the same rank-15 adjoint-tractor Hodge wave used
for the causal homotopy.  Whole S³ eigenspace projectors define the nonzero-mode
Hadamard pair

```text
w_plus(lambda)  = -exp(-i sqrt(lambda) (t-t'))/(2 sqrt(lambda))
w_minus(lambda) = -exp(+i sqrt(lambda) (t-t'))/(2 sqrt(lambda)).
```

Their difference is `i sin(sqrt(lambda)(t-t'))/sqrt(lambda)`, exactly `i`
times the repository retarded-minus-advanced kernel.  The scalar zero mode is
retained with `w_0^plus=+i(t-t')/2` and `w_0^minus=-i(t-t')/2`.  It is an exact,
smooth, stationary bisolution and supplies the missing zero-mode commutator
without deleting the mode or introducing a scale.

Applying `W_parent` turns the wave pair into a BRST chain two-point pair.  The
certified cyclic BGG maps, trace/Weyl shear and graph retract then transport it
to all 386 rows.  The algebraic retract summand has zero causal difference and
therefore receives the explicit zero two-point value.  That is full typed
coverage, not an omitted sector.

## What is certified

All eleven distributional obligations pass: left and right bisolution,
graded CCR, Hadamard wavefront relation, both BRST Ward identities, graded
Hermiticity and reality, cylinder-flow stationarity, retained zero-mode policy,
declared positivity/Krein policy, and complete row coverage.  The microlocal
statement is

```text
WF'(lambda_sign) = (N_sign x N_sign) intersect WF'(Delta_Lambda).
```

The finite-order transport maps do not enlarge wavefront sets, and the two
frequency cones are disjoint, so any polarization removed by the graph maps is
removed from the causal kernel as well.

## Positivity boundary

This is a Hadamard **two-point function**, not a positive Hadamard state.  That
distinction is standard in the BRST literature: positivity is an additional
condition.  The selected scale-free zero-mode split has vanishing symmetric
part, and the parent normalization is indefinite.  The certificate therefore
calls the result a graded Hadamard pseudo-state pair and keeps physical
positivity false.

No renormalized time-ordered products, Feynman propagator, Lorentzian QME,
residual quantum transfer, particle interpretation or interacting quantum
theory follows from this free two-point construction.

## Reproduction

```text
python3 quantum-weyl/lorentzian/build_strict_386_brst_hadamard_two_point.py --check
python3 quantum-weyl/lorentzian/check_strict_386_brst_hadamard_two_point.py
python3 quantum-weyl/lorentzian/verify_strict_386_brst_hadamard_two_point.py
python3 -m unittest quantum-weyl.lorentzian.tests.test_strict_386_brst_hadamard_two_point
```
