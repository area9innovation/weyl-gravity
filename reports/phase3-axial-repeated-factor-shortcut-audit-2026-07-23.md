# Phase 3 axial repeated-factor shortcut audit

Date: 23 July 2026

## Verdict

The certified six-dimensional axial Bach module is not conjugate to the
square of the scalar Regge--Wheeler operator.

What is exact is the typed covariant composition

\[
\delta B[h]
=
\left(\frac12\Box+C\right)\delta{\rm Ric}[h],
\]

and the local solution-space extension

\[
0\longrightarrow{\cal E}_{\rm Einstein}^{\,2}
\longrightarrow{\cal E}_{\rm Bach}^{\,6}
\longrightarrow{\cal E}_{\rm Ricci\ carrier}^{\,4}
\longrightarrow0.
\]

The factors act on different field modules.  They have not been identified
by an intertwining isomorphism.

## Scalar-square obstruction and endpoint diagnostic

A second-order scalar Regge--Wheeler operator has a two-dimensional local
radial solution space.  Its square has dimension four.  An invertible
conjugacy cannot map that module onto the certified six-dimensional Bach
module.

The horizon exponent data give a useful diagnostic.  The Regge--Wheeler
scalar exponents are

\[
\{0,-4i\omega\}.
\]

A naïve zero-weight duplicated-root model would repeat these roots.  The
certified four-dimensional Ricci carrier instead has

\[
\{0,0,-4i\omega,-2-4i\omega\},
\]

and the complete Bach module has

\[
\{0,0,0,-4i\omega,-1-4i\omega,-2-4i\omega\}.
\]

These multisets are distinct for real nonzero frequency, so the carrier is
not merely two identical RW endpoint copies.

This comparison is not promoted to a general operator-square no-go.
Composition of singular differential expressions can shift indicial roots
according to their radial weights.  The invariant no-go for a **scalar** RW
square is the six-versus-four solution dimension above.

At infinity the carrier does have two columns at each exponential rate,
\(0\) and \(-2i\omega\).  This is not enough to infer a square.  Their
independent powers are respectively

\[
(0,-1),\qquad(-4i\omega,-4i\omega-1),
\]

and the certified recurrences are log-free.  They form a rank-two tensor
carrier at each rate, not a certified pair of scalar spectral derivatives.

## What remains of the factorization shortcut

The outer Ricci-carrier equation is a second-order tensorial
Lichnerowicz-type system.  Treating it as a four-dimensional first-order
matrix system remains useful.  The complete metric module is then obtained
as an extension by the two-dimensional Einstein kernel.  This block
triangular organization is the valid computational shortcut.

An identical matrix square is not certified.  No common three-component
module or intertwiner identifying the two typed factors has been produced.
The present theorem does not exclude every local weighted matrix square, nor
arbitrary singular, nonlocal or frequency-dependent transformations.

## Spectral derivatives are not automatically physical columns

For a scalar family

\[
P(\lambda)u(\lambda)=0,\qquad P(\lambda)=P_0+\lambda,
\]

differentiation gives

\[
P(\lambda)\,\partial_\lambda u=-u,\qquad
P(\lambda)^2\,\partial_\lambda u=0.
\]

This supplies at most one generalized scalar partner for each of the two
Regge--Wheeler solutions.  Even if both partners lift, the resulting four
columns cannot span the six-dimensional Bach module.

For the actual frequency-dependent radial operator,

\[
P(\omega)\partial_\omega u
=-(\partial_\omega P)u.
\]

The frequency sensitivities used in Taylor transport therefore solve a
variational equation.  They are not automatically homogeneous Bach modes.

There is also a separate time-domain distinction.  A fixed-frequency radial
generalized solution retains \(e^{i\omega v}\), so time translation remains
diagonal.  A genuine time-translation Jordan vector arises only from

\[
\partial_\omega\!\left(e^{i\omega v}u_\omega\right)
=e^{i\omega v}\left(iv\,u_\omega+\partial_\omega u_\omega\right),
\]

whose \(iv\,u_\omega\) term is absent from a radial sensitivity table.

## Superseded polynomial column

The older two-row reconstruction contained

\[
H_1=\mathrm{constant},\qquad H_0=-i\omega r+O(1).
\]

That radial degree-one column was log-free, but it fails the subsequently
restored \(v\phi\) Ricci equation by

\[
\frac{3i(\omega-2i)}{r^2}.
\]

It is nonzero on the real pilot interval, so the column is excluded from the
complete six-dimensional module.  It is neither evidence for a scalar
Regge--Wheeler square nor a time-translation Jordan chain.

## Scope

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This audit does not construct the horizon-to-infinity connection, a
scattering matrix, a canonical spectral-derivative submodule, stability,
CPT positivity, particles, a physical ghost, or unitarity.

Verification:

```bash
python3 -m black_hole_programme.phase3.axial_repeated_factor_audit.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_repeated_factor_audit.tests.test_audit
```
