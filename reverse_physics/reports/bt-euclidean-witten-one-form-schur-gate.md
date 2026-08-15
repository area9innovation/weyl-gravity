# BT Witten one-form Schur gate

## Result

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The pointwise-Hessian barrier does not rule out the strongest natural
finite-volume covariance method.  For the normalized BT measure

\[
 d\mu(\psi)=Z^{-1}e^{-S(\psi)}d\psi
\]

on the mean-zero field carrier, the scalar Witten operator is

\[
 \mathcal L_0=d_\mu^*d
 =-\Delta_H+\nabla S\mathbin\cdot\nabla,
\]

and the corresponding one-form operator is

\[
 \boxed{\mathcal L_1=dd_\mu^*+d_\mu^*d
 =\mathcal L_0\otimes I+\nabla^2S.}
\]

It obeys

\[
 \mathcal L_1(df)=d(\mathcal L_0f)
\]

and the exact quadratic-form identity

\[
 \langle v,\mathcal L_1v\rangle_{L^2(\mu)}
 =\mathbb E_\mu\!\left[
   \|D_Hv\|_{\rm HS}^2+v^T(\nabla^2S)v\right]
 =\|d_\mu^*v\|_{L^2(\mu)}^2+\|dv\|_{L^2(\mu)}^2
 \geq0.
\]

The field-space derivative term can compensate a negative pointwise action
Hessian.  Consequently neither the certified period-four negative
orthogonal Hessian block nor the new low-action flat-coordinate negative
curvature is a no-go theorem for \(\mathcal L_1\).

For a centered observable \(F\), on the gradient cyclic subspace and with the
finite-volume Friedrichs domains understood,

\[
 \operatorname{Var}_\mu(F)
 =\langle dF,\mathcal L_1^{-1}dF\rangle_{L^2(\mu;H)}.
\]

This replaces the invalid pointwise Hessian inverse with the correct positive
operator.  It is an exact reduction, not yet the missing uniform estimate.

## Why this changes the barrier

The earlier Schur attempt split the ordinary action Hessian into the lowest
Fourier sector and its orthogonal complement.  An exact period-four family
made the orthogonal block negative, so that block had no positive inverse.

That calculation omitted a term which is essential for covariance.  The
Helffer--Sjöstrand equation acts on one-forms over the entire configuration
space.  Its complement block contains not only the pointwise orthogonal
Hessian but also \(\mathcal L_0\), the positive field-space diffusion
operator.  Schematically,

\[
 Q\mathcal L_1Q
 =Q(\mathcal L_0\otimes I)Q+Q(\nabla^2S)Q.
\]

Thus a vector field concentrated near a negative-curvature configuration
pays a configuration-space localization cost.  The factorization above says
that the exact total cost can never be negative.  Pointwise nonconvexity is
still a serious coercivity problem, but it is no longer a fatal sign error.

## Correct lowest-mode Schur complement

Let \(P\) project the spatial one-form index onto the complete lowest axial
cosine--sine sector and put \(Q=I-P\).  On the finite-volume one-form Hilbert
space define

\[
 A=P\mathcal L_1P,\qquad
 B=Q\mathcal L_1Q,\qquad
 C=Q\mathcal L_1P.
\]

On the source cyclic subspace, or equivalently after the standard Friedrichs
regularization before taking its limit, the operator Schur complement is

\[
 \mathcal K_W=A-C^*B^{-1}C,
 \qquad
 P\mathcal L_1^{-1}P=\mathcal K_W^{-1}.
\]

For the lowest-mode amplitude \(T\) in the normalization of
`REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1`, the live
bound becomes

\[
 \langle dT,\mathcal L_1^{-1}dT\rangle
 \leq\frac{C}{N\omega_L^2}.
\]

The already-certified all-background conditional curvature controls the
direct \(P\) fiber with coefficient \(2/9\).  What remains is the reduction
caused by coupling through \(C^*B^{-1}C\).  A proof must retain the
field-space Dirichlet term in \(B\).  A negative result must construct a
normalized low-Rayleigh sequence for the full one-form form, with nonzero
overlap with \(dT\); another field at which \(\nabla^2S\) is negative is not
enough.

## Exact symbolic check

The certificate checks the commutator on a deliberately nonconvex,
confining polynomial potential

