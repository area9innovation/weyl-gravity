# BT crossed Wightman-dual no-go

Certificate: `REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1`

Lifecycle: `CLASSIFIED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The incoming/outgoing Wightman dual does not generate the internal
dual-number parity needed to repair the reversed six-point quotient.
Momentum reflection exchanges positive- and negative-energy support, but it
acts as the identity on the simple/dipole mass jet.  Imposing the missing
parity as a universal one-particle crossing rule would also spoil the already
positive first crossed $5\to4$ splitting.

The missing six-point sign must therefore be profile-selective, come from a
higher composite or doubled carrier, or be replaced by a nonfactorizing
crossed $3\to3$ pre-trace term.  None of those alternatives is constructed
here.

## Spectral reflection

Use the massive spectral families

\[
 W_\mu^+(p)=\theta(p^0)\delta(p^2-\mu),\qquad
 W_\mu^-(p)=\theta(-p^0)\delta(p^2-\mu).
\]

With the BT dipole convention,

\[
 W_{\rm dip}^{\pm}
 =-\left.\partial_\mu W_\mu^{\pm}\right|_{\mu=0}
 =\theta(\pm p^0)\delta'(p^2).
\]

Reflection $C:p\mapsto-p$ sends $W_\mu^+$ to $W_\mu^-$.  It is
independent of $\mu$, hence

\[
 C_*W_{\rm dip}^+
 =-\left.\partial_\mu(C_*W_\mu^+)\right|_{\mu=0}
 =W_{\rm dip}^-.
\]

Thus, in the simple/dipole basis, the induced jet map is

\[
 C_{\rm jet}=I_2,
 \qquad C_{\rm jet}^TJC_{\rm jet}=J,
 \qquad J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

No oriented Jacobian sign is available: distributional pushforward uses

\[
 |\det(-I_4)|=1.
\]

This is an identity of parameterized tempered distributions after smearing.
It is not a construction of the interacting incoming rigged state or an LSZ
crossing theorem.

## The first crossed split is already positive

On the spacelike sheet write $\tau=-x$, with $x>0$.  For positive
$a_0,a_1$, $a_0\ne a_1$, define

\[
 q_x=\frac{2x(a_0+a_1)+(a_0-a_1)^2}{2x^2}>0,
 \qquad
 \ell_x=\frac{(a_0-a_1)^2}{2x}>0.
\]

Crossing the certified five-to-four amplitude-level operator gives

\[
 T_x=\operatorname{diag}(-q_x,\ell_x),
 \qquad
 T_x^\sharp=JT_x^TJ=\operatorname{diag}(\ell_x,-q_x).
\]

Consequently

\[
 T_x^\sharp T_x=-\rho_xI_2,
 \qquad
 \rho_x=q_x\ell_x>0.
\]

The five external delta-prime measures retain their odd sign after crossing.
Multiplying by that sign gives the physical Gram

\[
 -T_x^\sharp T_x=+\rho_xI_2.
\]

The first crossed splitting is therefore positive and full rank with the
identity Wightman dual.

## Why a universal parity is impossible

The six-point quotient would be repaired algebraically by

\[
 S_\epsilon=\operatorname{diag}(1,-1),
 \qquad S_\epsilon^TJS_\epsilon=-J.
\]

If this were a universal incoming one-particle rule, it would also act on the
first crossed operator:

\[
 T_xS_\epsilon=\operatorname{diag}(-q_x,-\ell_x).
\]

Its unsigned $J$-Gram is now $+\rho_xI_2$.  The unchanged fifth
delta-prime sign turns the physical Gram into

\[
 -\rho_xI_2,
\]

destroying the healthy first crossed splitting.  The sign repair needed at
the second coherent collapse cannot be a common incoming Wightman-reflection
law.  In particular, it cannot be attached independently to every crossed
one-particle leg.

## Remaining physical gate

The smallest surviving possibility must satisfy two incompatible-looking
local requirements in a larger carrier:

1. act as the identity on the first crossed $T_x$ block;
2. act as $\operatorname{diag}(I_2,-I_2)$ only at the second parent/profile
   collapse.

That action needs an explicit higher-composite, doubled, or profile-selective
BT source and must respect the public charge and ghost-parity constraints.  If
the public algebra supplies no such operator, the next calculation is the
first nonfactorizing crossed $3\to3$ pre-trace term.

## Claim boundary

This certificate does not establish a complete interacting Wightman domain,
a dipole LSZ crossing theorem, a positive crossed six-point probability, any
of the twelve reversed physical intertwiners, the remaining seven-point and
spectator sheets, a spacetime Møller or $S$ operator, Eq. (19), beyond-tree
positivity, a metric/BRST lift, anything `LORENTZIAN-CAUSAL`, a new spacetime
dimension, or literature priority.

## Verification

```bash
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_wightman_dual_no_go.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_wightman_dual_no_go.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_wightman_dual_no_go
```

Tier 0 and Tier 1 are applicable.  The affected chain consists of unchanged,
content-addressed predecessor certificates plus this new terminal
certificate.  Tier 3 is not applicable because no freeze, theorem-lifecycle
promotion, shared-core algebra change, or release is being made.

| Tier | Check | Result | Elapsed |
|---|---|---:|---:|
| 0 | Python compile, JSON parse, scoped `git diff --check` | PASS | under 1 s |
| 1 | producer, 27 exact checks | PASS | 1.1 s |
| 1 | independent verifier, 30 checks | PASS | 1.0 s |
| 1 | 21-test mutation suite | PASS | 10.0 s |
| 1 | Paper V, two sequential `pdflatex` passes | PASS | 2.8 s total |
| 1 | Paper VI, two sequential `pdflatex` passes | PASS | 2.8 s total |
| affected planning rail | Science Forge import, 1441 nodes, zero invalid items or malformed events | PASS | 10.9 s |
| 2 | unchanged predecessors checked by pinned hashes and independently re-read by the verifier | PASS | included above |
| 3 | not run: no freeze, lifecycle promotion, shared-core change, or release | NOT APPLICABLE | -- |
