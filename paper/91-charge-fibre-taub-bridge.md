# Charge fibres and Taub obstructions in compact Einstein--Maxwell gravity

*Bridge note for mathematical relativity and linearization-stability
researchers. Status: draft allowed, 17 July 2026.*

## 1. Their object and the unresolved question

Linearization stability asks whether every solution of the linearized field
equations is tangent to an actual family of exact solutions. On compact Cauchy
surfaces with symmetries, quadratic Taub constraints can obstruct such an
extension. The modern genericity result of Saraykar and Rai places this in the
class of constant-mean-curvature spacetimes with compact Cauchy hypersurfaces
([arXiv:1609.07703](https://arxiv.org/abs/1609.07703)); it builds on the
Fischer--Marsden--Moncrief tradition.

Our adjacent question is whether the obstruction depends on the **global
charge fibre**: is a tangent obstructed on a fixed $U(1)$ bundle but
extendible when electric or magnetic flux is admitted as part of the family?

```text
                         quadratic source
H^0_lin x H^0_lin  ---------------------------->  coker L
       |                                                |
       | fixed bundle: charge row unavailable           | Taub pairing
       | enlarged flux family: new charge direction     | may be absorbed
       +------------------------------------------------+
```

## 2. Exact dictionary

| Item | Linearization-stability language | This project | Conversion or caveat |
|---|---|---|---|
| Background | Einstein or Einstein--matter solution | compact $\mathbb R\times S^1\times S^2$ Einstein--Maxwell product | It is simultaneously a tuned Weyl--Maxwell background. |
| Linear tangent | kernel of the linearized equations modulo gauge | standard photon/graviton harmonics and extra Weyl classes | The present bilinear is before the final residual quotient. |
| Quadratic constraint | Taub charge paired with a Killing initial datum | constant-lapse component of $D^2E[\Phi_1,\Phi_1]$ | Other adjoint-cokernel classes remain to be classified. |
| Global sector | fixed conserved charges | fixed Chern class $P_N$, with electric variation tracked separately | A continuous magnetic variation changes the bundle family. |
| Extension | solution of $L\Phi_2=-\tfrac12D^2E[\Phi_1,\Phi_1]$ | explicit correction or normalized adjoint witness | A removable output block is not proof that the real tangent extends. |
| Pairing | constraint/cokernel pairing | relative Taub form $\mathfrak O$ | Exact algebraic arithmetic is used. |

## 3. Reproduced benchmark

The compact topology fixes the magnetic sector. On the rational fixture the
bundle number expands as

\[
N(\epsilon)=2+2\epsilon^2p.
\]

A smooth family on the same $N=2$ bundle therefore has $p=0$. The
constant-lapse Taub component cannot be removed by silently varying magnetic
flux. On the declared four-dimensional fixture span—radion, duality,
$\ell=1$ photon, and plus-branch $\ell=2$ graviton—the symmetric form is

\[
\operatorname{diag}\!\left(-2,-\frac12,-\frac{16}{3},
-\frac{72}{5}-12\sqrt3\right).
\]

Gauge descent and Cauchy-slice conservation follow from the coupled action
Noether identities. The benchmark is independently replayed by:

```bash
python3 -m bridge.einstein_sector.compact_harmonic_domain_taub_descent \
  --verify bridge/certificates/compact_harmonic_domain_taub_descent.json
python3 bridge/einstein_sector/verify_compact_harmonic_domain_taub_descent.py
```

## 4. Added result

> **Scoped charge-fibre obstruction.** On the declared compact fixed bundle,
> several physical photon, graviton, and extra-Weyl tangents have nonzero
> second-order Taub pairings and therefore no smooth periodic second-order
> correction. Allowing a formal magnetic coefficient can remove specified
> constant-lapse components, but that coefficient belongs to an enlarged
> flux family, not the original fixed-bundle phase space.

The most recent real test uses the degenerate axial--polar
$\ell=2,k=0$ minus-frequency Einstein pair. Its Hermitian Taub form is
positive definite, so every nonzero real combination is obstructed at fixed
bundle topology. A separate axial--polar sum-frequency source has an exact
correction; it does not remove the zero-frequency constraint arising from
conjugate self-products. Thus source solvability must be checked in every
selection channel before declaring extension.

## 5. Consequence in their language

The result promotes “hold the charge fixed” from an informal side condition
to part of the domain of the obstruction map. It suggests that linearization
stability for gauge--gravity systems should be indexed by a charge fibre—or a
stratum of the global bundle moduli—before genericity is discussed. The same
linear tangent can have different integrability status in different enlarged
families without contradiction.

## 6. Scope boundary

This is `LOCAL-ALGEBRAIC/REDUCED-MODE`, not a causal nonlinear evolution
theorem. The complete harmonic obstruction bilinear, all equal-quantum-number
polarization blocks, the full adjoint cokernel, charge-relaxed corrections,
and final residual quotient remain open. No asymptotic, scattering, or quantum
claim follows. The result is a family of exact obstructions, not yet a theorem
that the entire Einstein sector fails nonlinearly.

## 7. One useful question for adjacent experts

> Should the fixed-versus-variable flux distinction be formulated as
> linearization stability on separate connected components of configuration
> space, as a stratified moment-map problem, or as an enlarged constraint
> operator with additional global rows? Which formulation best preserves the
> classical Taub theorem when the underlying principal bundle changes?

## Reproducibility receipt

```text
source paper: arXiv:1609.07703v1 and its cited classical framework
project certificates: COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT;
  EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1;
  EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB
verification: section 3 plus certificate-local commands
dependency tags: LOCAL-ALGEBRAIC; REDUCED-MODE
generality level: G1_DECLARED_COMPACT_HARMONIC_DOMAIN
lifecycle state: DRAFT_ALLOWED
claim flag: CHARGE_FIBRE_DEPENDENT_TAUB_OBSTRUCTIONS_CERTIFIED
open fields: all-harmonic bilinear; full cokernel; charge-relaxed extensions
```
