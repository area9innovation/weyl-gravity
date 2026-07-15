# Final covariant claim dependency report

This report is generated from the atomic certificates. Each derived claim
uses its displayed all/any dependency mode.

## Dependency flow

```mermaid
flowchart TD
  A[curved_operator_identity] --> F[final_covariant_H4]
  E[exact curved first-order E/B system] --> F
  S[sourced constraints and E/A/L audit] --> F
  P[all-row support-local prolongation] --> F
  G[prolonged witness and causal Green homotopy] --> F
  T[endpoint, SO(4,2), and pairing transport] --> F
  R[curved_deformation_retract] --> F[final_covariant_H4]
  C[curved_current_comparison] --> F
```

## Theorem boundary

| Curved lemma | Status | Direct requirements |
| --- | --- | --- |
| `curved_operator_identity` | **true** | `curved_hessian_expanded`, `curved_companion_expanded`, `curved_Q_nilpotency`, `curved_witness_identity`, `curved_formal_adjointness`, `curved_globalization_coverage` |
| `curved_deformation_retract` | **true** | `support_preserving_retract` |
| `curved_current_comparison` | **true** | `curved_auxiliary_shift_is_BV_canonical`, `exact_action_Fourier_current_improvement`, `curved_auxiliary_presymplectic_potential`, `curved_metric_presymplectic_potential`, `curved_cauchy_boundary_current`, `curved_auxiliary_metric_current_identity`, `EAL_pairing_regression` |

## Final claims

| Claim | Status | Requires |
| --- | --- | --- |
| `complete_bv_green_hyperbolicity` | **false** | `curved_auxiliary_hessian_exact`, `support_preserving_retract`, `curvature_green_realization`, `curved_Q_nilpotency`, `curved_witness_identity`, `curved_formal_adjointness` |
| `support_preserving_metric_equivalence` | **true** | `curved_deformation_retract`, `support_preservation` |
| `pairing_compatibility` | **false** | `curved_current_comparison`, `green_homotopies`, `curved_green_current`, `EAL_pairing_regression` |
| `causal_quasi_isomorphism` | **false** |  |
| `CKV_recovery` | **false** | `green_homotopies`, `ckv_cutoff_identity` |
| `residual_no_duplication` | **false** | `support_preserving_metric_equivalence`, `CKV_recovery`, `algebraic_residual_no_duplication` |
| `energy_H4_is_C2` | **true** | `residual_H4_is_C2` |
| `energy_gram_is_I2` | **true** | `residual_gram_is_I2` |
| `residual_H4_is_C2` | **true** |  |
| `residual_gram_is_I2` | **true** |  |
| `final_covariant_H4` | **false** | `curved_operator_identity`, `curved_deformation_retract`, `curved_current_comparison`, `scalar_wave_witness_no_go`, `weyl_symbol_helicity_isomorphism`, `curved_EB_equations`, `curved_EB_first_order_closure`, `curved_EB_symmetric_hyperbolicity`, `curved_sourced_constraint_identity`, `curved_constraint_propagation`, `EAL_curvature_spectrum_match`, `support_local_prolongation_retract`, `prolonged_BV_operator_identity`, `prolonged_green_witness`, `curvature_causal_green_operators`, `causal_green_homotopy`, `causal_quasi_isomorphism`, `residual_endpoint_recovery`, `SO42_equivariant_transport`, `prolonged_current_comparison`, `residual_H4_is_C2`, `residual_gram_is_I2` |

## Implemented scaffold

