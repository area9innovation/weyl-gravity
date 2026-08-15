# BT one-site fiber single-well gate

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_FIBER_SINGLE_WELL_GATE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

Every one-site conditional fiber of the residual-square BT action on the
four-dimensional nearest-neighbor lattice has exactly one critical point, and
that point is its global minimum.  The curvature at the minimum is strictly
greater than (13) in the log-field coordinate.  This is uniform in the
frozen background and the lattice volume.

The fibers are nevertheless not globally convex.  An exact field on the
periodic (4^4) lattice has one-site curvature (-57) at a declared point.
Thus the result is genuinely single-well rather than a hidden convexity
theorem.

This is useful because it removes one possible source of the Witten barrier:
an individual lattice site cannot develop two conditionally competing wells.
It also tells us exactly why standard convex local-to-global criteria cannot
yet be imported.  The next question is whether these nonconvex but single-well
one-dimensional laws have a background-uniform Poincare constant.

## Exact one-site reduction

On a (q)-regular graph write

\[
 A(\psi)=\frac12\sum_v r_v(\psi)^2,
 \qquad
 r_v=\sum_{w\sim v}e^{\psi_w-\psi_v}-q.
\]

Fix all variables except (psi_o), and add (z) at the site (o).  For its
neighbors (i), put

\[
 B_i=e^{\psi_o-\psi_i},\qquad
 A_0=\sum_iB_i^{-1},\qquad
 d_i=\sum_{w\sim i,\,w\ne o}e^{\psi_w-\psi_i}-q.
\]

The part of the action which depends on (z) is exactly

\[
 F(z)=\frac12(A_0e^{-z}-q)^2
      +\frac12\sum_i(B_ie^z+d_i)^2+\text{constant}.
\]

Notice that (d_i>-q).  With

\[
 C_2=\sum_iB_i^2,\qquad C_1=\sum_iB_id_i,
 \qquad x=e^z,
\]

the critical-point equation becomes

\[
 x^2F'(z)=P(x)
 =C_2x^4+C_1x^3+qA_0x-A_0^2.
\]

## Why there is exactly one minimum

At any positive stationary point of the polynomial (P), eliminating (C_1)
with (P'(x)=0) gives

\[
 P(x)=-\frac13
 \left(C_2x^4-2qA_0x+3A_0^2\right).
\]

The bracket has its minimum at
(x_0^3=qA_0/(2C_2)), where it equals

\[
 3A_0\left(A_0-\frac q2x_0\right).
\]

Cauchy--Schwarz gives the parameter constraint

\[
 A_0^2C_2
 =\left(\sum_iB_i^{-1}\right)^2\sum_iB_i^2
 \ge q^3.
\]

For (q<16), this implies (x_0<2A_0/q).  Therefore every positive
stationary value of (P) is strictly negative.  Since (P(0)=-A_0^2<0) and
(P(x)	o+infty), the polynomial crosses zero exactly once.  The fiber
energy diverges at both ends, so this crossing is the unique global minimum.
The BT lattice has (q=8), safely inside the theorem.

At the root, a second elimination gives

\[
 F''=C_2x^2+\frac{3A_0^2}{x^2}-\frac{2qA_0}{x}.
\]

Writing (y=A_0/x) and
(K=A_0\sqrt{C_2}\ge q^{3/2}), elementary completion yields

\[
 F''\ge 2K-\frac{q^2}{2}.
\]

For (q=8), this is (32\sqrt2-32>13).  The last comparison is exact:
(2\cdot32^2>45^2).

## Exact nonconvex fixture

On the periodic (4^4) lattice, set the central log field to zero, its eight
neighbors to (-\log2), and every other site to (-5\log2), modulo an
irrelevant common shift.  Along the central-site coordinate,

\[
 A_0=4,\qquad C_2=32,\qquad C_1=-121,
\]

so

\[
 P(x)=32x^4-121x^3+32x-16.
\]

Direct site enumeration gives

\[
 F''(0)=-57.
\]

Nevertheless (P(3)=-595<0<P(4)=560), and the theorem proves that this is
the only root.  Thus the minimum lies between (log3) and (log4): the
fiber bends the wrong way at the displayed point but does not split into two
wells.

## Literature boundary

[Thoma's membrane-model theorem](https://arxiv.org/abs/2112.07584) uses a
uniformly convex single-site potential in the Laplacian field.  The exact
(-57) fixture violates that hypothesis.

[Menz and Otto's two-scale theorem](https://arxiv.org/abs/1307.2338) concerns
a noninteracting conservative spin system whose single-site potential is a
bounded perturbation of a strictly convex potential.  The present result does
not produce such a decomposition for the many-body BT residual-square action.

[Hilger's nonconvex gradient-model analysis](https://arxiv.org/abs/2007.10869)
controls a nonconvex perturbation of a quadratic gradient model by
renormalization-group methods.  No smallness or structural identification with
that class has been proved for BT.  These papers therefore guide the operator
and multiscale strategy but are not imported as BT theorems.

## Meaning and next calculation

In ordinary language, freezing every lattice variable except one always
leaves a bowl with one bottom.  The bowl can have an inward dent, so convexity
methods still fail, but it never develops two bottoms separated by a local
barrier.

The precise next calculation is one-dimensional: apply a
Muckenhoupt/Hardy criterion to the exact exponential-quartic density
(e^{-F(z)/\lambda^2}dz), and determine whether its Poincare constant is
uniform in (A_0,C_1,C_2) under the BT constraints.  A proof would provide the
local gap needed before an inter-site influence or multiscale argument.  A
counterfamily would produce the first genuine local low-gap obstruction.

## Boundary

This certificate does not establish a uniform one-site Poincare inequality,
an inter-site influence bound, global Witten coercivity, the normalized
lowest-mode or interacting (H^{-1}) estimate, tightness, or an interacting
continuum measure.  It does not restore ordinary OS positivity at
(lambda=0.4), and has no Born, Krein, or `LORENTZIAN-CAUSAL` consequence.

Paper 21 is not edited at this checkpoint because the interacting-moment and
reconstruction lifecycle states do not change.  The certificate and report
are the publication surface for this scoped local theorem.

## Reproducibility receipt

Run the exact scoped rails under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_single_site_fiber_single_well_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_single_site_fiber_single_well_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_single_site_fiber_single_well_gate
```

Tier 0 also compiles the changed Python, parses and validates the JSON/schema,
checks the two predecessor hashes, runs the scoped diff check, and inspects the
exact staged paths.  Tier 2 uses the unchanged content-addressed predecessors
by hash.  Tier 3 is not triggered: this is a classified local theorem and
method obstruction, not a freeze, reconstruction theorem, shared-core change,
or release.

Measured command times, peak memory, and the append-only planning-import
receipt are recorded in the generated certificate.  A skipped Science Forge
shadow audit is explicitly not counted as a pass.
