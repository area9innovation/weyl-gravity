# BT canonical phase-score connection

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_PHASE_SCORE_CONNECTION_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

Lifecycle: CANONICAL_PHASE_SCORE_MOMENT_CONTROL_PROVED

## Result

The normalized cosine--sine Ward frame can be inverted without creating a
new, more singular connection term. The exact canonical score for the
two-dimensional lowest-phase marginal is now known, and the connection part
has a volume-uniform estimate at the physical lowest-frequency scale.

On the periodic four-torus, write

\[
 h(x)=
 \begin{pmatrix}
 \cos(2\pi x_\mu/L+\alpha)\\
 \sin(2\pi x_\mu/L+\alpha)
 \end{pmatrix},
 \qquad
 F_i=\sum_xh_i(x)\psi_x.
\]

For the reciprocal probability \(\pi\), define the normalized frames and
their phase matrix by

\[
 X_i=P_H(\pi h_i),\qquad
 G_{ij}=X_i\mathbin\cdot\nabla F_j
       =\sum_x\pi_xh_i(x)h_j(x).
\]

The preceding inverse-ellipticity theorem proves that \(G^{-1}\) exists and
that \(\sin^2(2\pi/L)G^{-1}\) has a volume-uniform second moment. Define the
canonical lifts

\[
                       Z_i=\sum_j(G^{-1})_{ij}X_j.
\]

They satisfy

\[
                         Z_i\mathbin\cdot\nabla F_k=\delta_{ik}.
\]

If \(Y_i\) denotes the normalized Ward score,

\[
                 \mathbb E[X_i\mathbin\cdot\nabla f]
                 =\mathbb E[fY_i],
\]

then the exact field-level canonical score is

\[
 \boxed{\displaystyle
 S_i=\sum_j(G^{-1})_{ij}Y_j
       -\sum_jX_j[(G^{-1})_{ij}].}
\]

For every smooth test function \(g\) on the phase plane,

\[
 \boxed{\displaystyle
 \mathbb E[\partial_i g(F)]=\mathbb E[S_i g(F)].}
\]

In particular,

\[
                 \mathbb E[S_i]=0,\qquad
                 \mathbb E[F_kS_i]=\delta_{ik}.
\]

The second term in \(S\) is the connection. The main new identity is

\[
 \boxed{\displaystyle
 C:=\sum_jX_j[(G^{-1})_{\cdot j}]
 =\sum_x\pi_x^2(\ell_x-1)G^{-1}h(x),\qquad
 \ell_x=h(x)^TG^{-1}h(x).}
\]

Its coefficients are nonnegative and have total mass at most one. Therefore

\[
                         |C|\leq\|G^{-1}\|_{\rm op}
\]

pointwise. Consequently,

\[
 \mathbb E\left[
  \left(\sin^2(2\pi/L)|C|\right)^2\right]
 \leq16+4\lambda^2.
\]

At \(\lambda=2/5\), the right side is \(416/25\).

Thus differentiating \(G^{-1}\) does not cost a second inverse power. A
higher constant-frame Ward calculation below also controls all moments of
the weighted residual energy. Combined with reciprocal uncertainty, it
controls the correlated drift \(G^{-1}Y\) and the full canonical score in
scaled \(L^2\). The remaining barrier is coercivity: an upper score moment
does not prevent a broad phase marginal or prove an upper field variance.

## Canonical lift and its cost

The phase vector has unit Euclidean norm at every site. For
\(v\in\mathbb R^2\), the corresponding linear combination of normalized
frames is

\[
                    X(v)=P_H\bigl(\pi\,h\mathbin\cdot v\bigr).
\]

Orthogonal projection is a contraction, \(\pi_x^2\leq\pi_x\), and therefore

\[
 \begin{aligned}
 |X(v)|^2
 &\leq\sum_x\pi_x^2(h(x)\mathbin\cdot v)^2\\
 &\leq\sum_x\pi_x(h(x)\mathbin\cdot v)^2
 =v^TGv.
 \end{aligned}
\]

Putting \(v=G^{-1}e_i\) gives

\[
 |Z_i|^2\leq e_i^TG^{-1}e_i,
\]

and hence

\[
 \sum_i|Z_i|^2\leq\operatorname{tr}G^{-1}
 \leq2\|G^{-1}\|_{\rm op}.
\]

Cauchy--Schwarz and the certified inverse second moment now give

