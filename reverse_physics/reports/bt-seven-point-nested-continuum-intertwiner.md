# BT seven-point nested continuum intertwiner

## Result

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`CLASSIFIED`.

The positive signed seven-point parent/profile quotient has an exact physical
continuum realization in the leading triple-strongly-ordered hierarchy. After
the correct dimensionless substitution, its conditional eigenvalue is a
quadratic polynomial in the inverse middle invariant. Multiplying by the
massless-hierarchy Källén measure and dividing by the exact asymptotic
coefficient gives a positive cumulative coordinate from the middle threshold
onto the whole positive half-line.

The resulting normalized quotient column composes with the certified
two-emission column to give an ordered three-noise isometry for edge marks 15
through 74. Together with the first two continuum certificates, all 75 edge
marks present in the available finite HP instrument now have physical
continuum affiliation. This is a completion of the available three-emission
hierarchy, not an all-order intertwiner, fourth jump, complete probability, or
Eq. (19).

## Dimensionless signed quotient

For the seven-point quotient write

\[
 \alpha=\frac{A}{\tau_1^2},\qquad
 s=\frac{a_3}{\tau_3},\qquad
 w=\frac{\tau_2}{a_2}.
\]

The inherited six-point coordinate gives

\[
 \alpha=2(1-q_{\rm inner}),
\]

so the inner physical threshold ray has

\[
 1\leq\alpha<2.
\]

Both bounds are exact identities rather than endpoint interpolation:

\[
 \alpha-1=\frac{\lambda(w_0,1,r_0)}{w_0^2}\geq0,
 \qquad
 2-\alpha=2q_{\rm inner}>0.
\]

The other two variables obey \(0<s<1\) and \(w>1\). Define

\[
 H_0(\alpha,s)=2+\alpha s(2-s)
\]

and

\[
 H_{\alpha,s}(w)
 =H_0+\frac{6-2\alpha}{w}+\frac{\alpha}{w^2}.
\]

The exact factorization coefficients from the seven-point certificate reduce
to

\[
 u=-\frac{\alpha}{2},\qquad
 v=\frac{\tau_3}{4(1+s)}H_{\alpha,s}(w).
\]

This identity is obtained by substituting the dimensionless variables into
the original expression

\[
 v=\frac{C\tau_3^2-A\tau_2^2
 (a_3^2-2a_3\tau_3+2\tau_3^2)}
 {4\tau_1^2\tau_2^2(\tau_3+a_3)};
\]

it is not inferred from a fitted rate.

Positivity is immediate in the reduced form:

\[
 H_0>2,\qquad 6-2\alpha>2,\qquad \alpha>0.
\]

Consequently \(H_{\alpha,s}(w)>0\), \(u<0<v\), and the signed physical
quotient eigenvalue is

\[
 \lambda_7=-2uv
 =\frac{\tau_3\alpha}{4(1+s)}H_{\alpha,s}(w)>0.
\]

This sharpens the earlier open-domain inequality: every coefficient in the
inverse-\(w\) expansion is positive on the complete declared domain.

## Normalized signed quotient range

With

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},
 \qquad\eta=J\otimes3J,
\]

use the image and kernel bases

\[
 N_+=\begin{pmatrix}
 v&0\\0&v\\u&0\\0&u
 \end{pmatrix},\qquad
 N_-=\begin{pmatrix}
 v&0\\0&v\\-u&0\\0&-u
 \end{pmatrix}.
\]

They satisfy

\[
 N_+^T\eta N_+=6uvJ,
 \qquad
 N_-^T\eta N_-=-6uvJ,
 \qquad
 N_-^T\eta N_+=0.
\]

Because \(uv<0\), the signed profile fundamental symmetry \(-J\) converts the
image form into

\[
 -6uvI_2>0.
\]

For the exact collapse \(R\) and diagonal amplitude map \(D\),

\[
 RDN_+=2uvI_2,
 \qquad RDN_-=0.
\]

The collapse-invisible kernel therefore remains nondegenerate and orthogonal
to the image, while

\[
 E_7(\alpha,s,w,\tau_3)
 =\frac{N_+}{\sqrt{-6uv}}
\]

is the normalized positive quotient embedding.

## Physical middle-threshold resolution

At finite hierarchy parameter \(\epsilon_1\), the mass ratio of the
pre-existing inner cluster to the newly attached middle daughter is

\[
 \rho=\frac{\epsilon_1\tau_1}{a_2}.
\]

The exact two-body measure is

\[
 \frac{\sqrt{\lambda(w,1,\rho)}}{w}\,dw.
\]

On every compact set with \(w>1\), its exact hierarchy limit is

\[
 d\nu_0(w)=\frac{w-1}{w}\,dw.
\]

The large-\(w\) limit of the quotient eigenvalue is

