# Berger retained stationary spectral preflight

The retained 26-row causal witness is not itself a uniform fourth-order
Cauchy operator. Exact extraction of its pure temporal leading coefficient
gives ranks

\[
(3,8,8,3)
\]

on bundle ranks \((3,10,10,3)\). In particular, attempting to obtain a
26-row first-order generator by inverting the fourth-time-derivative
coefficient would divide by a singular metric block.

The exact Volterra construction already supplies the correct replacement.
Use rank-six second-order companions for the ghost and identity products,
the exact rank-twenty companion

\[
C_{20}=\begin{pmatrix}\Box_2&-I_{10}\\V_2&\Box_2\end{pmatrix}
\]

for the metric, and its rank-twenty formal-adjoint companion. The resulting
hybrid second-order bundle has rank

\[
6+20+20+6=52,
\]

so its first-order Cauchy generator acts on rank-104 data. This operator,
denoted \(A_{104}\), is the real time-evolution generator. The exact Cauchy
ordering is now frozen as

\[
\Psi_{104}=(\Phi_{52},\partial_t\Phi_{52}),
\]

with the ghost primary/auxiliary ranks (3+3), metric ranks (10+10),
metric-antifield ranks (10+10), and identity primary/auxiliary ranks
(3+3) in each configuration half, followed by the same velocity ordering.

There is an essential factor of (i) between evolution and physical
frequency. With

\[
\partial_t\Psi=A_{104}\Psi,
\qquad
\Psi_\omega(t)=e^{-i\omega t}\Psi_\omega(0),
\]

one has

\[
A_{104}\Psi_\omega=-i\omega\Psi_\omega.
\]

The frequency operator is therefore

\[
H_{104}=iA_{104},
\qquad
H_{104}\Psi_\omega=\omega\Psi_\omega.
\]

Positive frequency means the positive spectral part of \(H_{104}\), not of
\(A_{104}\). Complex conjugation commutes with the real generator
\(A_{104}\), anticommutes with \(H_{104}\), and exchanges frequencies
(\omega\leftrightarrow-\omega). This agrees with the independently frozen
flat kernel (e^{-i|p|\Delta t+i p\cdot\Delta x}).

The differential block form, temporal degree, leading rank, stationary
action \(D=e_0=\partial_t\), global causal evolution and local metric energy
spaces are now pinned. The candidate mixed Sobolev scale assigns

\[
(u,\partial_tu)\in H^{s+1}\oplus H^s,
\qquad
(z,\partial_tz)\in H^s\oplus H^{s-1}
\]

to every companion pair, with candidate graph domain
\(\mathcal E_{s+1}\subset\mathcal E_s\). This is a typed analytic target,
not a closed-realization theorem. It remains to prove that this common
graded Hilbert/Krein space and dense graph domain make \(A_{104}\) closed
and generating.

The candidate embedding \(\mathcal E_{s+1}\hookrightarrow\mathcal E_s\) is
Rellich compact on the spatial Berger sphere. Compactness and finite-slab
energy estimates nevertheless do not identify the actual closed domain or
show that the resolvent is nonempty. A parameter-elliptic theorem for
\(z-A_{104}\), or an equivalent analytic Fredholm/direct mode theorem, is
still required. Only after it isolates zero with finite algebraic
multiplicity may one set

\[
P_0=\frac{1}{2\pi i}\oint(z-A_{104})^{-1}\,dz,
\qquad
E_0=\operatorname{ran}P_0
=\bigcup_k\ker A_{104}^k
=\bigcup_k\ker H_{104}^k.
\]

Multiplication by (i) leaves the generalized zero space and its algebraic
multiplicity unchanged; the \(A_{104}\) and \(H_{104}\) Riesz contours are
rotations of one another. The nilpotent Jordan restriction on \(E_0\) must
be computed, not only the ordinary kernel. A finite-rank smooth Riesz
projector is permitted for state selection after isolation is proved; it
remains forbidden in the causal advanced/retarded construction.

The covariance lift is also frozen in an unambiguous two-slot form,

\[
\omega_{54}(f,h)=\omega_{26}(\pi_{\rm cl}f,\pi_{\rm cl}h).
\]

Its operator expression uses the separately certified cyclic adjoint
identification \(\pi_{\rm cl}=\iota_{\rm cl}^{\sharp}\).

This receipt fixes the size, ordering and frequency convention, but not the
coefficientwise spatial matrix of \(A_{104}\). The next gate must first
extract the stationary \(K_2,K_1,K_0\) blocks, assemble the first-order
operator, prolong the BRST differential to Cauchy data, and derive the
Cauchy Lagrange form. Only after those algebraic carriers exist does the
minimal missing problem become the closed graded/Krein realization and
isolated-zero spectral calculus. Spectral reality is correctly phrased as
imaginary-axis spectrum for \(A_{104}\), or real/definitizable spectrum for
\(H_{104}=iA_{104}\); neither is proved. No Riesz projector, frequency
splitting, covariance, Hadamard state, positivity, QME or quantum theorem is
claimed.

```text
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_retained_stationary_spectral_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_retained_stationary_spectral_preflight
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_retained_stationary_spectral_preflight.py -v
```

## Verification receipt

Recorded 2026-07-17:

- Tier 0: Python compilation, strict JSON-schema parsing, and
  `git diff --check` passed (under one second).
- Tier 1: the independent verifier and 11 focused stationary-spectral tests
  passed as part of the combined Cauchy preflight run.
- Tier 2: the affected nine-certificate Hadamard/companion/Cauchy chain was
  regenerated in 9.9 seconds; all nine freshness checks passed in 11.559
  seconds, all nine independent verifiers passed in 11.844 seconds, and the
  68 direct-consumer tests passed in 21.247 seconds.
- Tier 3 was not run: this is a convention/schema correction with fail-closed
  analytic claims, not a freeze, release, shared-core algebra change, or
  paper-theorem promotion.
