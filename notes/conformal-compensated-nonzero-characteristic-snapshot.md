# Compensated nonzero-characteristic BV snapshot

## Scoped theorem

The compensated flat minimal BV operator is now exported entry by entry in a
canonical sparse JSON format.  A separate consumer reconstructs those entries
without importing either the constructor or exporter and proves exactly

\[
q^2=0,
\qquad
q(-p)^T\Omega+\Omega q(p)=0,
\]

the Hessian/gauge/Noether block identities, and the Weyl-doublet contraction.
The characteristic calculation consumes only that independently checked
export.

At `c1=alpha=-1`, `v=1`, the exact finite symbol fibers are:

| Representative covector | \((\mathrm{rk}R,\mathrm{rk}H,\mathrm{rk}N)\) | \(H^{-1},H^0,H^1,H^2\) |
|---|---:|---:|
| generic `p=(2,1,0,0)` | `(5,6,5)` | `(0,0,0,0)` |
| nonzero null `p=(1,0,0,1)` | `(5,4,5)` | `(0,2,2,0)` |
| second root `p=(0,1,0,0)` | `(5,1,5)` | `(0,5,5,0)` |
| zero `p=0` | `(1,0,1)` | `(4,10,10,4)` |

For each promoted nonzero branch the certificate contains actual sparse
matrices for cohomology inclusion (i), homological projection
\(\pi_{cl}\), and homotopy (s), satisfying

\[
\pi_{cl}i=1,
\qquad
i\pi_{cl}=1-qs-sq,
\qquad
s^2=si=\pi_{cl}s=0.
\]

Because formal adjunction reverses momentum, the induced odd BV pairing is
not (i_p^T\Omega i_p).  It is

\[
\Omega_H(p)=i_{-p}^{T}\Omega i_p.
\]

This pairing has full rank four on the null cohomology and full rank ten on
the second-root cohomology.

## Where the graviton is

Before any final residual quotient, the nonzero null symbol fiber contains
exactly two degree-zero classes.  For the representative wave covector along
the (z) direction, the certified real basis is equivalent to

\[
h_{12},
\qquad
h_{22}-h_{11}.
\]

Their complex combinations are the usual helicity-(\pm2) polarizations.
The two degree-one classes are their BV-dual equation/antifield classes.

This answers “where did the graviton go?” at the local symbol level: it is
present before the global residual quotient.  Its disappearance from the
absolute one-particle residual cohomology on the closed cylinder is a
different statement.  There the programme additionally quotients by the
residual `SO(4,2)` action on a compact global state problem.  It does not say
that the local null characteristic complex is empty, nor that asymptotically
flat radiative states vanish when boundary symmetries carry charges and are
therefore not proper gauge.

The existing flat TT causal-subsector certificate supplies the complementary
physical statement: after TT reduction and the local Einstein-branch Cauchy
conditions, the two helicities have the Einstein-Hilbert symplectic current
and positive `P_0` energy.  The present certificate does not rederive or
replace that physical Cauchy pairing.

## Extra branch and interpretation boundary

The second characteristic root carries five degree-zero symbol classes and
five BV-dual degree-one classes.  These are genuine extra Einstein--Weyl
linearized modes.  Calling them particles, assigning a norm, or deciding
whether boundary conditions exclude them requires a declared causal phase
space.  The fixture has (p^2=-1) in signature `(+---)`; it is an algebraic
root test, not by itself a positive-energy mass-shell assertion.

The zero fiber is deliberately not promoted.  Its dimensions mix Killing and
reducibility data with compact/global and boundary-sensitive modes.  A
finite-dimensional symbol calculation cannot decide which are global
physical states.

Thus the certified interpretation is

\[
\boxed{
\text{local null graviton classes exist}
\quad\text{and}\quad
\text{the closed-cylinder residual quotient is a separate global reduction}
}.
\]

It is not yet a global classical import freeze, a graviton Hilbert space, or a
Lorentzian scattering theorem.

## Next gates

1. Covariantize the framewise contractions over each nonzero characteristic
   component.
2. The universal external-source Ward/defect chain map is now complete in
   `notes/conformal-compensated-sourced-defect-chain-map.md`.  Next select a
   dynamical matter model and lift its full BV complex into that Ward complex;
   the theorem proves that Ward compatibility by itself is insufficient.
3. Classify the (p=0) modes in each chosen global/boundary function space.
4. Construct the nonminimal causal complex and its Green/current pairing.
5. At null infinity, decide which conformal transformations are charged,
   recover the radiative symplectic form, and test whether boundary conditions
   remove the five-class extra branch causally.

Machine artifacts:

- `bridge/certificates/compensated_minimal_bv_operator_export.json`;
- `bridge/certificates/compensated_nonzero_characteristic_snapshot.json`.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