\[
 \mathbb E\left[
  s_L^2\sum_i|Z_i|^2\right]
 \leq4\sqrt{4+\lambda^2},
 \qquad s_L=\sin(2\pi/L).
\]

At \(\lambda=2/5\), this is \(8\sqrt{26}/5\). This is an actual normalized
volume-uniform cost for lifting coordinate derivatives from the phase plane
back to the full field space.

## Derivation of the canonical score

Because \(G\) is positive definite at every finite field, the definition of
\(Z_i\) and the identity \(X_jF_k=G_{jk}\) immediately imply
\(Z_iF_k=\delta_{ik}\). Thus

\[
 \partial_i g(F)=Z_i g(F)
 =\sum_j(G^{-1})_{ij}X_jg(F).
\]

Apply the fixed-frame Ward identity to the product
\((G^{-1})_{ij}g(F)\):

\[
 \mathbb E\left[
  X_j\bigl((G^{-1})_{ij}g(F)\bigr)\right]
 =\mathbb E\left[(G^{-1})_{ij}Y_jg(F)\right].
\]

Expanding the derivative and summing \(j\) gives the boxed canonical score.
Finite-volume coercive tails justify the cutoff removal. The volume-uniform
claim in this certificate concerns \(Z\) and \(C\), not the complete
correlated score.

The conditional expectation

\[
                           \overline S(F)=\mathbb E[S\mid F]
\]

is the negative logarithmic score of the two-dimensional \(F\) marginal in
the distributional sense. The identities
\(\mathbb E S=0\) and \(\mathbb E[F_kS_i]=\delta_{ik}\) follow by taking
\(g=1\) and \(g(F)=F_k\).

This exact normalization is useful but is not an upper variance estimate:
Cauchy--Schwarz applied only to \(\mathbb E[F_kS_i]=\delta_{ik}\) points in
the wrong direction. Coercivity of the score or the full Witten form remains
necessary.

## Why the connection simplifies

For a fixed modulation \(a\), differentiating the reciprocal probability
along \(X_a=P_H(a\pi)\) gives

\[
 X_a\pi_x
 =\pi_x\left(\sum_ya_y\pi_y^2-a_x\pi_x\right).
\]

For the two phase directions define

\[
 t_j=\sum_x\pi_x^2h_j(x),\qquad
 T_j=\sum_x\pi_x^2h_j(x)h(x)h(x)^T.
\]

It follows that

\[
                         X_jG=t_jG-T_j
\]

and

\[
                  X_jG^{-1}=-t_jG^{-1}+G^{-1}T_jG^{-1}.
\]

Contract the \(j\) index in the \(j\)-th column. The first term becomes
\(-G^{-1}\sum_x\pi_x^2h(x)\). In the second term,

\[
 \sum_jh_j(x)\bigl(h(x)^TG^{-1}\bigr)_j
 =h(x)^TG^{-1}h(x)=\ell_x.
\]

Their difference is precisely

\[
                  C=\sum_x\pi_x^2(\ell_x-1)G^{-1}h(x).
\]

The phase matrix is a probability average of rank-one projectors:

\[
                         0<G=\sum_x\pi_xh(x)h(x)^T\leq I.
\]

Therefore \(G^{-1}\geq I\) and \(\ell_x-1\geq0\). The leverage trace identity
is

\[
 \sum_x\pi_x\ell_x
 =\operatorname{tr}\left(
  G^{-1}\sum_x\pi_xh(x)h(x)^T\right)=2.
\]

Hence

\[
                 \sum_x\pi_x(\ell_x-1)=1,
\]

and, because \(0<\pi_x\leq1\),

\[
                 \sum_x\pi_x^2(\ell_x-1)\leq1.
\]

The connection is therefore a subprobability-weighted sum of the vectors
\(G^{-1}h(x)\), each of norm at most
\(\|G^{-1}\|_{\rm op}\). This proves the pointwise connection bound.

## All moments of the weighted residual energy

The same constant normalized frame supplies substantially more than its
first Ward identity. Put

\[
 R=\sum_x\pi_xr_x^2,\qquad
 S_2=\sum_x\pi_x^2,\qquad
 P=\sum_x\pi_x^2r_x^2.
\]

The exact constant-frame derivatives are

\[
 X_1\pi_x=\pi_x(S_2-\pi_x),\qquad
 X_1r_x=-\pi_xr_x,
\]

