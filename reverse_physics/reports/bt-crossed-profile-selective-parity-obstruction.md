# BT crossed profile-selective parity obstruction

Certificate: `REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1`

Lifecycle: `CLASSIFIED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The missing crossed six-point sign cannot be supplied by a regular
profile-selective parity on the certified four-component carrier.  A map that
preserves the Krein metric preserves the wrong-sign quotient spectrum.  A map
that reverses the spectrum must reverse the Krein metric, but then it also
reverses the nonzero norm of the already-certified five-point prefix.

Public BT ghost parity and its neutral degree-four symmetric-Fock action are
metric-preserving.  They therefore fall in the first class and cannot generate
the required internal anti-Krein action.  A new doubled/off-diagonal amplitude,
a singular different chart, or a nonfactorizing crossed $3\to3$ pre-trace
term remains open.

## Same-carrier theorem

The parent-jet and spectator-profile metric is

\[
 \eta=J\otimes 3J,
 \qquad J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

On the crossed sheet the diagonal coefficient map and outgoing-style collapse
are

\[
 D_\times=\operatorname{diag}(-q,-q,v,v),
 \qquad R_+=[I_2,I_2],
 \qquad q,v>0.
\]

The raised pullback

\[
 A_+=\eta^{-1}D_\times^TR_+^T(3J)R_+D_\times
\]

has characteristic polynomial

\[
 z^2(z+2qv)^2.
\]

It has a negative rank-two nonzero quotient.

Let $C$ be an invertible same-carrier operation.  If it is a Krein
isometry,

\[
 C^T\eta C=\eta,
\]

then the transformed raised pullback is

\[
 A_C=C^{-1}A_+C.
\]

Its spectrum cannot change sign.  If instead $C$ is anti-Krein,

\[
 C^T\eta C=-\eta,
\]

then

\[
 A_C=-C^{-1}A_+C.
\]

This flips the nonzero eigenvalue to $+2qv$, but also flips the norm of every
vector.

## The non-null prefix obstruction

The certified five-point prefix inside this carrier is

\[
 h=(0,\tfrac12,\tfrac12,0)^T,
 \qquad h^T\eta h=\frac32.
\]

The canonical algebraic repair is

\[
 S_{\rm parent}=\operatorname{diag}(I_2,-I_2),
 \qquad R_+S_{\rm parent}=R_-=[I_2,-I_2].
\]

It is anti-Krein and produces the desired positive characteristic polynomial

\[
 z^2(z-2qv)^2.
\]

But it acts on the prefix as

\[
 S_{\rm parent}h=(0,\tfrac12,-\tfrac12,0)^T,
 \qquad
 (S_{\rm parent}h)^T\eta(S_{\rm parent}h)=-\frac32.
\]

More generally, every anti-isometry obeys

\[
 (Ch)^T\eta(Ch)=-h^T\eta h.
\]

Since $h$ is non-null, no anti-isometry can fix it or preserve its Gram.
Thus the operation that repairs the second crossed quotient cannot be the
identity on the first crossed prefix.

The exhaustive real unit-sign census confirms the general proof:

| Type | Count | Repairs sign | Preserves prefix Gram |
|---|---:|---:|---:|
| Krein isometry | 4 | 0 | 4 |
| Krein anti-isometry | 4 | 4 | 0 |
| Mixed sharp-breaking map | 8 | not an admissible parity | not relevant |

The exact $R_-$ collapse repair is unique up to a global sign.

## Why spectator control cannot be regular

Suppose a same-carrier family $C_s$ is the identity at the no-spectator
boundary, $C_0=I$, but becomes anti-Krein for every $s>0$.  If the family
is continuous at zero, taking the limit in

\[
 C_s^T\eta C_s=-\eta
\]

would give $\eta=-\eta$, a contradiction.  The metric type cannot switch
regularly on a fixed nondegenerate carrier.  A spectator-activated switch
must therefore be singular, discontinuous, or leave the carrier.

## Public ghost parity does not supply the sign

The certified public neutral degree-four two-profile Fock sector has dimension
nine and inertia $(6,3)$.  Its induced ghost parity $\kappa_9$ obeys

\[
 \kappa_9^2=I,
 \qquad \kappa_9^TW_9\kappa_9=W_9.
\]

On the selected two-dimensional negative plane its metric and parity action
are both $-I_2$.  This plane is ghost odd, but its parity still preserves the
metric:

\[
 (-I_2)^T(-I_2)(-I_2)=-I_2.
\]

“Ghost odd” means parity eigenvalue (-1); it does not mean anti-Krein.
Symmetric powers inherited from public ghost parity remain isometries on every
invariant nondegenerate subspace.  The selected sector is also exactly charge
neutral, so charge compatibility supplies no additional sign.

The public carrier exists, but the nonlinear $R_t$ dynamics has not been
shown to excite it with the required coefficient.  Carrier existence is not
dynamical production.

## Remaining physical gate

Regular same-carrier parity and inherited public higher-composite parity are
now closed.  The next calculation must introduce genuinely new amplitude
data: the first nonfactorizing crossed $3\to3$ six-point pre-trace block on
the complete 220-tree external-mass jet.  It must be computed before the
coherent $R_+$ collapse and before orientation factorization, retaining:

- both crossed incoming/outgoing assignments;
- the parent constant/linear jet;
- singleton/pair spectator profiles;
- the common tree phase and generalized-Born sharp.

If that block vanishes or retains the same negative quotient, the first twelve
reversed histories are obstructed on the available regular architecture.  If
it supplies a positive full-rank block, it must then be affiliated with all
twelve histories.

## Claim boundary

This result does not rule out singular charts, discontinuous spectator
control, a new doubled cross-paired carrier, an off-diagonal Krein-skew
dynamical coupling, or a nonfactorizing crossed amplitude.  It does not
construct crossed probability, the twelve reversed intertwiners, the 300
seven-point crossed sheets, a Møller/LSZ/$S$ operator, Eq. (19), beyond-tree
positivity, a gravity/BRST lift, anything `LORENTZIAN-CAUSAL`, a new physical
dimension, or literature priority.

## Verification

```bash
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_profile_selective_parity_obstruction.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_profile_selective_parity_obstruction.py
mkdir -p reverse_physics/.tmp_crossed_profile_tests
ulimit -v 500000; TMPDIR=/home/alstrup/area9/weyl-gravity/reverse_physics/.tmp_crossed_profile_tests /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_profile_selective_parity_obstruction
find reverse_physics/.tmp_crossed_profile_tests -depth -delete
```

| Tier | Check | Result | Elapsed |
|---|---|---:|---:|
| 0 | Python compile and JSON parse | PASS | under 1 s |
| 1 | producer, 33 exact checks | PASS | 1.1 s |
| 1 | independent verifier, 33 checks | PASS | 1.0 s |
| 1 | 23-test mutation suite | PASS | 11.6 s |
| 1 | Paper V, two sequential `pdflatex` passes | PASS | 3.1 s total |
| 1 | Paper VI, two sequential `pdflatex` passes | PASS | 2.9 s total |
| affected planning rail | Science Forge import, 1443 nodes, zero invalid items or malformed events | PASS | 11.0 s |
| 2 | unchanged predecessor chain re-read and pinned by hashes | PASS | included above |
| 3 | not run: no freeze, lifecycle promotion, shared-core change, or release | NOT APPLICABLE | -- |
