# C2j-D: residual descent and the deformation--anomaly fork

## Correct interpretation of the C2g result

C2g computes a top-degree residual descent class.  In Hamada's cylinder
conventions, a scalar primary $V_h$ transforms as

\[
sV_h
=c^\mu\nabla_\mu V_h
+\frac h4(\nabla_\mu c^\mu)V_h.
\]

The four-ghost function

\[
\omega={1\over4!}\epsilon_{\mu\nu\rho\sigma}
c^\mu c^\nu c^\rho c^\sigma
\]

obeys

\[
s\omega=-\omega\nabla_\mu c^\mu,
\qquad \omega c^\mu=0.
\]

Consequently both variations are controlled by the same weight defect:

\[
s\!\int V_h
=\left({h\over4}-1\right)
\int(\nabla\!\cdot c)V_h
\quad\pmod{\text{boundary}},
\]

\[
s(\omega V_h)
=\left({h\over4}-1\right)
\omega(\nabla\!\cdot c)V_h.
\]

At $h=4$ both vanish.  Hamada gives these formulas explicitly in
equations (4.8)--(4.12), and equation (6.4) identifies the corresponding
top-ghost insertion in the state--operator map
([arXiv:1202.4538](https://arxiv.org/abs/1202.4538)).  The residual
calculation is therefore naturally read as

\[
\boxed{
[\omega V_4]
\longleftrightarrow
\left[\int d^4x\,V_4\right].}
\]

This also explains the compact-degree centering:

\[
D_{\rm gh}(\omega)=-4,
\qquad D(V_4)=4,
\qquad D_{\rm total}=0.
\]

The statement is exact for the residual conformal algebra.  Promoting it to
an isomorphism in the complete local Diff `x` Weyl complex still requires
the C2i zero-mode transfer.

## What the two classes are

The two normalized residual classes are

\[
[W_+^2],\qquad[W_-^2].
\]

In Euclidean signature, with

\[
C_\pm={1\over2}(C\pm *C),
\]

their sum and difference give, up to the normalization of $C_\pm$,

\[
C^2,
\qquad C\widetilde C.
\]

In Lorentz signature $*^2=-1$ on two-forms.  A real parity-odd density
therefore differs from the raw chiral difference by an
orientation-dependent factor of $i$.  The exact certificate checks both
signature conventions and shows that the change of basis is unitary.  Thus

\[
G_{\rm residual}=I_2
\]

is unchanged in the parity basis.

The even class is the Weyl-square interaction/coupling direction.  Under the
locality, smoothness, Lorentz-invariance, and at-most-four-derivative
hypotheses of
Boulanger--Henneaux, the Weyl action is the unique consistent nonlinear
deformation of a single linear conformal graviton, modulo the usual
equivalences and topological terms
([hep-th/0106065](https://arxiv.org/abs/hep-th/0106065)).  The odd class is
the Pontryagin/theta direction and is locally dynamically inert on a closed
four-manifold.

This yields the corrected headline:

\[
\boxed{
I_2\text{ is a positive pairing on two residual
vertex/deformation classes, not on a propagating graviton Fock space.}}
\]

There is no one-particle absolute residual class in this compact reduction.
Calling $I_2$ a positive graviton Hilbert space would therefore be a
category error.

The two oscillator classes also do **not** exhaust every general-background
local density.  In particular the Euler/type-A anomaly and scheme-dependent
total derivatives require curvature data outside the on-shell Weyl
oscillator module.

## Classical deformation and one-loop obstruction

The even class has two distinct roles:

\[
[C^2]\in H^{0,4}_{\rm def}(s\mid d)
\]

is the allowed classical deformation, while the one-loop trace/Weyl anomaly
contains the type-B class

\[
[c_{\rm W}C^2]\in H^{1,4}_{\rm anom}(s\mid d).
\]

It is useful to record a **literature-seeded projected type-B target**

\[
\pi_B\mathfrak O_1:
\operatorname{span}\{W_{\rm e}^2,W_{\rm o}^2\}
\longrightarrow
\operatorname{span}\{[c_{\rm W}C^2]\}.
\]

For a parity-preserving pure-metric quantization its background-anomaly
normalization is

\[
\boxed{
\pi_B\mathfrak O_1
=\begin{pmatrix}199/30&0\end{pmatrix}.}
\]

This row is not yet a direct calculation of the quantum BV obstruction in
the repository conventions.  C2k separates the counterterm, beta-function,
background-trace, and BV coefficients and leaves the last one undetermined.
The zero in the odd column is conditional on parity and on a
parity-preserving regulator; it is not a universal cohomological theorem for
chiral theories.  The full obstruction is not this one-row matrix.  It also
has an independent type-A Euler component and possibly scheme-dependent
total derivatives, which require a general curved-background local-BV
calculation.

The normalization must be stated carefully.  Tseytlin gives for the isolated
conformal spin-two field

\[
a_2={87\over20},
\qquad c_2={199\over30}
\]

in the convention

\[
b_4=-aE_4+cC^2
\]

([arXiv:1309.0785](https://arxiv.org/abs/1309.0785), equation (1.6)).
Hamada uses the same $199/30$ as the traceless-tensor contribution to the
numerator of the Weyl-coupling beta function.  Adding his Riegert-field
contribution gives

\[
{199\over30}-{1\over15}={197\over30},
\]

followed by an overall $1/(32\pi^2)$ in his beta-function convention
([arXiv:1202.4538](https://arxiv.org/abs/1202.4538), footnote 3).  Thus
“$199/30$ is the beta coefficient” and “$199/30$ is the type-B anomaly
coefficient” are related statements, but not literally the same normalized
quantity.

## The three routes

### A. Strict pure Weyl

Keep only the metric and its Diff `x` Weyl ghosts.  Then the minimal residual
answer remains

\[
H^4_{\rm residual,min}
=\operatorname{span}\{[\omega W_+^2],[\omega W_-^2]\},
\qquad G=I_2,
\]

conditional on the C2i local bridge.  Conventional one-loop quantization has
nonzero $a_2$ and $c_2$, so quantum BRST nilpotency is not established.
An unconventional measure is a proposal until it supplies an explicit local
quantum-master-equation cancellation.

### B. Riegert--Wess--Zumino completion

Hamada's physical states obey

\[
h_{\gamma_l}+l=4,
\qquad
\gamma_l=2b_1\left(1-\sqrt{1-{4-l\over b_1}}\right).
\]

The certificate verifies the identity exactly.  In particular $l=6$
requires $h_{\gamma_6}=-2$.  Higher-weight Weyl composites may therefore
return to total weight four after Riegert dressing.  The pure-Weyl finite
matter-weight-four inventory no longer exhausts the enlarged cohomology, and
its pairing must be recomputed.

### C. Additional conformal fields

Extra conformal matter or higher-spin fields can change the anomaly balance,
but they also enlarge the residual coefficient module.  Tseytlin's 2013
calculation records the zeta-regularized vanishing of the complete bosonic
CHS $a_s$ sum under its stated prescription, while the $c_s$ analysis was
prescription-dependent.  A later $S^4_q$ calculation selects the $r=-1$
prescription and reports vanishing regularized sums of both $a_s$ and $c_s$.
Neither free-tower result establishes anomaly cancellation in a complete
interacting CHS theory
([arXiv:1707.02456](https://arxiv.org/abs/1707.02456)).

## Recommended sequence

The three routes should not be mixed in one cohomology calculation.

1. Finish C2i for strict pure Weyl gravity.  This establishes exactly what
   the positive residual deformation-class pairing lifts to at the classical
   local-BV level.
2. Formulate the strict-theory quantum master equation on a general curved
   background and recover both the type-A and type-B local classes.  This is
   the clean baseline obstruction; the cylinder alone cannot supply it.
3. If a quantum completion is the goal, treat the Riegert--Wess--Zumino
   theory as a new coefficient module and recompute its centered cohomology
   and pairing.  It is the most concrete finite-field candidate, but it must
   not inherit the strict-theory two-class theorem by assumption.
4. Keep the CHS enlargement exploratory: even a prescription for which both
   regularized free-tower sums vanish is not an interacting anomaly theorem.

Thus no route choice is hidden in C2j-D.  It supplies a common baseline and
makes every proposed cure pay the correct cohomological price.

## Exact claim boundary

`symbolic/verify_conformal_descent_anomaly.py` proves or audits:

1. equality of the integrated and top-ghost weight defects;
2. closure at weight four and compact-degree centering;
3. Euclidean and Lorentzian parity/self-dual conventions;
4. preservation of the residual $I_2$ under the parity change of basis;
5. the exact coefficient arithmetic $199/30-1/15=197/30$;
6. rank one of the parity-preserving **projected type-B** map; and
7. the exact Riegert dressing identity.

It does not compute:

- the full local Diff `x` Weyl descent;
- a one-loop determinant;
- the Euler/type-A anomaly;
- anomaly cancellation or the quantum master equation;
- the cohomology of the Riegert or extra-field completions; or
- positivity of a propagating-particle Hilbert space.

Reproduce with

```bash
python3 symbolic/verify_conformal_descent_anomaly.py
```

The fail-closed rails reject each of the broad claims above explicitly.

The normalization/compensator audit and the dynamical/topological quotient
are continued in
[`conformal-c2k-coefficient-compensator.md`](conformal-c2k-coefficient-compensator.md)
and
[`conformal-c2l-dynamical-topological.md`](conformal-c2l-dynamical-topological.md).
