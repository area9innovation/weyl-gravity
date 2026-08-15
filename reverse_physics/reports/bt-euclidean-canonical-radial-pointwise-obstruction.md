# BT canonical-radial pointwise obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_RADIAL_POINTWISE_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle: `POINTWISE_RADIAL_SCORE_METHODS_OBSTRUCTED`

## Result

The two immediate pointwise coercivity routes opened by the normalized
additive Ward frame and its canonical two-phase score both fail on exact BT
fields.

First, the globally action-decreasing additive contraction need not decrease
the complete lowest Fourier phase.  On an exact periodic $6^4$ tensor
fixture,

\[
                 F\mathbin\cdot(X_1F)={540\over17}\log2>0.
\]

Second, the exact field-level canonical score need not point radially outward.
At $\lambda=2/5$, an exact periodic $4^4$ tensor fixture gives

\[
                         F\mathbin\cdot S
                 =-{563\over3}\log2<0.
\]

Thus neither $X_1$ nor $S$ supplies an uncompensated pointwise Lyapunov
sign for the lowest phase.  This is a method obstruction, not an obstruction
to the actual Gibbs bound.  The conditional marginal score

\[
                 \overline S(F)=\mathbb E[S\mid F]
                              =-\nabla_F\log\rho_F
\]

may still be coercive after averaging over the complete phase fiber, and the
full Witten one-form quadratic form may still have the required lower bound.

## Exact additive-contraction fixture

On the axial $C_6$, repeated over the $6^3=216$ transverse sites, take

\[
            \Omega=2^n,
       \qquad n=(2,-2,2,0,-1,0).
\]

The reciprocal weights and their normalized axial marginal are

\[
 (\Omega_x^{-1})=(1/4,4,1/4,1,2,1),
 \qquad
 p={1\over34}(1,16,1,4,8,4).
\]

For the lowest cosine--sine phase
$h(x)=(\cos(2\pi x/6),\sin(2\pi x/6))$, direct arithmetic in
$\mathbb Q(\sqrt3)$ gives

\[
 {F\over\log2}=216\,h(1),
 \qquad
 X_1F=\sum_xp_xh(x)={5\over34}h(1).
\]

Their scalar product is the positive number displayed above.  The earlier
additive contraction theorem remains valid: $X_1\cdot\nabla A<0$ away from
the vacuum.  What fails is the extra inference that the same flow must shrink
the selected Fourier phase at every field.

## Exact canonical-score fixture

On the axial $C_4$, repeated over $4^3=64$ transverse sites, take

\[
              \Omega=2^n,
       \qquad n=(-1,0,-1,1).
\]

Then

\[
 p={1\over11}(4,2,4,1),
 \qquad r=(4,-1,4,-3/2),
\]

and for cardinal cosine--sine phases

\[
 G=\begin{pmatrix}8/11&0\\0&3/11\end{pmatrix},
 \qquad
 G^{-1}=\begin{pmatrix}11/8&0\\0&11/3\end{pmatrix}.
\]

The normalized Ward score at $\lambda=2/5$ and lowest frequency
$\omega_4=2$ is

\[
       Y=\left(0,{6201\over7744}\right).
\]

The inverse-frame connection and complete canonical score are

\[
       C=\left(0,{1\over264}\right),
 \qquad
       S=G^{-1}Y-C
        =\left(0,{563\over192}\right).
\]

But the field phase is $F=(0,-64\log2)$, which gives the negative radial
product.  The independent verifier reconstructs the residual, Ward score,
connection, and score site by site rather than importing the producer.

## What survives averaging

The canonical Stein identity proved in the predecessor remains

\[
       \mathbb E[\partial_i g(F)]=\mathbb E[S_i g(F)].
\]

Conditioning on $F$ identifies the actual marginal score and gives

\[
       \mathbb E[F_k\overline S_i(F)]=\delta_{ik},
       \qquad
       \mathbb E[F\mathbin\cdot\overline S(F)]=2.
\]

The negative field-level value in the $4^4$ fixture does not fix
$\overline S$ at that phase: the latter averages $S$ over every full field
with the same two Fourier coordinates.  Likewise, one outward point of the
additive flow does not produce a low-Rayleigh sequence.  Therefore it would
be incorrect to promote either fixture to failure of marginal coercivity,
Witten coercivity, or the interacting moment.

This sharpens the live gate.  Further pointwise sign searches for these two
fields are closed.  The next calculation must retain conditional averaging or
the field-space derivative term in the Witten form.  A valid negative branch
must construct an actual volume-indexed full-Witten low-Rayleigh family with
nonvanishing lowest-phase overlap.

## Meaning in ordinary language

We found two natural arrows that looked as if they might always push a large
long-wavelength wave back toward zero.  Exact examples show that each arrow
can point the wrong way at an individual configuration.  The statistical
average can still push the right way, because it combines all configurations
with the same long wave.  So the theorem may still be true, but it must be
proved statistically rather than one configuration at a time.

## Boundary

This certificate does not establish failure of the conditional marginal
score or the Witten operator, an actual low-Rayleigh sequence, boundedness or
divergence of the normalized lowest-mode or interacting $H^{-1}$ moment,
tightness, or a continuum Euclidean BT measure.  It does not alter the scoped
ordinary Osterwalder--Schrader obstruction and has no Born, Krein,
gravitational, or `LORENTZIAN-CAUSAL` consequence.  No literature-priority
claim is made.

Paper 21 is not changed at this scoped method obstruction because neither the
interacting-moment nor reconstruction lifecycle state changes.

## Reproducibility receipt

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_canonical_radial_pointwise_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_canonical_radial_pointwise_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_canonical_radial_pointwise_obstruction
```

Tier 0 compiles the changed Python, parses the JSON and schema, checks the
predecessor hash, runs the scoped diff check, and inspects the exact paths.
Tier 1 is the deterministic producer, nonimporting exact verifier, and focused
mutation suite.  Tier 2 uses the exact hash of the unchanged canonical-score
certificate.  Tier 3 is not applicable: this is a scoped method obstruction,
not a freeze, lifecycle promotion, shared-core change, release, or theorem
about the actual interacting moment.

Final elapsed-time, peak-memory, planning-import, and repository-audit receipts
are recorded in the machine certificate generated with this report.
