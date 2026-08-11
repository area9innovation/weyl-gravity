# BT covariant formal Eq. (19) charge support

Certificate: REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1

Lifecycle: CLASSIFIED

Dependencies: LOCAL-ALGEBRAIC, REDUCED-MODE

## Result

The charge-support portion of Bateman--Turok Eq. (19) holds to every formal
order on the covariant zero-mode-completed Laurent--Fock algebra, and it is
stronger there than the published one-sided statement: the pushed projector
is entirely charge neutral, so its strictly negative component is

\[
 Q_{\mathrm{negative}}=0.
\]

This is not the full Eq. (19). Charge zero does not imply ghost evenness, and
the proof does not give time independence, the asymptotic \(R_{\pm\infty}\)
limits, the fixed-vacuum representation, or a generalized-Born trace.

## Exact covariant algebras

Split the perfect-square field into the boost-orbit zero mode and its
nonzero-mode part,

\[
 \phi=\phi_0+\varphi,\qquad Z=e^{\lambda\phi_0}.
\]

Work over the formal Laurent coupling field \(\mathbb Q((\lambda))\). On

\[
 \mathcal A_\phi
 =\mathbb Q((\lambda))[Z,Z^{-1}]\otimes\mathcal A_{\mathrm{nz}},
\]

define

\[
 \delta_\phi(Z^nX)=nZ^nX,\qquad \delta_\phi(X)=0
\]

for every finite nonzero-mode word \(X\). On the target \(O(1,1)\) algebra,

\[
 \delta_{1,1}\Omega=\Omega,\qquad
 \delta_{1,1}\Upsilon=-\Upsilon.
\]

The Krein adjoint preserves these boost charges; this is not the
charge-reversing Hilbert-space \(U(1)\) convention.

## Eq. (16) intertwines the derivations

Let \(\alpha(X)=R^\dagger XR\) denote the Eq. (16) pullback. The exact
zero-mode factorization is

\[
 \alpha(\Omega)
 =\lambda^{-1}Z e^{\lambda\varphi},
\]

\[
 \alpha(\Upsilon)
 =Z^{-1}e^{-\lambda\varphi}
   \left(\Box\varphi+\lambda(\partial\varphi)^2\right).
\]

Coefficient by coefficient,

\[
 [\lambda^{n-1}]\alpha(\Omega)
 = Z\frac{\varphi^n}{n!},
\]

and

\[
\begin{split}
 [\lambda^n]\alpha(\Upsilon)
 =Z^{-1}\bigg[
 &\frac{(-1)^n}{n!}\varphi^n\Box\varphi\\
 &+\mathbf 1_{n\geq1}
 \frac{(-1)^{n-1}}{(n-1)!}
 \varphi^{n-1}(\partial\varphi)^2
 \bigg].
\end{split}
\]

Every \(\Omega\) coefficient has orbit power and charge \(+1\); every
\(\Upsilon\) coefficient has orbit power and charge \(-1\). Hence

\[
 \delta_\phi\circ\alpha=\alpha\circ\delta_{1,1}
\]

on the two generators. Multiplicativity and the Leibniz rule extend this
identity to all formal words, derivatives and finite sums. The certificate
replays the coefficients through order twelve and all \(255\) target words
of lengths zero through seven, but the displayed coefficient formula is the
all-order proof.

The time translation in \(R_t\) preserves this identity. The free
perfect-square Hamiltonian is independent of the constant shift orbit, while
the free \(O(1,1)\) Hamiltonian is assembled from charge-zero cross bilinears.
Their adjoint evolutions therefore commute with the respective derivations,
so

\[
 \delta_\phi\circ\alpha_t=\alpha_t\circ\delta_{1,1}
\]

at every finite \(t\).

## Formal inversion gives the projector result

The perturbative-coisometry rigidity certificate supplies

\[
 R^\dagger R=RR^\dagger=1
\]

coefficient by coefficient. Thus \(\alpha\) is formally invertible on the
declared image. Write

\[
 \beta=\alpha^{-1},\qquad
 \beta(P)=RPR^\dagger.
\]

Applying \(\alpha^{-1}\) to the intertwining identity gives

\[
 \delta_{1,1}\circ\beta=\beta\circ\delta_\phi.
\]

Let \(P\) be a finite nonzero-mode projector satisfying

\[
 P^2=P=P^\dagger,\qquad \delta_\phi(P)=0.
\]

Then

\[
 A=\beta(P)
\]

obeys exactly

\[
 A^2=A=A^\dagger,\qquad \delta_{1,1}(A)=0.
\]

Its charge decomposition therefore has

\[
 A_0=A,\qquad A_q=0\quad(q\neq0).
\]

