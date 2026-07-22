# Phase-2 dyonic flat-family preflight

Date: 2026-07-22  
Agent: `phase2-sign-1`  
Work item: `sf:program/work/phase2-sign-dyonic-flat-family-preflight`

## Disposition

The exact local coupling-background family exists, but it is obstructed as the
proposed stationary fixed-bundle positive-frequency base.

At $k_1=0$, fixed nonzero magnetic Chern number $N$, and
$\tau=E/P$, exact elimination gives

\[
 \beta=\frac{\kappa N^2}{4q_{\min}^2},\qquad
 k_2=\frac{1}{\beta(1+\tau^2)},
\]

\[
 P=\frac{2q_{\min}}{N\kappa(1+\tau^2)},\qquad
 E=\tau P,
\]

\[
 \alpha_B=\alpha_{\rm crit}(1+\tau^2),\qquad
 \alpha_{\rm crit}=\frac{3N^2}{4q_{\min}^2}.
\]

This varies the coupling and the background together. It is not an open
background family inside one fixed-$\alpha_B$ theory.

## Global connection obstruction

On north and south monopole patches the connection may be written

\[
 A_N=Et\,dx+\frac{P}{k_2}(1-\cos\theta)d\phi,
 \qquad
 A_S=Et\,dx-\frac{P}{k_2}(1+\cos\theta)d\phi,
\]

with

\[
 A_N-A_S=\frac{N}{q_{\min}}d\phi.
\]

The metric and field strength are invariant under $H=\partial_t$, but

\[
 \mathcal L_H A=E\,dx.
\]

For a single-valued infinitesimal gauge parameter,
$\int_{S^1}d\chi=0$, whereas
$\int_{S^1}E\,dx=EL\neq0$ when $E\neq0$. Therefore $H$ has no
continuous global lift stabilizing the connection. Equivalently, the spatial
Wilson loop evolves as

\[
 W_x(t)=\exp(iq_{\min}ELt)W_x(0).
\]

Large gauge transformations compensate only isolated time shifts and do not
supply the missing infinitesimal stabilizer. At the pure-magnetic endpoint
$\tau=0$, the obstruction vanishes.

The surviving exact lifts are $P_x=\partial_x$ with zero compensator and the
standard monopole $SO(3)$ lifts

\[
 \chi_i=-\iota_{J_i}A_{N/S}-\frac{P}{k_2}n_i,
 \qquad
 \iota_{J_i}F=\frac{P}{k_2}dn_i.
\]

## Parity and duality

Spherical antipodal parity acts on the charge vector as

\[
 (E,P)^T\mapsto(E,-P)^T.
\]

An equation-level Maxwell duality rotation can be chosen so that its product
with parity fixes the dyonic background. The resulting involution is

\[
 J_\tau=\frac1{1+\tau^2}
 \begin{pmatrix}
 \tau^2-1&2\tau\\
 2\tau&1-\tau^2
 \end{pmatrix},
 \qquad J_\tau^2=1,
 \qquad J_\tau(\tau,1)^T=(\tau,1)^T.
\]

It is not an allowed symmetry of the declared fixed-Chern tangent carrier:

\[
 J_\tau(\delta E,0)^T
 =\left(\frac{\tau^2-1}{1+\tau^2}\delta E,
 \frac{2\tau}{1+\tau^2}\delta E\right)^T.
\]

For generic $\tau\neq0$, it creates a forbidden magnetic-Chern tangent.
Moreover the continuous duality rotation is an equation/stress-tensor
symmetry, not a local off-shell symmetry of the declared single-potential
fixed-bundle action. Hence no inherited axial/polar block split is authorized;
any continuation must use a combined mixed-parity carrier.

## Scope and next choices

No tangent cofiber, dispersion relation, Lee--Wald current, inertia, or sign
wall was computed. The exact obstruction leaves three genuinely changed
successor scopes:

1. a duality-covariant two-potential/global charge-lattice formulation;
2. a noncompact spatial direction with an explicit boundary policy permitting
   the electric compensator;
3. a compact but nonstationary mixed-parity formulation, without claiming
   positive-frequency continuation from Phase 1.

## Evidence

- Certificate: `bridge/phase2/dyonic_flat_family_preflight/DYONIC_FLAT_FAMILY_PREFLIGHT_V1.json`
- Independent verifier: `bridge/phase2/dyonic_flat_family_preflight/verify.py`
- Tier receipt: `bridge/phase2/dyonic_flat_family_preflight/DYONIC_FLAT_FAMILY_PREFLIGHT_V1_TIER_RECEIPT.json`
- Atlas: `residual_atlas/phase2-sign-dyonic-flat-family-preflight-fragment-v1.json`

Tier 0 and Tier 1 pass. Tier 2 was not run because the imported mathematical
inputs are unchanged and pinned by exact hashes. Tier 3 was not run because
this is a scoped background/symmetry obstruction, not a release or theorem
promotion.

CLOSE-OUT: OBSTRUCTED — the exact coupling-background family exists, but for tau!=0 it has neither a continuous global H lift on the compact fixed bundle nor an allowed parity-duality symmetry preserving the fixed-Chern tangent carrier
EVIDENCE: bridge/phase2/dyonic_flat_family_preflight/DYONIC_FLAT_FAMILY_PREFLIGHT_V1_TIER_RECEIPT.json