and therefore

\[
                         X_1R=S_2R-3P.
\]

Its normalized Ward score is

\[
                         Y_1=1-S_2-{R\over\lambda^2}.
\]

Apply the Ward identity to \(R^n\), \(n\geq1\). Exact rearrangement gives

\[
 {1\over\lambda^2}\mathbb E[R^{n+1}]
 =\mathbb E\left[
 R^n(1-(n+1)S_2)+3nPR^{n-1}\right].
\]

Since \(P\leq R\) and the term involving \(S_2\) has a favorable sign,

\[
 \boxed{\displaystyle
 \mathbb E[R^{n+1}]
 \leq\lambda^2(3n+1)\mathbb E[R^n].}
\]

The \(n=0\) Ward identity gives
\(\mathbb E R=\lambda^2\mathbb E(1-S_2)\leq\lambda^2\). Induction proves

\[
 \boxed{\displaystyle
 \mathbb E[R^n]\leq\lambda^{2n}A_n,\qquad
 A_1=1,\quad
 A_n=\prod_{k=1}^{n-1}(3k+1).}
\]

In particular,

\[
 \mathbb E[R^2]\leq4\lambda^4,\qquad
 \mathbb E[R^3]\leq28\lambda^6,\qquad
 \mathbb E[R^4]\leq280\lambda^8.
\]

These are actual normalized, volume-uniform interacting moments. They are
moments of the reciprocal-probability-weighted residual energy, not of the
field.

## All scaled inverse moments

Let \(c=|z_2|\), \(\delta=1-c\), and \(s_L=\sin(2\pi/L)\). Reciprocal phase
uncertainty gives

\[
                         R\geq{16s_L^4c^4\over\delta^2}.
\]

For an integer \(m\geq1\), split into \(c<1/2\) and \(c\geq1/2\). On the
first event \(\delta^{-2m}\leq4^m\); on the second,
\(c^{-4m}\leq16^m\). Hence

\[
 \mathbb E[\delta^{-2m}]
 \leq4^m+{\mathbb E[R^m]\over s_L^{4m}}.
\]

Because \(\|G^{-1}\|_{\rm op}=2/\delta\),

\[
 \boxed{\displaystyle
 \mathbb E\left[
  \left(s_L^2\|G^{-1}\|_{\rm op}\right)^{2m}\right]
 \leq16^m+4^m\lambda^{2m}A_m.}
\]

Thus the preceding second-moment theorem is part of an all-even-moment
hierarchy. Two constants used below are

\[
                  K_2=16+4\lambda^2,\qquad
                  K_4=256+64\lambda^4.
\]

## The correlated drift is controlled

For the lowest phase vector, \(\Delta h=-\omega_Lh\), where

\[
                 \omega_L=4\sin^2(\pi/L)\leq2
                 \quad(L\geq4).
\]

The normalized Ward score is

\[
 Y=-{1\over\lambda^2}\sum_x\pi_xh(x)
       (r_x^2+\omega_Lr_x)
       +\sum_x\pi_x(1-\pi_x)h(x).
\]

Since \(|h(x)|=1\), probability Cauchy--Schwarz gives

\[
                         |Y|\leq
 1+{1\over\lambda^2}\left(R+\omega_L\sqrt R\right).
\]

Put \(A=s_L^2\|G^{-1}\|_{\rm op}\). The inequality
\((a+b+c)^2\leq3(a^2+b^2+c^2)\), followed by Hölder, gives

\[
 \begin{aligned}
 \mathbb E[(s_L^2|G^{-1}Y|)^2]
 &\leq3\left[
   \mathbb E A^2
  +\lambda^{-4}(\mathbb E A^4\,\mathbb E R^4)^{1/2}\right.\\
 &\hspace{35mm}\left.
  +\lambda^{-4}\omega_L^2
   (\mathbb E A^4\,\mathbb E R^2)^{1/2}
 \right].
 \end{aligned}
\]

Substituting the certified moment constants and \(\omega_L\leq2\) proves

\[
 \boxed{\displaystyle
 \mathbb E[(s_L^2|G^{-1}Y|)^2]\leq B_Y,}
\]

where

\[
 B_Y=3\left(
 K_2+\sqrt{280K_4}+{8\sqrt{K_4}\over\lambda^2}
 \right).
\]

Finally \(S=G^{-1}Y-C\), and the connection obeys the \(K_2\) bound. Therefore

