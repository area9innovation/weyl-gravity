# Phase 3 axial infinity practical transfer

## Scope

This work imports the complete six-state axial Schwarzschild reconstruction at
`d5d5d6de648795203604d62ce7bc4f4ce6fea510` and the singular-endpoint
existence package at `ed3d95901`.  It treats only the axial `ell=2`, `M=1`,
real-frequency rectangle

\[
\frac12\leq M\omega\leq\frac34
\]

and only the infinity-to-`R=32M` initializer.  It does not compute a global
horizon-to-infinity connection, current, flux, scattering channel, pole,
stability statement, or CPT metric.

## Exact structural result

The phase-normalized formal frame has the exact lower-triangular form

\[
B=\begin{pmatrix}C&0\\ M&D\end{pmatrix}.
\]

The carrier residual is `O(z^6)`, the two Einstein-kernel residuals are
`O(z^5)`, and the lower forced residual orders are `(3,3,3,2)` before the row
and column weights are applied.  For the oscillatory `XI2` and `XI3` columns,
the final derivative coefficient is retained exactly:

\[
F_4=(h_{\rm power}-3)H_{1,3}.
\]

With this coefficient every same-rate and cross-rate entry of

\[
\frac{dZ}{dz}=z^{-2}K(1/z,\omega)Z
\]

has amplitude `O(z)` or better.  The exact continuous extension at `z=0` is
therefore the zero matrix.  Cross-rate phases are enclosed by the unit circle;
neither `1/z` nor `log z` is evaluated at the endpoint.

## Validated transfer

The exact coefficient proof uses the block solves for `C` and `D` separately,
with rational-centre Neumann certificates on a rational subdivision of the
full `(z,omega)` rectangle.  The generated Forge consumer integrates the
twelve-real-dimensional correction flow using `math/ivlinode`, compares two
subdivision depths, reconstructs the standard state order

`Re(P,P',Q,Q',H1,F), Im(P,P',Q,Q',H1,F)`,

and independently Krawczyk-certifies full rank of the finite-radius basis.
The resulting public entry point is `axial_infinity_initializer(which)` in
`validated_infinity_transfer.forge`; it returns `IvEndpointCert` objects that
can be consumed directly by the global validated connection rail.

The coefficient enclosure uses 64 exact rational frequency cells and 32
exact rational radial cells.  The generated consumer passed the C and native
x86-64 backends and both ASan/UBSan variants.  An independent verifier checks
the imported hashes, exact rectangle cover, zero-extension powers, Neumann
contractions, rank and claim boundary; six negative mutations must be
rejected.

## Evidence

- `black_hole_programme/phase3/axial_infinity_practical_transfer/certificate.json`
- `black_hole_programme/phase3/axial_infinity_practical_transfer/validated_infinity_transfer.forge`
- `black_hole_programme/phase3/axial_infinity_practical_transfer/verify.py`
- `black_hole_programme/phase3/axial_infinity_practical_transfer/mutations.py`
- `black_hole_programme/phase3/axial_infinity_practical_transfer/receipt.json`

## Boundary

The theorem is an endpoint handoff, not global scattering.  In particular it
does not establish that any finite formal additional direction is populated
by future-horizon-regular data.

CLOSE-OUT: DONE — the F4-corrected infinity normal form has a continuous phase-normalized z-flow and a full-rank validated R=32 IvEndpointCert on the declared real-frequency rectangle.
EVIDENCE: black_hole_programme/phase3/axial_infinity_practical_transfer/certificate.json
