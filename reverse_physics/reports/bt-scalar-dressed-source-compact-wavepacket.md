# BT dressed scalar source on compact wave packets

Certificate:
`REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The leading dressed positive scalar source is no longer restricted to three
delta-normalized box modes. It exists for three genuine compact momentum
wave packets on one common Gaussian image domain, and normalized finite-volume
approximants converge to it. The corresponding finite-rank click/no-click
effects also converge at fixed dimensionless detector strength.

This closes the source-carrier limit. It does **not** yet compute the
momentum-integrated BT Hamiltonian strength for the packets.

## Packet hypotheses

Let

\[
 f_j\in C_c^\infty(\mathbb R^3\setminus\{0\}),\qquad j=0,1,2,
\]

be normalized in the public one-particle measure. Write
\(K_j=\operatorname{supp}f_j\). We impose

\[
 0<\varepsilon\le |\mathbf p|\le M,
\]

on their union, and require both ordinary and reflected separation:

\[
 K_i\cap K_j=\varnothing,
 \qquad
 K_i\cap(-K_j)=\varnothing
\]

for all relevant pairs, including \(K_j\cap(-K_j)=\varnothing\). Hence

\[
 \langle f_i,f_j\rangle=\delta_{ij},
 \qquad
 \langle f_i,\mathcal Rf_j\rangle=0,
 \qquad (\mathcal Rf)(\mathbf p)=f(-\mathbf p).
\]

The reflected condition is substantive. The full pulled
\(\Omega\)-creator contains an annihilator at opposite momentum. Without this
condition it can contract with an earlier creator in the three-particle
product, so the finite-mode formula would not pass unchanged to arbitrary
overlapping packets.

## Bounded scalar pullback

Normalize the scalar Jordan oscillators by

\[
 a_r(\mathbf p)=(2E_\mathbf p)^{3/2}A_r(\mathbf p),
 \qquad E_\mathbf p=|\mathbf p|.
\]

The repaired cross CCR becomes

\[
 [A_1(f),A_2^\dagger(g)]_K=\langle f,g\rangle,
\]

with the same-species Krein contractions zero. The public Appendix-C pullback
then gives

\[
 d_\Upsilon^\dagger(f)
 =Z^{-1}A_1^\dagger(2Ef),
\]

and

\[
 d_\Omega^\dagger(f)
 =Z\left[
 A_2^\dagger\!\left(\frac f{2E}\right)
 -itA_1^\dagger(f)
 +A_1\!\left(\frac{\mathcal R_t f}{2E}\right)
 \right],
\]

where \(\mathcal R_t\) is reflection followed by the harmless unit-modulus
free phase. On the pulled vacuum, and in products satisfying the non-antipodal
support condition, the last term gives no contribution. Thus

\[
 d_\Omega^\dagger(f)|0_{\phi;t}\rangle
 =Z\left[
 A_2^\dagger\!\left(\frac f{2E}\right)
 -itA_1^\dagger(f)
 \right]|0_{\phi;t}\rangle.
\]

The apparent inverse powers of energy are harmless on the declared supports:

\[
 \|2Ef\|_2\le2M\|f\|_2,
 \qquad
 \left\|\frac f{2E}\right\|_2
 \le\frac1{2\varepsilon}\|f\|_2,
 \qquad
 \|-itf\|_2=|t|\|f\|_2.
\]

## One common closable domain

Use the already certified weighted squeeze \(S_t\) and define

\[
 \mathcal G_t=
 S_t\bigl(\ell_{\rm fin}(\mathbb Z)
 \mathbin\otimes
 \mathcal F_{\rm fin}(\mathcal D\otimes\mathbb C^2)\bigr),
 \qquad
 \mathcal D=C_c^\infty(\mathbb R^3\setminus\{0\}).
\]

The squeeze assumptions

\[
 \sup_p|z_p|<1,
 \qquad
 \sum_p|z_p|^2<\infty
\]

give finite polynomial number moments for its Gaussian vacuum. Standard
creation and annihilation estimates therefore make the displayed smeared
operators and all products through degree three well defined on
\(\mathcal G_t\). Their reversed Krein-adjoint products are defined on the
same dense core. Because the fundamental symmetry is bounded, a densely
defined Krein adjoint gives a densely defined Hilbert adjoint. Every declared
creator product is consequently closable.

This is a domain theorem for the needed packet polynomials. It is not a claim
that the full nonlinear \(R_t\) is bounded or globally defined.

## Exact positive packet frame

For a three-bit species word \(x\), define

\[
 |x;f\rangle=
 \prod_{j=0}^2d_{x_j}^\dagger(f_j)|0_{\phi;t}\rangle.
\]

The packet overlaps and normalized cross CCR give

\[
 \langle x;f|y;f\rangle_K=\delta_{y,7-x}.
\]

Therefore

\[
 u_x(f)=\frac{|x;f\rangle+|7-x;f\rangle}{\sqrt2},
 \qquad x=0,1,2,3,
\]

obey

\[
 \langle u_x(f),u_y(f)\rangle_K=\delta_{xy}.
\]

In particular,

\[
 \psi_{\phi,+}^{(0)}(f)=u_0(f)
 =\frac{|\Upsilon\Upsilon\Upsilon;f\rangle
       +|\Omega\Omega\Omega;f\rangle}{\sqrt2}
\]

has exact Krein norm one. Its state orbit support remains
\(\{Z^{-3},Z^3\}\), and its projector support remains
\(\{Z^{-6},1,Z^6\}\).

## Fixed-strength detector effect

Let \(W_f:\mathbb C^4\to\operatorname{span}\{u_x(f)\}\) be the packet-frame
isometry. The fixed-channel residue remains

\[
 R_+=\frac14
 \begin{pmatrix}
 1&0&0&0\\
 0&1&1&0\\
 0&1&1&1\\
 0&1&1&1
 \end{pmatrix},
 \qquad G=R_+^TR_+.
\]

Transporting it only changes its carrier:

\[
 G_f=W_fGW_f^\sharp.
\]

For fixed \(\zeta\), the relative effects

\[
 E_{\rm click}(f)=\zeta G_f,
 \qquad
 E_{\rm no}(f)=P_f-E_{\rm click}(f),
 \qquad P_f=W_fW_f^\sharp,
\]

are positive and complete on the packet four-plane whenever

\[
 0\le\zeta\le16-8\sqrt3.
\]

The declared source has

\[
 q_{\rm click}(f)=\frac\zeta{16},
 \qquad
 q_{\rm no}(f)=1-\frac\zeta{16}.
\]

This statement holds at fixed \(\zeta\). The earlier point-cell expression
for \(\zeta\) is not silently reused as the integrated packet value.

## Finite-volume approximation

Let \(f_j^{(L)}\) be normalized cell-average or step approximants on the same
supports, with

\[
 f_j^{(L)}\longrightarrow f_j\quad\hbox{in }L^2.
\]

The uniform energy bounds imply convergence after both scalar multipliers.
The usual telescoping identity for a trilinear product, combined with the
finite Gaussian number moments, then gives

\[
 u_x(f^{(L)})\longrightarrow u_x(f)
\]

in the weighted Hilbert majorant. For a rank-one Krein operator
\(\Theta_{x,x}=|x\rangle\langle Jx|\), boundedness of \(J\) gives

\[
 \|\Theta_{x,x}-\Theta_{y,y}\|_1
 \le(\|x\|+\|y\|)\|x-y\|.
\]

Consequently the packet-frame projector and both fixed-strength effects
converge in finite-rank Hilbert trace norm. The limiting prepared source and
effect do not depend on the chosen box discretization.

## Remaining physical gate

The carrier problem and the dynamical problem are now separate. The source,
positive plane and fixed-strength effect possess a continuum packet limit.
The next calculation must evaluate the finite-time BT Hamiltonian form
\(\zeta_T[f]\) on those packets, glue the ten channel tubes with an explicit
positive record, and treat their intersection strata. Only then will the
point-cell rate have been replaced by a box-independent packet probability.

Removal of \(\varepsilon\) is a different gate. The ordinary massless Fock
topology remains excluded by the certified squeezed-vacuum divergence; any
zero-gap limit must use the inequivalent weighted representation or a local
algebraic state.

General Eq. (19), the standard shift-invariant \(P_\chi^{(\phi)}\), complete
finite- or all-time scattering, loops, gravity/BRST transfer and every
`LORENTZIAN-CAUSAL` claim remain open.

## Verification receipt

All scientific commands are required to run sequentially under
`ulimit -v 500000`.

The producer uses exact rational step packets to test orthogonality,
antipodal separation, scalar multiplier cancellation, the complement-exchange
Gram and the fixed detector effect. The independent verifier reconstructs
those fixtures with `fractions.Fraction`, including the characteristic
polynomial by a direct Leibniz determinant, rather than importing the SymPy
producer algebra. Mutation tests guard the support gap, reflected annihilator,
packet-strength boundary, ordinary-Fock boundary, Eq. (19) boundary and
trace-norm convergence claim.

- The exact producer passes 26/26 checks with peak resident memory 66,888 KB.
- The independent `Fraction` verifier passes 20/20 checks with peak resident
  memory 23,552 KB.
- Eight tests, including six decisive boundary mutations, pass with peak
  resident memory 24,748 KB.
- Paper 6 rebuilds twice in 0.52 s and 0.54 s with peak resident memory
  50,732 KB and 50,664 KB. No new box warning is introduced; its two existing
  overfull paragraphs remain unchanged apart from shifted source line numbers.
- Tier 2 consists of the content-hash checks of the four unchanged predecessor
  certificates and this new terminal producer/verifier/test package. Tier 3 is
  unnecessary because no shared algebra, freeze, release, QME lifecycle or
  Lorentzian claim changes.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_source_compact_wavepacket.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_source_compact_wavepacket.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_source_compact_wavepacket
```

CLOSE-OUT: DONE -- the leading dressed scalar source and its fixed-strength
positive detector effect have a compact continuum packet realization on a
common closable Gaussian domain and a finite-volume approximation limit; the
packet Hamiltonian strength, infrared removal and general Eq. (19) remain
open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json`
