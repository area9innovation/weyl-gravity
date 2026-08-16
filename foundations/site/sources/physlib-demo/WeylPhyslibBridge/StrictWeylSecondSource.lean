/-
Copyright (c) 2026 Area9 Innovation. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Authors: Weyl-gravity programme contributors
-/
import Mathlib.Algebra.Module.Defs
import Mathlib.Tactic.NormNum
import Physlib.Meta.Informal.Basic

/-!
# Strict pure-Weyl second-source bridge

This is a deliberately small bridge from the exact certificate
`STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1` into the Physlib/Lean
ecosystem.  It formalizes the final algebraic implication in the certificate:
once the receiver-supplied reduction and diagonal arity-three identity hold,
the second nonlinear source is `q₁`-closed because `1/2 - 3/6 = 0`.

The hypotheses are explicit.  This file does not formalize or replace the
certificate's differential-geometric, causal-support, Green-homotopy, or
microlocal arguments.
-/

namespace WeylPhyslibBridge.StrictWeyl

/-- The authoritative certificate imported by the external provenance check. -/
def sourceCertificateId : String :=
  "STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1"

/-- The immutable classical snapshot to which the source certificate is bound. -/
def classicalSnapshotId : String :=
  "STRICT_PURE_WEYL_BV_SNAPSHOT_07dc7271b95b263a"

/-- The rational coefficient cancellation in the second nonlinear source. -/
theorem rationalCoefficientCancellation :
    (1 / 2 : ℚ) + (1 / 6 : ℚ) * (-3) = 0 := by
  norm_num

variable {V : Type*} [AddCommGroup V] [Module ℚ V]

/--
If the certificate's reduction of `q₁ S₂` to the quadratic Jacobiator and
the diagonal arity-three identity are supplied, then the second nonlinear
source is exactly `q₁`-closed.

This theorem isolates the pure logical/algebraic step from the analytic and
geometric premises that remain owned by the source certificate.
-/
theorem secondNonlinearSourceClosed
    (q₁ : V → V) (S₂ jacobiator cubicVertex : V)
    (hReduction :
      q₁ S₂ = (1 / 2 : ℚ) • jacobiator + (1 / 6 : ℚ) • q₁ cubicVertex)
    (hArityThree : q₁ cubicVertex = (-3 : ℚ) • jacobiator) :
    q₁ S₂ = 0 := by
  calc
    q₁ S₂ = (1 / 2 : ℚ) • jacobiator + (1 / 6 : ℚ) • q₁ cubicVertex :=
      hReduction
    _ = (1 / 2 : ℚ) • jacobiator + (1 / 6 : ℚ) • ((-3 : ℚ) • jacobiator) := by
      rw [hArityThree]
    _ = ((1 / 2 : ℚ) + (1 / 6 : ℚ) * (-3)) • jacobiator := by
      rw [smul_smul, ← add_smul]
    _ = 0 := by
      rw [rationalCoefficientCancellation, zero_smul]

/--
The physical interpretation attached to the formal theorem.  This Physlib
metadata is intentionally informal: the fully formal content is the theorem
`secondNonlinearSourceClosed`, while causal and geometric meaning remains in
the pinned Forge certificate.
-/
informal_definition strictWeylSecondSourceBridge where
  deps := [``secondNonlinearSourceClosed]
  tag := "WG2Q3"

#print axioms rationalCoefficientCancellation
#print axioms secondNonlinearSourceClosed

end WeylPhyslibBridge.StrictWeyl