\[
 \boxed{\displaystyle
 \mathbb E[(s_L^2|S|)^2]\leq2B_Y+2K_2.}
\]

This closes the integrability and correlation question in scaled \(L^2\).
It does not prove the sign, monotonicity, or inverse-Witten estimate needed
for an upper field variance.

## Exact \(4^4\) fixture

Use the axial reciprocal marginal

\[
                  p=(2/9,1/9,2/9,4/9)
\]

uniformly over the \(4^3=64\) transverse sites. For phases

\[
 h(0)=(1,0),\quad h(1)=(0,1),\quad
 h(2)=(-1,0),\quad h(3)=(0,-1),
\]

one obtains

\[
 G=\begin{pmatrix}4/9&0\\0&5/9\end{pmatrix},
 \qquad
 G^{-1}=\begin{pmatrix}9/4&0\\0&9/5\end{pmatrix}.
\]

The cosine derivative of \(G\) vanishes. For the sine frame,

\[
 X_sG=
 \begin{pmatrix}-5/3888&0\\0&5/3888\end{pmatrix},
\]

and direct matrix differentiation gives

\[
 X_sG^{-1}=
 \begin{pmatrix}5/768&0\\0&-1/240\end{pmatrix}.
\]

Contracting the appropriate columns therefore gives

\[
                         C=(0,-1/240).
\]

The four leverage values are

\[
                         (9/4,9/5,9/4,9/5).
\]

Reconstructing \(C\) from the leverage formula gives the same vector, while
the total subprobability weight is exactly \(59/12960\).

The two full-field canonical lift norms are

\[
                         |Z_c|^2={1\over128},
 \qquad |Z_s|^2={59\over6400}.
\]

Their sum \(109/6400\) is below
\(\operatorname{tr}G^{-1}=81/20\), as required. The independent verifier
reconstructs the 256 site derivatives and the inverse derivative directly,
without importing the producer's moment-tensor formulas.

## Meaning for the reconstruction programme

There were two possible new singularities after inverting the normalized
phase frame:

1. the derivative of \(G^{-1}\), which superficially contains two inverse
   factors;
2. the product of \(G^{-1}\) with the nonlinear Ward score \(Y\).

Both integrability problems are now closed. Exact leverage contraction
reduces the connection to one inverse power. The new constant-frame moment
hierarchy and all-inverse-moment lift control the correlated nonlinear score
in scaled \(L^2\).

The live barrier is no longer size or integrability; it is sign and
coercivity. The exact normalization
\(\mathbb E[F_kS_i]=\delta_{ik}\) and an upper score moment cannot rule out a
broad marginal. The next theorem must show monotonicity of the conditional
canonical score, a relative lower bound in the lowest-phase Witten form, or
an actual BT low-Rayleigh countersequence.

## Boundary

This result does not establish coercivity of the canonical marginal score, a
normalized lowest-mode or field second moment, the interacting \(H^{-1}\)
estimate or its divergence, tightness, or a continuum Euclidean measure. It
does not change the existing scoped ordinary-OS obstruction and has no Born,
Krein, gravitational, or LORENTZIAN-CAUSAL consequence. No
literature-priority claim is made.

## Verification

Run sequentially under the 500 MB cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_canonical_phase_score_connection.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_canonical_phase_score_connection.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_canonical_phase_score_connection

## Verification receipt

The final producer byte check passed in 0.04 seconds with peak RSS 21164 KiB.
The independent verifier passed all 18 checks in 0.10 seconds with peak RSS
30452 KiB. All 12 focused tests passed in 0.14 seconds with peak RSS 30692
KiB, including eight adversarial certificate mutations. Python compilation
passed in 0.04 seconds with peak RSS 16464 KiB. Every Python command ran under
the 500 MB virtual-memory cap.

The Science Forge planning import passed with 1673 nodes, zero invalid items,
and zero malformed events in 7.02 seconds with peak RSS 222900 KiB under
GOMEMLIMIT=300MiB and GOGC=50. Tier 2 uses the unchanged, content-addressed
normalized Ward-frame and reciprocal-phase inverse inputs. Tier 3 was not run
because canonical-score coercivity, the lowest field moment, interacting
\(H^{-1}\) estimate, and continuum lifecycle states remain open. The Science
Forge shadow rail was skipped because no registered shadow input changed;
that skip is not recorded as a pass.
