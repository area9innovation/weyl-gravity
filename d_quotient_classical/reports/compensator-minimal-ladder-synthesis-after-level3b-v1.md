# Minimal compensator ladder after convention-correct Level 3b

## Result

The complete declared minimal ladder has no selected action:

\[
\boxed{
\mathcal L_{\mathrm{minimal,\ declared}}^{\mathrm{good}}
=\varnothing .
}
\]

This is a theorem about an explicitly printed union of action families, not
about all compensator or scalar-tensor theories.

The machine result hash-imports fifteen authoritative artifacts and uses every
one in the table:

```text
d_quotient_classical/compensator/
COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json
```

## Exact action and background ledger

### Passive tau-adic strict action

```text
action:
  S_W = alpha_C integral sqrt(-g) C(g)^2
  tau enlarges the formal BV/Wess-Zumino algebra only
  no classical dressed-trace kinetic and no new gauge generator

background:
  g_bar = -dt^2 + dOmega_3^2
  tau_bar = 0
  closed S3 Cauchy surfaces
```

### Candidate A: tuned \(R^2\) auxiliary scalar

```text
action:
  integral sqrt(-g_hat)[
    alpha_B C^2/8
    + chi R - chi^2/(4 beta)
    + R/12 - 1/4
    - (nabla theta)^2/2
  ]
  beta = -1/144
  chi_bar = -1/12

background:
  unit cylinder, R=6, theta constant
  the frozen positive Berger fixture is a different action
```

### Candidate B: minimal HT three-form

```text
action:
  S_base + integral lambda_HT(vol_g_hat - dA3)
  small reducible A3 gauge tower
  no fixed-flux sector and no large/global quotient

backgrounds:
  unit cylinder, A3_bar=t vol_S3, theta constant
  frozen Berger a=1, q=9/40, theta=3t/4
```

### Complete minimal formal-polar family

```text
action:
  integral vol_g_hat[
    alpha_B C^2/8 + alpha_R R^2
    + M_P^2 R/2
    - Z_theta (nabla theta)^2/2 - V0
    + alpha_E E4
  ]
  optionally plus the normalized minimal HT sector

backgrounds:
  unit cylinder with theta constant
  frozen Berger a=1, q=9/40, theta=3t/4
```

### Active clock \(P_2(X)\)

```text
action:
  integral vol_g_hat[
    alpha_B C^2/8 + alpha_R R^2 + M_P^2 R/2
    + p0 + p1 X + p2 X^2 + alpha_E E4
  ]
  X=(nabla theta)^2

backgrounds:
  unit cylinder with theta constant
  Berger a=1, q=9/40, theta=3t/4
  exact stability box:
    15/16 < kappa < 17/16
    1/5 < q < 1/4
    2/3 < nu < 5/6
```

At the frozen point the exact common stationary ray is

\[
t\left(
\frac{81}{20},
\frac{27}{3290},
-\frac{324}{1645},
\frac{486}{1645},
\frac{18}{25},
1
\right).
\]

### Level 2: first nonexact kinetic braiding

```text
action:
  S_P2 + beta integral sqrt(-g_hat) X Box_hat(theta)

backgrounds:
  constant-clock unit cylinder
  Berger a=1, q=9/40, theta=3t/4
```

The constant \(g_0\Box\theta\) term is horizontally exact. Thus this is the
complete degree-one polynomial \(G(X)\) family after quotienting the boundary
term.

### Level 3 literal \(+F_X\)

```text
action:
  S_P2 + integral sqrt(-g_hat){
    F(X) R_hat
    + F_X[(Box_hat theta)^2-(nabla_hat nabla_hat theta)^2]
  }
  F=f0+f1 X

background:
  active-clock homogeneous ADM fixture
  f1=0 imports the failed P2 cylinder/Berger family
```

### Level 3b convention-correct \(-2F_X\)

```text
action:
  S_P2 + integral sqrt(-g_hat){
    F(X) R_hat
    - 2 F_X[(Box_hat theta)^2-(nabla_hat nabla_hat theta)^2]
  }
  F=f0+f1 X

background:
  constant-clock unit cylinder
  no Berger sample is required after the complete cylinder separator
```

### Level 4 minimal real Weyl connection

