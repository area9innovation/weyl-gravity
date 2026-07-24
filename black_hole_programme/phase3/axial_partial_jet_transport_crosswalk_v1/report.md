# Exact local partial-jet crosswalk

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The published complete reconstruction has old state order
\((\mathrm{carrier}_4,\mathrm{metric}_2)\). Combining its exact flow with the
published carrier gauge \(T=[J,N]\) and metric master transformation \(U\)
gives the new order
\((\mathrm{metric\ RW},\mathrm{carrier\ RW},L_x)\). Direct transformation of
the entire six-state connection verifies

\[
G'G^{-1}+G\,A_6G^{-1}
=
\begin{pmatrix}
A&E&C\\
0&A&D\\
0&0&A_x
\end{pmatrix}.
\]

The missing block is \(C=USN\). It has rank one, and its \((0,0)\) entry
reproduces the earlier natural-gauge \(L_x\)-to-metric witness. The already
published \(E=USJ\) block is independently reimported by content hash and
rechecked as rank one.

More strongly,

\[
[E\ C]=US[J\ N]
\]

has rank one. The explicit factorization
\(US=(-r,1)^T\rho\) gives a single scalar forcing
\(\sigma=\rho(JY+NZ)\); both upper-row extension blocks are projections of
that same scalar source.

This exact connection is the partial first jet of the four-state family

\[
\mathcal B(\tau)=
\begin{pmatrix}
A+\tau E&D+\tau C\\
0&A_x
\end{pmatrix}.
\]

Differentiating only the upper spin-two row, while holding the spin-one state
fixed, reproduces the six-state system. Calling it a full jet would be
incorrect: the full jet of all four states would have dimension eight.

The same exact functor applied to a base fundamental map
\(\Phi_4(\tau)=\left(\begin{smallmatrix}P(\tau)&Q(\tau)\\0&R\end{smallmatrix}\right)\)
gives
\(\Phi_6=\left(\begin{smallmatrix}P&\dot P&\dot Q\\0&P&Q\\0&0&R\end{smallmatrix}\right)\)
and \(\det\Phi_6=(\det P)^2\det R\). Endpoint derivative formulas require
compatible analytic endpoint frames and remain conditional.

This result supplies the correct algebra for a correlated transport
successor, but it does not itself validate that successor. The H4
exterior-norm rail already shared the frequency generator across all real
coordinates and still failed through Taylor-product conditioning. Therefore
the needed arithmetic is a mixed algebra of shared \(\omega\)-Taylor models
and intrinsic dual numbers, not dual numbers alone.

No endpoint frame, outgoing map, scattering identity, interval enclosure, or
bounded direct-integral map is claimed.

CLOSE-OUT: DONE — exact local partial-jet crosswalk certified; endpoint jet frames and bounded transport remain open.

EVIDENCE: `black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json`
