# Relative off-shell changed-action BV-lift obstruction

## Result

The selected repair orbit is exactly the reduced quadratic-action
deformation,

```text
ACTION_CHANGED_EINSTEIN_Q_PRIMARY_REDUCED_THEORY
```

with no changed-pairing or physical-auxiliary repair mixed into it.  Since a
single real parity-even covariant action controls both parity sectors, its
axial and polar target shifts are tested together.

Within the complete real parity-even local Diff x U(1) Einstein--Maxwell
action quotient through four derivatives, the requested rank-one repair has
no action preimage.  The result is

```text
OBSTRUCTED_COMPLETE_PARITY_EVEN_FOUR_DERIVATIVE_LOCAL_ACTION_ANSATZ
```

and carries `LOCAL-ALGEBRAIC` and `REDUCED-MODE` only.

## Complete bounded ansatz

Before quotienting, the four-derivative action space contains

```text
Riem2 Ricci2 R2 nablaF2 divF2 RF2 RicciFF RiemFF F2sq P2
```

The Euler relation, integrated Maxwell Weitzenboeck relation, one bounded
connection redefinition, and four bounded metric redefinitions have exact
relation rank seven.  The four-derivative quotient is therefore represented
by

\[
 R_{abcd}F^{ab}F^{cd},\qquad (F^2)^2,\qquad (F{}^\star F)^2.
\]

Together with the lower-derivative densities \(1,R,F^2\), this is the complete
six-direction action basis at the declared bound.  The two exact
same-background incidence rows are retained; they can only shrink the action
response image.

## First invariant obstruction

For a general action in this quotient, the axial \((2,2)\) response is

\[
 -8(c_F+4c_{F^4}-8c_{P^2}),
\]

so the coefficient of \(\lambda\) is identically zero.  The requested
source-action shift is

\[
 \Delta_A=\begin{pmatrix}0&0\\0&-9\lambda\end{pmatrix},
\]

whose same coefficient is \(-9\).  This exact dual functional already proves
that the unrestricted action-response coefficient system is empty.

The polar control is independent: every action response has zero
\(\lambda^2\) coefficient in its \((2,2)\) entry, whereas the requested

\[
 \Delta_P=\operatorname{diag}\!\left(0,
 -\frac34(\lambda-2)(3\lambda+2)\right)
\]

has coefficient \(-9/4\).  In addition, the exact coefficientwise system
requiring zero q-to-p Hessian cross response is a \(17\times6\) matrix of rank
six.  Its kernel is zero: no nonzero action deformation in the complete
bounded quotient preserves the declared p-shell separation.

## BV and quantum disposition

Every ansatz density has the ordinary conditional Diff x U(1) Noether
completion on its own stationary background.  That general construction has
38 rows: five ghosts, fourteen fields, fourteen Euler rows and five identity
rows.  It does not produce the requested changed theory because the target
Hessian is outside the action-response image.

Consequently the following gates are not activated:

- the requested changed local/master action and BV differential;
- its odd pairing, nonminimal sector and gauge-fixed operator;
- the requested full 40-to-38 cyclic chain lift;
- a common source/target density, measure, domain and regulator;
- changed-theory local cohomology, relative anomaly coefficients and the
  relative one-loop QME.

The strict pure-Weyl coefficient vector is not imported as a relative vector.
Paper 12's lifecycle disposition is therefore a scoped obstruction of this
four-derivative changed-action route, while the relative QME remains
undefined.  No Paper 12 theorem is promoted by this result alone.

## Independent evidence

The upstream independent rail constructs all six covariant densities directly
in an exact compact-product tensor Taylor algebra, polarizes their second
variations, substitutes independent axial and polar harmonics, and integrates
after \(z=\cos\theta\).  It imports no producer response matrices and replays
the q/p tables at \(\lambda=6,12,20,30\).

The quantum-side independent verifier separately recomputes the relation
rank, both polynomial cokernel functionals, and the \(17\times6\) rank from
the pinned artifacts.  Mutations that change repair orbit, cross the axial
rank-one wall, construct a nonexistent BV lift, or promote an anomaly/QME are
rejected.

## Boundary and open routes

This does not rule out six-or-more-derivative local actions, nonlocal actions,
the distinct changed-pairing orbit, or a theory with new physical auxiliary
fields.  It supplies no anomaly coefficient, QME restoration, Lorentzian
causal construction, Hadamard state, positivity, particle, scattering or
unitarity result.

Evidence:

- `quantum-weyl/relative/certificates/RELATIVE_OFFSHELL_CHANGED_ACTION_BV_LIFT_OBSTRUCTION_V1.json`
- `residual_atlas/relative-offshell-changed-action-bv-lift-obstruction-fragment-v1.json`