On this formal covariant algebra the charge-support part of Eq. (19) can be
written

\[
 R_tP R_t^\dagger=P_{\mathrm{neutral}}+Q_{\mathrm{negative}},
 \qquad
 P_{\mathrm{neutral}}=A,\quad Q_{\mathrm{negative}}=0.
\]

The certified order-\(\lambda\) result \(Q_1=0\) is the first-order
specialization of this theorem.

## Why this does not descend to the fixed vacuum

Fixing the broken-symmetry vacuum would impose

\[
 I=(Z-1).
\]

The boost derivation does not preserve that ideal:

\[
 \delta_\phi(Z-1)=Z\equiv1\pmod I.
\]

Consequently the all-order charge theorem does not descend to \(Z=1\).
One cannot use this covariant proof and simultaneously use the
fixed-vacuum strictly-negative radical as if they belonged to the same
graded representation.

The exact alternatives are therefore:

1. keep \(Z\): the formal pushforward is wholly neutral and \(Q=0\);
2. set \(Z=1\): the boost derivation no longer defines the same charge
   decomposition; or
3. construct a larger dynamical zero-mode representation and trace in which
   the broken-vacuum limit is controlled.

## Projector and scattering ledgers remain separate

The Eq. (19) object is

\[
 R_tP_\chi^{(\phi)}R_t^\dagger.
\]

The physical transition object is

\[
 P_{\mathrm{out}}(S_\phi-1)P_{\mathrm{in}}.
\]

The eight-point block \(K_4\) and graph slope \(T\) were derived from the
second, physical-response ledger. They are not coefficients of the first
object unless an explicit intertwiner is constructed. The public-Fock graph
remains a valid candidate response carrier or projector-dilation
architecture, but the present theorem neither requires nor permits fitting
\(T\) as an \(R_t\) coefficient.

## Exact boundary

Established:

- all-order homogeneity of both exact Eq. (16) generator images;
- all-order pullback equivariance;
- all-order inverse equivariance on the formal perturbative image;
- preservation of projector idempotence and adjointness;
- neutral charge support with \(Q=0\) for finite shift-invariant nonzero-mode
  projectors;
- recovery of the previous order-\(\lambda\), \(Q_1=0\) result;
- failure of charge descent through \(Z=1\); and
- separation of the Eq. (19) and physical scattering objects.

Not established:

- ghost evenness of the neutral pushed projector;
- time independence of its neutral coefficients;
- existence of \(R_{\pm\infty}\);
- identification with a specific continuum
  \(P_\chi^{(\Omega\Upsilon)}\) kernel and its domains;
- a fixed-vacuum or semifinite generalized-Born trace;
- the full Eq. (19);
- weak ghost symmetry of a scattering process;
- a physical fourth probability;
- a gravity/BRST lift or anything LORENTZIAN-CAUSAL; or
- literature priority.

## Next gate

The next finite algebraic test is ghost parity, not another charge
calculation. Construct the hidden-parity automorphism on the covariant
Laurent--Fock algebra and determine whether

\[
 \kappa\,\beta(P_\chi)\,\kappa=\beta(P_\chi)
\]

for the declared nonzero-mode projectors. Separately, test whether the
neutral finite-time coefficients commute with the free \(O(1,1)\)
Hamiltonian. Both are necessary before taking asymptotic limits or asking
for the generalized-Born trace.

## Verification receipt

All scientific commands ran sequentially under ulimit -v 500000 with
Python 3.12.13.

- Tier 0 Python compilation and structured-data parsing passed in (0.17) s
  with (14980) KiB peak RSS.
- The exact producer passed 29/29 checks in (0.34) s with (64844) KiB
  peak RSS.
- The independent recurrence/binomial verifier passed 25/25 checks in
  (0.41) s with (68496) KiB peak RSS.
- The falsification suite passed 22/22 tests in (6.06) s with (68804)
  KiB peak RSS. Mutations covered field-map coefficients, charge labels,
  finite-time intertwining, formal two-sidedness, the fixed-vacuum quotient,
  object typing, graph-slope typing, ghost/time/asymptotic promotions, the
  full Eq. (19), physical probability and input hashes.
- Paper V built twice in (0.45/0.44) s with at most (50904) KiB peak
  RSS, retaining exactly its four pre-existing overfull boxes.
- Paper VI built twice in (0.53/0.51) s with at most (50820) KiB peak
  RSS and no overfull box or undefined reference.

The coefficient replay and independent recurrence verifier form the affected
Tier 2 chain. Tier 3 is not a pass and was not required because this is a
CLASSIFIED formal charge-support result, not a full Eq. (19), physical,
Lorentzian, freeze or release promotion.