\[
 S_7(\alpha,s,\tau_3)
 =\frac{\tau_3\alpha H_0}{4(1+s)}.
\]

This coefficient fixes the cumulative physical resolution:

\[
 d\chi_{\alpha,s}(w)
 =\frac{\lambda_7}{S_7}d\nu_0
 =\frac{H_{\alpha,s}(w)}{H_0}
   \frac{w-1}{w}\,dw.
\]

Every factor is positive for \(w>1\), the density vanishes at threshold, and

\[
 \lim_{w\to\infty}\frac{d\chi_{\alpha,s}}{dw}=1.
\]

Thus the new gap is asymptotically linear rather than logarithmic. That is not
a change of physical dimension: it is the exact resolution scale selected by
the seven-point quotient and middle two-body measure.

The range statement has an elementary exact primitive. Set

\[
 B=\frac{6-2\alpha}{H_0},\qquad
 C=\frac{\alpha}{H_0}.
\]

Then

\[
 F_{\alpha,s}(w)=
 w+(B-1)\log w-\frac{C-B}{w}+\frac{C}{2w^2}
\]

obeys \(F'=d\chi/dw\). Taking the threshold as origin gives

\[
 \chi_{\alpha,s}(w)=F_{\alpha,s}(w)-F_{\alpha,s}(1).
\]

It is continuous and strictly increasing, and
\(\chi_{\alpha,s}(w)/w\to1\). Therefore it maps \([1,\infty)\)
bijectively onto \(\mathbb R_+\).

The coordinate is invariant under exchange of the innermost daughters because
\(q_{\rm inner}\), hence \(\alpha\), is exchange invariant. All 60 labeled
histories use the same conditional formula by the already certified external-
label permutation covariance. The chronologically attached middle daughter is
not silently identified with the pre-existing cluster.

## Conditional direct-integral isometry

On the measurable field of signed positive quotient ranges define

\[
 (C_{\alpha,s}f)(w)
 =\sqrt{\frac{\lambda_7}{S_7}}
 E_7(\alpha,s,w,\tau_3)
 f(\chi_{\alpha,s}(w)).
\]

Then

\[
\begin{split}
 \|C_{\alpha,s}f\|^2
 &=\int_1^\infty d\nu_0(w)
   \frac{\lambda_7}{S_7}
   \|f(\chi_{\alpha,s}(w))\|^2\\
 &=\int_0^\infty d\chi\,\|f(\chi)\|^2.
\end{split}
\]

Since \(\chi\) is bijective and \(E_7\) has full rank on its image,
\(C_{\alpha,s}\) is unitary onto the quotient-range direct integral.

Right translation in \(\chi\) conjugates to transport along

\[
 w\longmapsto
 \chi_{\alpha,s}^{-1}(\chi_{\alpha,s}(w)+b).
\]

The square-root Radon--Nikodym ratios and the canonical signed polar transports
telescope, so these conditional shifts satisfy the exact semigroup law. They
are auxiliary resolution shifts, not Minkowski-time translations.

## Ordered three-noise carrier

The physical carrier through three emissions is

\[
 \mathcal H^{\rm phys}_{\mathrm{HP},3}
 =L^2\!\left(\{0<t_1<t_2<t_3\},dt_1dt_2dt_3\right)
 \otimes\mathbb C^{60}_{\rm edge}
 \otimes\mathbb C^2_{\rm species}.
\]

Identify the third ordered gap by

\[
 t_3-t_2=\chi_{\alpha,s}(w).
\]

Fibrewise composition of \(C_{\alpha,s}\) with the certified two-emission
intertwiner \(A_2\) defines \(A_3\). The two exact change-of-variable
identities and the normalized polar ranges give

\[
 A_3^*A_3=I,
 \qquad
 A_3A_3^*=P_{\rm seven\mbox{-}point\ range}.
\]

Joint translations of \((t_1,t_2,t_3)\) pass through the prior column and
leave both ordered gaps fixed. Conditional shifts of the third gap conjugate
through \(C_{\alpha,s}\). Thus all 60 third-level histories, HP marks 15
through 74, have physical continuum columns.

Direct-summing the vacuum identity and the independently certified
one-, two-, and three-emission columns gives

\[
 A_{\leq3}=I_{\rm vac}\oplus A_1\oplus A_2\oplus A_3.
\]

This is an isometry onto the direct sum of the available physical ranges and
affiliates marks 0 through 74. No extrapolation beyond level three occurs in
this statement.

## Finite-hierarchy exhaustion

Before taking the hierarchy limits, the exact middle thresholds imply

\[
 \left(1+\sqrt{\frac{\epsilon_1\tau_1}{a_2}}\right)^2
 \leq w\leq
 \frac{(\sqrt{\tau_3}-\sqrt{a_3})^2}{\epsilon_2a_2}.
\]

The lower endpoint tends to one as \(\epsilon_1\to0\), and the upper endpoint
tends to infinity as \(\epsilon_2\to0\). Since every compact \(\chi\) shell
has a compact \(w\) preimage, those finite domains exhaust compactly supported
sections in the prior variables, \(\chi\), \(\alpha\), and \(s\), bounded
away from all endpoints. Such sections form the declared dense core.

Only the measure and column limits are taken. No derivative with respect to
\(\epsilon_1\), \(\epsilon_2\), or an external mass is used, so the earlier
strong endpoint-derivative obstruction is not bypassed.

## Rates and channel count

The exact conditional rates are

\[
 q_0=\frac1{48},\qquad
 q_1=\frac5{64},\qquad
 q_2=\frac{27}{400}.
\]

For one labeled history before the ordered simplex,

\[
 q_0q_1q_2=\frac9{81920}.
\]

The ordered three-simplex contributes \(1/6\), so the coefficient per history
is

\[
 \frac3{163840}.
\]

There are five children for each of 12 second-level parents. Summing the 60
histories gives

\[
 60\frac3{163840}=\frac9{8192},
\]

exactly the independently certified seven-point coefficient. The level-two HP
drift is likewise

\[
 \frac12(5q_2)=\frac{27}{160}.
\]

The continuum normalization is fixed by \(S_7\); the independent rate
\(q_2\) is not obtained by rescaling \(\chi\).

## Claim boundary

This constructs physical continuum columns for all 75 edge marks in the
available leading strongly ordered reduced-mode hierarchy. It does not
construct a finite-\(\epsilon\) equality, a fourth jump, an all-order
inductive limit, a complete probability, the non-strongly-ordered seven-body
sector, a strong endpoint derivative, a spacetime Møller/LSZ/S operator,
identification with the public \(R_t\), Eq. (19), loop positivity, a metric/BV
lift, a new physical dimension, anything `LORENTZIAN-CAUSAL`, or literature
priority.

## Independent verification

The independent verifier does not import the producer. It reconstructs the
signed quotient matrices with exact rational arithmetic at three fixtures,
rebuilds the dimensionless quotient from the original seven-point
factorization, differentiates the serialized primitive, checks the
Radon--Nikodym identity and asymptotes, independently takes the massless
Källén and finite-endpoint limits, enumerates the HP channels, and recomputes
all rates. A strict schema and falsifying mutations protect the lifecycle and
claim boundaries.

The certificate is
`REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1`.

## Verification receipt

All scientific Python, SymPy, and TeX processes run sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON/schema parse on scoped artifacts | PASS | at most 0.02 s | at most 15,384 KB |
| 0 | `git diff --check` on scoped paths | PASS | 0.01 s | 11,524 KB |
| 1 | exact producer and certificate drift check | PASS, 43/43 | 0.68 s | 70,420 KB |
| 1 | method-distinct verifier | PASS, 25/25 | 0.55 s | 73,968 KB |
| 1 | producer/verifier plus seventeen falsifying mutations | PASS, 19/19 | 11.20 s | 74,428 KB |
| 1 | Paper V two-pass PDF build | PASS, no new overfull box | 0.44 s + 0.43 s | 50,616 KB / 50,564 KB |
| 1 | Paper VI two-pass PDF build | PASS, no overfull box or final warning | 0.45 s + 0.45 s | 50,748 KB / 50,844 KB |
| advisory | Science Forge planning import | PASS, 1,406 nodes, 0 invalid, 0 malformed | 5.65 s | 524,752 KB |

Tier 2 is unnecessary unless an imported amplitude, signed quotient, HP
channel table, rate, or schema changes. This package is an exact new consumer
of unchanged content-addressed inputs. Tier 3 is unnecessary because no
classical or quantum freeze, release, shared-core change, fourth jump,
all-order theorem, Eq. (19), gravitational transfer, or Lorentzian theorem is
promoted. No skipped or advisory rail is counted as a pass.

The advisory Science Forge shadow rail exited zero but is not scientific
evidence. Its cached Forge binary reported a standard-library hash mismatch,
the bridge audit failed closed with `E9118`, and the read-only census found
1,539 certificates against the 976-certificate baseline. The diagnostics are
preserved under `/tmp/sf-shadow.0LwwNL`; none of these findings is promoted to
a passing verification rail.

## Next gate

The finite 75-mark continuum-affiliation barrier is closed. The next physical
calculation is the complete eight-point pre-trace parent/profile tensor and
its fourth signed quotient. It must decide whether the cumulative-coordinate
construction recurses on an inductive ordered Fock core. In parallel, the
finite direct-sum column must be compared with the certified three-jump Krein
Møller jet to isolate the exact extra condition needed to identify or replace
the public \(R_t\) in Eq. (19). Complete probability, spacetime scattering,
gravity, and Lorentzian claims remain open.