\[
 S(x,y)=\frac{x^4}{4}-\frac{x^2}{2}+\frac{y^2}{2}+\frac{xy}{3}.
\]

At the origin,

\[
 \nabla^2S(0,0)=
 \begin{pmatrix}-1&1/3\\1/3&1\end{pmatrix},
 \qquad \det\nabla^2S(0,0)=-\frac{10}{9}<0.
\]

For

\[
 f(x,y)=x^3y+2xy^2+\frac15y^3-x,
\]

the producer expands both components of
\(\mathcal L_1(df)\) and \(d(\mathcal L_0f)\) in exact rational polynomial
arithmetic and proves coefficientwise equality.  The independent verifier
uses a separate dense-polynomial implementation and checks the degree-bounded
identity on a complete rational interpolation grid.  This fixture does not
prove the general calculus identity by sampling; it independently falsifies
the machine projection of the displayed analytic derivation.

## Relation to membrane-model work

[Eric Thoma's non-Gaussian membrane analysis](https://arxiv.org/abs/2112.07584)
uses the Helffer--Sjöstrand one-form equation and its variational energy to
control models with Hamiltonian \(\sum_xV(\Delta\phi_x)\).  That theorem
assumes a smooth uniformly convex single-site potential \(V\).  The BT action
is not of that form and its pointwise Hessian has exact negative witnesses,
so Thoma's coercivity theorem cannot simply be imported.

The transferable lesson is the operator level at which the estimate should
be posed.  No literature novelty is claimed for the Witten identity itself.
The new result here is the exact BT dependency boundary and the corrected
operator Schur gate.

## Meaning and next calculation

In ordinary language, we had been asking whether every frozen configuration
looks convex.  The answer is no.  The corrected question asks whether a
wavepacket in the space of configurations has enough total energy after its
localization cost is included.  That question is still open, but it survives
all certified pointwise counterexamples.

The next calculation should use the \(2/9\) conditional-mode curvature in
the \(P\) block and seek a relative form bound on the coupling \(C\): for
example,

\[
 \|B^{-1/2}Cw\|^2
 \leq(1-\varepsilon)\langle w,Aw\rangle
\]

uniformly on the \(dT\) cyclic sector.  The falsification branch is an exact
or rigorously bounded family \(v_L\) with small full Witten Rayleigh quotient
and nonvanishing overlap with \(dT\).

This report does not establish that relative bound, an annealed score bound,
the normalized lowest-mode or interacting \(H^{-1}\) estimate, tightness, a
continuum measure, Born probabilities, Krein reconstruction, or Lorentzian
physics.

## Reproducibility receipt

Run the scoped exact rails under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_witten_one_form_schur_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_witten_one_form_schur_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_witten_one_form_schur_gate
```

The producer passed in 0.04 seconds at 21,152 KiB, the independent verifier
in 0.22 seconds at 29,508 KiB, and all 10 focused/mutation tests in 0.50
seconds at 30,768 KiB.  Python compilation passed in 0.04 seconds at 15,996
KiB.  JSON and schema parsing passed.

Tier 0 additionally compiles the Python sources, parses the certificate and
schema, checks the exact four input hashes, runs the scoped diff check, and
inspects the staged paths.  The inputs are unchanged content-addressed
certificates, so Tier 2 requires their hashes rather than rebuilding their
producer chains.  Tier 3 is not applicable: this is an exact method reduction
with the estimate explicitly open, not a freeze, lifecycle promotion,
shared-core change, or release.

The append-only planning import passed with 1,644 nodes, zero invalid items,
and zero malformed events.  The read-only Science Forge shadow wrapper exited
zero but is not scientific verification: its bridge audit failed closed on
the existing Forge binary/library hash mismatch and compiler error `E9118`,
and its census reported 1,765 certificates versus the stale 2026-07-19
baseline of 976.  Those findings remain failures/drift, not passes.

Paper 21 is not edited in this checkpoint.  The independent foundations/Atlas
V12 authority regeneration landed while this calculation was in progress,
and this result changes the viable proof operator without changing the open
interacting-moment or reconstruction lifecycle state.  The exact certificate
and this report are the current publication surface for the scoped method
result; a later Paper 21 synthesis can import it through its generated
authority chain.