```text
action:
  integral sqrt(-g){
    alpha_C C^2/8
    + alpha_0 R_W^2
    + alpha_2 Ricci_W,TF^2
    - zeta F_W^2/4
    - kappa_r (D_W rho)^2/2
    - kappa_R rho^2 R_W/12
    - kappa_theta rho^2(nabla theta)^2/2
    - lambda rho^4/4
  }

background:
  local covariant gauge-rank and Ward gate
  no cylinder or Berger solution is inherited
```

## Theory-space table

Each cell gives the terminal status and its decisive exact reason.

| Declared family | Cylinder stationarity | Berger stationarity | Dressed trace | Reduced scalar inertia | Principal hyperbolicity | Raw \(D\) charge | Clock health | Causal parent |
|---|---|---|---|---|---|---|---|---|
| Passive tau-adic strict action | PASS: strict cylinder is Bach-flat | NOT COMPUTED | FAIL: arbitrary compact-support \(u\) class | DEGENERATE: trace Hessian zero | FAIL: no trace Green inverse | Compatible but does not remove homology | N/A | OBSTRUCTED |
| Candidate A tuned \(R^2\) | PASS: \(F(6)=F'(6)=0\) | FAIL: frozen positive Berger fixture is a different action | Physical scalar replacement | FAIL: eigenvalues \((-3,+3)\) | Reduced inverse only; full health fails | FAIL: witnesses \(+3,-3\) | FAIL: no same-action Berger clock | SUPERSEDED: historical rank-390 direct sum is not valid |
| Candidate B minimal HT | FAIL: trace-free Ricci Euler row survives | FAIL: nonexact \(L_DA_3=\mathrm{vol}_{S^3}\) | FAIL: \(H_c^4/H^3\) data survive | DEGENERATE topological block | FAIL: off shell and polynomial kernel | FAIL: \(\iota_D\Omega=V_{S^3}d\lambda_{\rm HT}\) | FAIL without new quotient | OBSTRUCTED |
| Complete minimal polar plus optional HT | CLASSIFIED: \(M_P^2=-24\alpha_R,\ V_0=-36\alpha_R\) | FAIL common locus | FAIL: trace, split scalar or HT global class | FAIL: split or null | FAIL: only empty bulk vector or HT kernel | FAIL: both signs or non-null HT charge | FAIL | OBSTRUCTED; NEITHER A nor B nor C selected |
| Active \(P_2(X)\) | PASS stationary ray | PASS stationary ray, stable as parameter-dependent family | Physical \(R^2\) replacement | FAIL: immutable \(+3,-3\) pair | Clock cones exist but gravity is split | FAIL: \(+3,-3\) | FAIL: cylinder needs \(t<0\), Berger needs \(t>0\) | NOT REACHED |
| Level-2 braiding | PASS: P2 ray plus beta axis | PASS first variation | FAIL: cylinder braiding Hessian zero | FAIL: zero or split | FAIL: zero cylinder block | FAIL: zero dynamics or inherited \(+3,-3\) | Berger-only visibility cannot repair cylinder | OBSTRUCTED |
| Literal Level 3 \(+F_X\) | FAIL degeneracy: \(\det H=-324X^2F_X^2\) | NOT COMPUTED on novel stratum | NOT REACHED | FAIL: rank-two lapse-acceleration block | FAIL: misses \(B=-2F_X\) | NOT REACHED | NOT REACHED | OBSTRUCTED |
| Correct Level 3b \(-2F_X\) | PASS: complete locus \(M_{P,\rm eff}^2=-24\alpha_R,\ p_0=36\alpha_R\) | Not needed after empty cylinder physical locus | FAIL: split auxiliary or surviving trace class | FAIL: \(\operatorname{diag}(-6,6)\) on \(\alpha_R\ne0\) | Horndeski-degenerate but physically unhealthy | FAIL: \(+3,-3\) or no trace generator | Tunable clock symbol cannot repair metric block | OBSTRUCTED |
| Minimal real Weyl connection | NOT COMPUTED after rank/charge separator | NOT COMPUTED | FAIL: dependent trace column or zero phase row | FAIL: \(\kappa_\theta=0\) on independent stratum | FAIL: zero phase principal row | FAIL: phase charge requires reducible stratum | FAIL: no common trace gauge and phase clock | OBSTRUCTED |

## Convention reconciliation

The project convention is

\[
X=\widehat g^{ab}\partial_a\theta\partial_b\theta.
\]

For

\[
F(X)R+B\left[(\Box\theta)^2-(\nabla\nabla\theta)^2\right],
\]

the exact homogeneous velocity determinant is

\[
-36X^2(B+2F_X)^2.
\]

Therefore:

\[
B=+F_X
\quad\Longrightarrow\quad
\det H=-324X^2F_X^2,
\]

whereas

\[
B=-2F_X
\quad\Longrightarrow\quad
\det H=0.
\]

The literal Level-3 theorem remains valid for its printed action. It is not
rewritten as the convention-correct Horndeski result. Level 3b is a separate
action theorem: it passes degeneracy, then fails because its complete cylinder
locus has either split \(R^2\) inertia or surviving dressed-trace homology.

## Superseded causal claim

The earlier changed-action certificate printed a complete rank-390 direct-sum
causal parent. Candidate A later derived the missing non-Einstein
metric--auxiliary rows

\[
L_{ab}\psi
=
(\nabla_a\nabla_b-g_{ab}\Box-R_{ab})\psi .
\]

Thus the complete direct-sum promotion and the claim of zero strict-complement
change are superseded. The following narrower results remain valid:

* the rational double-root tuning;
* the trace Schur complement
  \[
  H_u=-\frac18(\Box+2)^2;
  \]
* its iterated reduced scalar Green inverse;
* the independent phase wave block.

The synthesis records this as `SUPERSEDED`, not `CERTIFIED`.

## Exact exhausted union

The theorem covers exactly

\[
\begin{aligned}
\mathcal U_{\rm tested}
={}&
\mathcal T_{\rm passive}
\cup
\mathcal M_{\rm polar}^{(4\,{\rm metric},2\,{\rm scalar}),\,{\rm small\,HT}}
\\
&\cup
\mathcal P_{\deg\le2}
\cup
(\mathcal P_{\deg\le2}+\mathcal G_{\deg\le1})
\\
&\cup
\mathcal L_{3}^{F_{\deg\le1},+F_X}
\cup
\mathcal L_{3b}^{F_{\deg\le1},-2F_X}
\cup
\mathcal L_{4}^{\rm real\ Weyl,\ minimal}.
\end{aligned}
\]

The exhaustiveness statements are internal to each declared component:

* the minimal polar row exhausts the parity-even four-metric/two-scalar
  derivative basis plus the normalized small-gauge HT option;
* \(P(X)\) is complete through degree two;
* \(\beta X\Box\theta\) is the complete first nonexact polynomial braiding
  family;
* both curvature rows exhaust linear \(F=f_0+f_1X\) at their separately
  printed coefficients;
* the real-connection row exhausts the lowest-order parity-even invariants
  under its reality and representation assumptions.

This is a union of separately tested action families. It is not closure under
arbitrary hybrids.

## Genuinely untested mechanisms

The first open mechanisms are:

1. a separated real scale connection and compact internal \(U(1)\) connection
   charging \(\theta\);
2. simultaneous nonzero braiding and Horndeski curvature coupling;
3. higher \(G(X)\);
4. nonlinear \(F(X)\), \(G_5\), and general DHOST classes;
5. extra compensators or other matter fields;
6. fixed-flux sectors and large/global three-form quotients;
7. other backgrounds and fixed-charge reductions;
8. general metric-affine or complex gauge geometry.

## Smallest representation-level escape

The next gate is a preflight for

\[
\boxed{
\mathbb R_{\rm scale}\times U(1)_{\rm phase}
}
\]

with separate real connections on one complex compensator. The scale generator
can act on the radial/dressed-trace direction while the compact generator acts
additively on \(\theta\). This removes the specific Level-4 implication

\[
\Delta\kappa_\theta=0
\]

that tied an independent trace gauge direction to a zero phase Hessian.

This is only the smallest representation-level escape to test. It is not a
selected action or evidence that the escape succeeds.

## Claim boundary

The result establishes only that every separately declared component of
\(\mathcal U_{\rm tested}\) has empty good locus under its printed background,
charge, gauge and derivative assumptions.

It does not exclude all compensator, scalar-tensor, Horndeski, DHOST,
metric-affine, complex-connection, fixed-flux or changed-background theories.
It establishes no nonlinear \(q_2\), Hadamard state, anomaly/QME theorem,
particle space, scattering, positivity or unitarity result.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — the exact declared minimal ladder is exhausted without a
selected action; the separated scale/\(U(1)\) representation is activated only
as the next preflight.
