# Einstein--Maxwell/Weyl--Maxwell harmonic sign--resonance join

## Result

The certified all-harmonic current-sign theorem and the complete
finite-harmonic obstruction ledger now form one branch-labelled map:

\[
\mathcal O_{\rm bounded}(u)=
\bigl(\mu_H,\mu_{P_x},\mu_{J_1},\mu_{J_2},\mu_{J_3}\bigr)
\oplus\{P_{j,r}\}
\oplus\{R_{j,a}\}.
\]

The summands have distinct meanings.

- The five `mu` rows are the persistent compact stabilizer cokernel.
- `P_(j,r)` extracts every positive temporal-degree coefficient of the
  quadratic source in output block `j=(L,M,K,Omega,parity)`.
- `R_(j,a)` pairs the source with every exact reduced left-kernel vector on a
  nonzero characteristic `p/q` shell.

Distinct harmonic output labels are direct summands.  The zero-frequency
stabilizer block is excluded from `P` and `R`, and `R` contains only nonzero
shells.  The stationary Lee--Wald form is branch diagonal, so the sign ledger
is an orthogonal occupation sum before the remaining functionals are applied.

On the complete certified finite carrier,

```text
bounded or finite-quasiperiodic correction exists  iff  {mu,P,R}=0;
smooth exponential-polynomial correction exists   iff  mu=0;
causal/retarded correction                         NO_CERTIFIED_MAP.
```

The distinction is structural: positive-degree and resonant sources have
finite secular primitives in the smooth class but not in the bounded class.

## Sign consequences

Every nonzero real finite pure additional-Weyl sum has strictly negative
`mu_H`.  Therefore the pure-extra face of the joined second-order cone is
exactly the origin.  Generic Einstein `q_minus` modes have the opposite sign
in both parities and every `ell>=2`, so mixed moment-map-null directions are
possible.

Two exact independence witnesses prevent replacing the full bounded map by
the five moments:

```text
aligned global--extra tangent:      mu=0, P!=0;
twist-balanced exceptional tangent: mu=0, R!=0.
```

Moment-map cancellation is therefore not bounded solvability.

## Maximal complete mixed bounded carrier

The strongest fully classified carrier supported by the current exact inputs
contains:

- every standard homogeneous, twist and Maxwell global coordinate;
- an arbitrary finite set of generic `ell>=2` blocks at `k=0`;
- every `m`, both parities, both Einstein `q` branches and both
  additional-Weyl `p` multiplicities.

Its bounded common zero is the necessary-and-sufficient union

```text
wave=0:
    a=b=Q_e=B=0; c,d,W_x,A arbitrary;

wave!=0:
    a=b=d=Q_e=B=0; c,W_x,A arbitrary;
    total mu_H=mu_J1=mu_J2=mu_J3=0.
```

At `k=0`, `mu_Px=0` automatically.  Every remaining polynomial or shell
column is either one of the displayed global eliminators, identically zero,
or has a certified bounded inverse.  Cross-`ell` outputs are off shell, and
the finitely many block corrections add.

## Fail-closed remainder

Two complete nonzero-momentum controls are retained without crosswalking
them:

- the candidate-13 two-absolute-momentum all-`m`, both-parity cone is the
  origin;
- the distinct tuned opposite-momentum axisymmetric carrier has two nonzero
  mixed `q_minus` components.

Their circumferences, momentum fibres and phase carriers differ, so there is
`NO_CERTIFIED_MAP` between them.

The first unclassified union is exceptional `ell=1` oscillator input mixed
with generic waves and globals at arbitrary compact momentum, followed by
multiple `|k|` fibres.  The coefficientwise `{mu,P,R}` formula is complete
there, but its common-zero geometry remains `OPEN`.

No infinite-mode completion, all-orders integration, final residual descent,
causal propagation, observable, particle, scattering or quantum-norm theorem
is inferred.

## Evidence

- `bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json`
- atlas row `einstein.ph.wm.mixed.harmonic_sign_resonance_join`
- `bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_WEYL_HARMONIC_SIGN_RESONANCE_JOIN_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: EINSTEIN_MAXWELL_WEYL_HARMONIC_SIGN_RESONANCE_JOIN_V1_TIER_RECEIPT
