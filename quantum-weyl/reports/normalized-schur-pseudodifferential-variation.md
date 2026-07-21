# Normalized Schur pseudodifferential variation

Date: 2026-07-21

Science Forge item:
`sf:program/work/quantum-normalized-schur-pseudodifferential-variation`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Exact fixed-domain result

Let

\[
A(t)=F+tW,\qquad G=F^{-1},\qquad
S_L(t)=\frac23I+\frac13\delta A(t)^{-1}d
\]

on one fixed primed complement on which every operator has the same domain.
The noncommutative resolvent identity gives

\[
A(t)^{-1}=G-tGWG+t^2GWGWG-t^3GWGWGWG+O(t^4).
\]

Consequently,

\[
\begin{aligned}
S_L'(0)&=-\frac13\delta GWGd,\\
S_L''(0)&=\frac23\delta GWGWGd,\\
S_L'''(0)&=-2\delta GWGWGWGd.
\end{aligned}
\]

No commuting reorder has been used. An exact noncommuting finite fixture
reconstructs these derivatives directly from the rational matrix inverse and
rejects a reordered first word.

Using the Ward identities

\[
\delta G=\Delta_0^{-1}\delta,
\qquad Gd=d\Delta_0^{-1},
\]

the first variation is

\[
-\frac13\Delta_0^{-1}\delta Wd\,\Delta_0^{-1}.
\]

The two scalar inverses are essential.

## Symbol hierarchy

For Laplace-type (F\in\mathrm{Diff}^2), its parametrix satisfies
(G\in\Psi^{-2}). The three Taylor coefficients therefore lie in

\[
\Psi^{-2},\qquad\Psi^{-4},\qquad\Psi^{-6},
\]

with subprincipal orders (-3,-5,-7). Their leading scalar symbols are

\[
-\frac13\frac{\langle\xi,W\xi\rangle}{|\xi|^4},\qquad
+\frac13\frac{\langle\xi,W^2\xi\rangle}{|\xi|^6},\qquad
-\frac13\frac{\langle\xi,W^3\xi\rangle}{|\xi|^8}.
\]

The subprincipal coefficients require the subprincipal symbol of (F), the
connection parts of (d,\delta), and covariant derivatives of (W). The
manifest deliberately supplies their orders and required inputs, not guessed
coefficients absent a typed covariant symbol calculus.

This polyhomogeneous symbol data is local. It does not determine smoothing
traces, spectral cuts, zero-mode measures, or the finite global determinant.

## Priming and projector derivatives

The displayed resolvent series is unconditional only when a fixed orthogonal
projector (P) defines a common complement, commutes with (A(t)), and
(A(t)|_{\operatorname{Ran}(1-P)}) stays invertible. Then

\[
R'=-RWR.
\]

For a smooth moving kernel projector,

\[
R'=-RA'R-P'R-RP',
\qquad
P'=-RA'P-PA'R
\]

in the self-adjoint constant-rank case. A separate rotating-projector fixture
has a vanishing naive term but nonzero (R'), so freezing (P) is rejected.
At a rank-changing crossing there is no differentiable reduced resolvent
without an explicit stratum or contour choice.

For the scalar-flat Berger family at (t=0), the (F)-kernel is locally
fixed, coclosed, orthogonal to gradients, and annihilated by (W). Thus the
fixed-complement formula applies locally at the expansion point. It is not a
claim across the separately catalogued finite-(t) crossings.

## Berger and mutation controls

For the (n=0,j=1/2) block,

\[
\Delta_0=\frac9{16},\qquad \delta Wd=\frac34.
\]

The correct derivative is

\[
-\frac13\frac{3/4}{(9/16)^2}=-\frac{64}{81},
\]

while the forbidden one-inverse surrogate gives (4/9). The independent
rail rejects the wrong sign, commuting reorder, one-inverse word, frozen
moving projector, altered Berger value, global-determinant promotion and
QME/Lorentzian promotion.

## Boundary and next gate

This result provides the exact local operator words requested by the accepted
pseudodifferential/heat-kernel Forge request. It does not compute a
Seeley--DeWitt coefficient, Wodzicki residue, finite determinant, spectral
tail, anomaly coefficient, QME restoration, Lorentzian Green operator,
Hadamard state, particle space or unitarity result.

The next gate is independent consumption of the manifest by the typed
pseudodifferential/heat-kernel layer, together with the separate Berger
high-mode domain theorem.

## Verification

```text
python3 quantum-weyl/spectral/euclidean/normalized_schur_pseudodifferential_variation.py --check
python3 quantum-weyl/spectral/euclidean/verify_normalized_schur_pseudodifferential_variation.py
python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_normalized_schur_pseudodifferential_variation.py -v
```

EVIDENCE: `quantum-weyl/spectral/euclidean/certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json`; `quantum-weyl/spectral/euclidean/generated/normalized_schur_pseudodifferential_variation_v1/operator_words.json`

CLOSE-OUT: DONE — the exact fixed-domain variations, symbol orders, projector boundary, Berger replay and negative controls required by the stop condition are certified.
