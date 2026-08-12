# BT six-point sequential-history carrier

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The nonextendable positive six-point double pole has an exact ten-channel
sequential-history carrier. This identifies the part that must be counted as
a duration-growing on-shell history and separates it from the signed coherent
interference that still needs a detector and dynamical prescription.

Put (y_A=1/s_A). The certified coefficient formula is

\[
 c=\frac14(J-I)y,
 \qquad D=2c^Tc=y^T\left(J+\frac18I\right)y.
\]

For a fixed on-shell channel (B), the residue column has one zero and nine
entries (1/4). These are precisely the nine allowed products of two
auxiliary (O(1,1)) quartic transitions; the forbidden entry places all three
like species on one vertex. Its Born norm is

\[
 2\|r_B\|^2=2\cdot9\cdot\frac1{16}=\frac98.
\]

The residue map ((J-I)/4) is invertible. Its complete channel Gram is
(G=J+I/8), with spectrum (81/8,1/8,ldots,1/8). Thus no algebraic channel
direction is missing.

## Sequential and interference split

Pole order gives the exact decomposition

\[
 D=\frac98\sum_A\frac1{s_A^2}
   +2\sum_{A<B}\frac1{s_As_B}.
\]

The diagonal term contains every positive double pole and has a formal
direct-sum realization with ten channel labels at leading shell order. This
does not assert that an unresolved physical detector makes those labels
orthogonal. The second term has zero diagonal and Gram (J-I), with one
positive and nine negative eigenvalues. It is coherent interference, not
another positive outcome measure. Near an isolated channel pole it is only
order (1/s_B), while the entire (1/s_B^2) obstruction lies in the sequential
term.

## Finite-time normalization

For

\[
 F_T(\omega)=\int_0^T e^{i\omega t}\,dt,
\]

Plancherel gives

\[
 \int_{\mathbb R}|F_T(\omega)|^2d\omega=2\pi T,
 \qquad \frac{|F_T|^2}{T}\longrightarrow2\pi\delta(\omega).
\]

If the intermediate state has positive energy (E), then
(s=2E\omega+O(\omega^2)). Consequently

\[
 \frac{|F_T(\omega)|^2}{4E^2}
 \longrightarrow \frac{\pi T}{E}\delta(s).
\]

This matches
(1/(s^2+\epsilon_s^2)\to(\pi/\epsilon_s)\delta(s)) when
(epsilon_s=E/T). The BT leading pole therefore becomes the separately
counted sequential coefficient

\[
 \frac{9\pi T}{8E}\delta(s).
\]

This is a universal finite-time Fourier normalization, not a derivation from
the BT interaction Hamiltonian and not a `LORENTZIAN-CAUSAL` construction.

## Remaining physical gate

The calculation constructs the factorization carrier and normalizes its
leading duration dependence. It does not prescribe the off-diagonal
(1/(s_As_B)) distributions, determine which channels a physical detector
resolves, or supply the matching hard survival term. Those require a
wave-packet finite-time factorization block derived from the BT Hamiltonian.
That derivation must fix the previously arbitrary defect partial unitary on
this ten-channel subspace.

No finite inclusive probability, complete Møller/LSZ/S operator, Eq. (19),
loop cancellation, gravity/BRST lift, or Lorentzian causal theorem follows.

## Verification receipt

All scientific and TeX processes ran sequentially under `ulimit -v 500000`.

- The carrier producer passed 16/16 checks in 0.28 s with 65,692 KB maximum RSS.
- The method-distinct verifier independently reconstructed the matrices and the exact finite-time integral, passing 17/17 checks in 0.55 s with 74,552 KB maximum RSS.
- The affected positivity, pole, distributional no-go and carrier chain passed all four producers, all four verifiers and 22 scoped tests; the test run took 2.12 s with 84,912 KB maximum RSS.
- Papers V and VI passed two `pdflatex -interaction=nonstopmode -halt-on-error` runs each. Their second passes took 0.50 s with 50,708 KB and 0.54 s with 50,616 KB maximum RSS.
- Science Forge conformance reports the new work item and event as `OK`; the repository-wide scan still refuses on ten unrelated pre-existing nonconformances, which are neither repaired nor counted as a pass here.
- The non-certifying prose advisory leaves Paper V's pre-existing parenthetical/abstract findings and Paper VI's pre-existing abstract finding; the new text does not push emphasis, dash, or Paper VI parenthetical budgets over their advisory limits.
- Tier 0 includes Python compilation, structured-data parsing, staged diff inspection and `git diff --check`. Tier 2 was required and run because the content-addressed Bateman note changed. Tier 3 was not run because this is a scalar coefficient result, not a freeze, release, shared-core change, or Lorentzian theorem.

CLOSE-OUT: DONE -- the exact ten-channel residue carrier and leading finite-time sequential normalization are constructed; signed interference and BT dynamical affiliation remain open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1.json`