- `curved_auxiliary_hessian_exact` — The complete action-derived curved Hessian table is exact, formally adjoint, and has 630/630 high-order jet coverage.
- `physical_symbol_quotient_exact` — The normalized Hessian image modulo the gauge image is exactly two-dimensional.
- `physical_symbol_is_helicity_two` — The two quotient directions are the real helicity-two pair transverse to the null direction.
- `weyl_symbol_helicity_isomorphism` — On the exact Hessian-reduced physical quotient, the linearized Weyl symbol is an isomorphism onto the two helicity-two curvature directions.
- `curved_EB_equations` — The complete curved Weyl/Cotton and Bach equations agree on all 150 independent Weyl two-jets and globalize by cylinder homogeneity.
- `curved_EB_first_order_closure` — The ten Weyl E/B components plus the sixteen-component Cotton divergence form an exact local 26-state first-order closure with 34 covariant rows and eight constraints.
- `curved_EB_symmetric_hyperbolicity` — The constraint-adjusted 26-state system is formally integrable-equivalent to the exact covariant rows and has a positive symmetrizer with causal characteristics.
- `curved_sourced_constraint_identity` — The curvature-corrected sourced subsidiary identity and its six compatible-source rows are exact.
- `curved_constraint_propagation` — All fourteen primary and secondary constraints propagate in a causal symmetric-hyperbolic subsidiary system for compatible sources.
- `EAL_curvature_spectrum_match` — The exact covariant Weyl--Cotton equations carry precisely the parity-complete E, A, and L towers at every energy; symbolic BGG rank and character identities prove exhaustion and the Cotton graph adds no modes.
- `support_local_prolongation_retract` — The corrected curved p_E/p_I attachments and their cotangent lifts give a finite-order support-local mapping-cylinder SDR on all sixteen BV blocks.
- `prolonged_BV_operator_identity` — The complete sixteen-block fibre-identified mapping cylinder is coefficientwise nilpotent, odd cyclic, and satisfies PI=1 and IP-1=QH+HQ; the old rank-four Rees defect used the wrong flat-Fourier cotangent projection.
- `candidate_curvature_principal_symmetric_hyperbolicity` — The legacy candidate electric/magnetic Weyl principal block has a positive symmetrizer and the two physical characteristic speeds in each direction. This certificate alone is principal-symbol evidence; the exact curved derivation is certified separately by the curved E/B, first-order, sourced-constraint, and propagation nodes.
- `candidate_curvature_principal_constraints_propagate` — The principal divergence constraints close through div(curl_2 h)=(1/2)curl_1(div h).
- `support_preservation` — The displayed finite differential and pointwise maps do not enlarge support.
- `green_witness_recognition_theorem` — Formal Green consequences hold once the curved witness hypotheses hold.
- `compact_cylinder_spacelike_support` — On R x S^3 every smooth section is spacelike compact.
- `EAL_pairing_regression` — The reduced physical current has the certified +E,-A,-L normalization.
- `ckv_cutoff_identity` — The cutoff-source identity recovers all fifteen modes once Lambda exists.
- `algebraic_residual_no_duplication` — The algebraic BFV replacement contains one ghost and one momentum copy.
- `residual_H4_is_C2` — The completed energy-mode centered cohomology is the certified two-class space.
- `residual_gram_is_I2` — The completed energy-mode cohomological Gram matrix is I_2.
- `curved_action_and_gauge_map` — The exact covariant action and its curved 24-by-9 gauge map are instantiated.
- `parallel_curvature_derivative_normal_form` — Covariant derivative words reduce canonically using the parallel cylinder curvature.
- `curved_auxiliary_shift_is_BV_canonical` — The nonlinear completion-of-square shift has its exact local cotangent lift.
- `universal_post_shift_auxiliary_SDR` — The universal 36-dimensional shifted auxiliary cotangent summand contracts exactly.
- `exact_action_Fourier_current_improvement` — The action-level Fourier currents differ by an explicit antisymmetric improvement.
- `support_preserving_retract` — The complete all-row curved SDR is local and support preserving, independently of the Green realization.

## Remaining curvature-propagation theorem

The selected final gate is the constrained symmetric-hyperbolic
Weyl-curvature realization. The reduced Weyl-symbol theorem, the
exact curved equations, and the 26-state first-order closure are
true. The remaining analytic, causal, endpoint, equivariance, and
pairing-transport flags below remain open.

- `prolonged_green_witness` — The complete sixteen-block prolonged differential and its local graph SDR are exact.  Fourteen analytic Green blocks and the restricted physical biwave extension are certified, but the relative rank-14 equation-cone Green contraction is still missing.  The complete 421-variable two-factor PBW system and its order-two Schur projection are exact; the 214-parameter action-adjoint branch has an exact rank-52/100 order-two Schur gate with 1,050 projected constraints.  Its 179 independent quadratics have no nonzero affine-linear consequence.  The exact degree-one Macaulay matrix has 136,585 rows and 20,585 multiplier columns; its degree-three rational rank is rigorously bounded between 12,861 and 14,136, but the full rational ranks and constant-ideal question remain undecided.  The expanded relative route has a projector-free rank-14 principal presentation and same-sided Green algebra.  Its raw curvature map has rank five and kernel rank nine, while the compatible Weyl--Cotton source kernel has rank twelve; the generic off-shell compatibility defect has rank three, so the proposed K12/I5 quotient is not defined.  The corrected curved p_E/p_I maps prove the operator chain squares, but do not yet compute the relative equation-cone cohomology or its causal inverse.
- `curvature_causal_green_operators` — Construct retarded and advanced operators for the exact constrained curvature system and assemble the full BV blocks.
- `causal_green_homotopy` — Verify Q Lambda_+/- + Lambda_+/- Q=1 on the complete prolonged BV complex with causal support.
- `causal_quasi_isomorphism` — Prove that the causal map Gamma_c(C_prol)[1] -> Gamma_sc(C_prol) is a quasi-isomorphism and specialize it to all smooth cylinder solutions.
- `residual_endpoint_recovery` — Realize the fifteen cutoff CKV classes and their dual endpoints through the actual causal map, with no prolongation copy and suspension sign +1.
- `SO42_equivariant_transport` — Prove that the causal/Cauchy identification transfers the full SO(4,2) action, strictly or by an explicit chain homotopy.
- `prolonged_current_comparison` — The cyclic quadratic-parent formula is well typed for the corrected mapping cylinder, but the current certificate must explicitly bind the corrected curved core-chain digest before promotion.

> The algebraic and energy-mode result is independently certified:
> `H^4 = C^2` with Gram matrix `I_2`. This report tracks its
> still-open covariant transport.
