# Universal Hessian and axial factor-intertwiner structure

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact certificate establishes that, modulo the four-dimensional Euler
boundary/corner variation, the pure-Weyl Hessian about an arbitrary
Ricci-flat background is

\[
4\alpha\int\sqrt{-g}\left(
\delta R_{1,ab}\delta R_2^{ab}
-\frac13\delta R_1\delta R_2\right).
\]

Thus the Einstein kernel is the radical of the bulk Hessian.  A separate
two-dimensional Gram calculation proves that every nondegenerate
Einstein-containing restriction of the inherited form is indefinite; a
semidefinite restriction retaining that null line is necessarily
degenerate.

For the Schwarzschild axial `ell=2` factors, an independent symbolic
elimination reduces any rational differential intertwiner to
`P=a(r)D+b(r)` and derives the same fourth-order compatibility equation in
both spin directions.  Its local exponents, ordinary-point regularity and
infinity balance reduce every rational solution to `a=A+B/r`; exact
substitution forces `A=B=0` for every real `omega>0`, after which `b=0`.
The spin-one quotient and spin-two factor are therefore not related by a
rational local Darboux map.

Combined with the imported nonzero rational projective extension class, a
branch-resolving rational involution would solve the forbidden splitting
equation.  This rules out that local rational architecture, not a nonlocal
Mannheim operator or a quantum positive-metric construction.

Verification:

```text
python3 black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/produce.py
python3 black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/verify.py
python3 -m unittest -v black_hole_programme.phase4.axial_universal_hessian_intertwiner_v1.test_structure
```

`does_not_establish`: an Euler-free literal endpoint current, absence of
nonlocal intertwiners, a BRST physical-state theorem, quantum positivity,
unitarity, or a complete asymptotically flat phase space.

CLOSE-OUT: DONE — the exact action, positivity, rational-intertwiner and
local-\(C\) obstruction claims are independently certified with fail-closed
boundaries.
EVIDENCE: black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/certificate.json
