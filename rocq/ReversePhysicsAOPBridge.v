(** * Bridge: this stream's results in Assumptions-of-Physics notation.

    Carcassi and Aidala's classical theorem is

      Hamiltonian mechanics  <=>  determinism/reversibility + DOF independence

    and the structure carrying it is the symplectic form written as a tensor
    product (Reverse Physics for GR, Michigan, 16 Nov 2024, slide 2):

      omega_ab = [[0, 1], [-1, 0]] (x) I_n

    with the two factors given DISTINCT physical readings:

      the J factor      "area within each DOF"        (Areas = #confDOF)
      the (x) I_n       "scalar product across DOFs"  (#states = prod #confDOF)

    Their open conjecture, from the same talk, is that GR is the same statement
    for infinitely many dense DOFs -- a FIELD THEORY.  That is what makes this
    stream relevant: its carrier is a field theory on a compact state space, so
    it can test the conjecture rather than the finite-dimensional theorem.

    ** What this file establishes

      [alpha_of_is_contraction_with_omega]  the omega this development has been
                                            using all along, made explicit
      [omega_is_J_tensor_I]                 and it IS their J (x) I_n, once the
                                            coordinate ordering is matched
      [aop_factorisation_is_not_canonical]  the two factors' readings are
                                            bookkeeping: for EVERY decomposition
                                            their conjunction is the same
                                            proposition
      [aop_within_dof_reading_is_frame_dependent]
                                            "area within each DOF" is not
                                            invariant across admissible DOF
                                            decompositions
      [aop_conjecture_needs_a_topological_term]
                                            on a field theory with b_1 =/= 0,
                                            det/rev + DOF independence does NOT
                                            give Hamiltonian.  Uniform
                                            translation is the counterexample.

    The last is the one that bears on their open conjecture rather than on their
    established theorem.  Nothing here refutes the finite-dimensional result:
    H^1 vanishes on a vector space, which is exactly why it does not appear
    there.

    ** Boundary

    Everything is at one Fourier mode on T^4, inherited from the modules this
    imports.  No claim is made about GR, about their derivation, or about any
    carrier other than the one declared here. *)

Require Import QArith.
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
Require Import ReversePhysicsTorusReversal.
Require Import ReversePhysicsTorusSplit.

Open Scope Q_scope.

(** ** The symplectic form, made explicit *)

(** Our coordinate order is (q1, p1, q2, p2) -- interleaved.  omega_{ij} =
    omega(d_i, d_j) for omega = dq1^dp1 + dq2^dp2. *)
Definition omega_matrix (i j : Idx) : Q :=
  match i, j with
  | i0, i1 => 1 | i1, i0 => -1
  | i2, i3 => 1 | i3, i2 => -1
  | _, _ => 0
  end.

(** The [alpha_of] used throughout this stream is contraction with that form:
    (iota_X omega)_j = sum_i X^i omega_{ij}.  This is the only place the choice
    of omega is pinned down, and it is pinned to theirs. *)
Lemma alpha_of_is_contraction_with_omega :
  forall (a : Form) (j : Idx),
    alpha_of a j
    == a i0 * omega_matrix i0 j + a i1 * omega_matrix i1 j
     + a i2 * omega_matrix i2 j + a i3 * omega_matrix i3 j.
Proof. intros a j. destruct j; simpl; ring. Qed.

(** ** It is their J (x) I_n *)

(** Their slide writes the form in the BLOCK ordering (q1, q2, p1, p2), where it
    factorises as J (x) I_2.  Ours is the interleaved ordering; the two differ
    by a relabelling and nothing else. *)
Definition aop_reorder (i : Idx) : Idx :=
  match i with
  | i0 => i0    (* q1 -> slot 0 *)
  | i1 => i2    (* p1 -> slot 2 *)
  | i2 => i1    (* q2 -> slot 1 *)
  | i3 => i3    (* p2 -> slot 3 *)
  end.

(** J (x) I_2 in the block ordering: the identity block above the diagonal,
    minus the identity below. *)
Definition J_tensor_I (i j : Idx) : Q :=
  match i, j with
  | i0, i2 => 1 | i1, i3 => 1
  | i2, i0 => -1 | i3, i1 => -1
  | _, _ => 0
  end.

Theorem omega_is_J_tensor_I :
  forall i j, omega_matrix i j == J_tensor_I (aop_reorder i) (aop_reorder j).
Proof. intros i j. destruct i; destruct j; compute; reflexivity. Qed.

(** ** Their two factors, in this stream's vocabulary *)

(** The J factor: "area within each DOF".  [marginal] says each conjugate pair's
    own phase-space area is preserved, and [marginal_iff_intra_dof_closed]
    (proved in the reversal module) says that IS the intra-DOF part of the
    closedness conditions -- the same statement, not one implying the other. *)
Definition aop_within_dof_area := marginal.

(** The (x) I_n factor: "scalar product across DOFs". *)
Definition aop_across_dofs (k : Mode) (a b : Form) : Prop :=
  inter_dof_closed k (alpha_of a) (alpha_of b).

(** Determinism and reversibility are built into the carrier here (every mode
    evolves by a one-parameter group), so what remains of their hypothesis set
    is the DOF structure.  "Preserves omega" is the conjunction. *)
Definition aop_preserves_omega := symplectic.

(** ** Finding 1: the factorisation is bookkeeping, not physics *)

(** Their two factors are given distinct physical readings.  But the division of
    the closedness conditions into "within" and "across" depends on which
    Lagrangian decomposition is called "the degrees of freedom", and for EVERY
    such choice the conjunction is the same proposition.  The split is visible
    in each factor and invisible in the product. *)
Theorem aop_factorisation_is_not_canonical :
  forall k A B,
    (intra_P1 k A B /\ inter_P1 k A B <-> closed k A B) /\
    (intra_P2 k A B /\ inter_P2 k A B <-> closed k A B) /\
    (intra_P3 k A B /\ inter_P3 k A B <-> closed k A B).
Proof. apply split_dependence_cancels. Qed.

(** ** Finding 2: "area within each DOF" is frame-dependent *)

(** The same field preserves the area within each degree of freedom for the
    standard decomposition and fails to for a rotated one -- and BOTH are
    genuine symplectic decompositions (each block symplectic, the blocks
    omega-orthogonal, proved in [rotated_split_is_admissible]).

    So the J factor's reading is not a property of the dynamics alone.  It is a
    property of the dynamics together with a choice of what counts as a degree
    of freedom. *)
Theorem aop_within_dof_reading_is_frame_dependent :
  aop_within_dof_area k_drive a_drive b_zero /\
  ~ marginal_rot k_drive a_drive b_zero.
Proof. exact marginal_not_invariant_under_admissible_splits. Qed.

(** ** Finding 3: the conjecture needs a term the theorem does not have *)

(** THIS is the one aimed at their open conjecture rather than their established
    theorem.

    On a field theory whose state space has b_1 =/= 0, preserving omega does NOT
    give a global Hamiltonian.  Uniform translation X = d/dq1 on T^4 is
    deterministic, reversible, preserves the area within each degree of freedom,
    preserves the total phase-space volume, and preserves omega -- and admits no
    global Hamiltonian.

    Nothing here contradicts the finite-dimensional theorem: H^1 vanishes on a
    vector space, which is precisely why the obstruction is invisible there.
    But the conjecture "GR <=> det/rev + DOF independence for dense DOFs" is
    about a field theory, and a field theory can have topology. *)
Theorem aop_conjecture_needs_a_topological_term :
  forall k, zero_mode k ->
    closed k (unit_form i0) zero_form /\ ~ exact_form k (unit_form i0) zero_form.
Proof. apply translation_is_closed_but_not_exact. Qed.

(** And the size of the missing term is not a detail that could be absorbed: it
    is exactly the first Betti number of the state space, four for T^4, carried
    entirely by the constants.  Every mode with a nonzero frequency contributes
    nothing. *)
Theorem aop_missing_term_is_exactly_the_first_cohomology :
  forall k A B, closed k A B -> (zero_mode k) \/ (exact_form k A B).
Proof. apply gap_is_carried_entirely_by_the_zero_mode. Qed.

(** ** The honest ledger *)

Print Assumptions alpha_of_is_contraction_with_omega.
Print Assumptions omega_is_J_tensor_I.
Print Assumptions aop_factorisation_is_not_canonical.
Print Assumptions aop_within_dof_reading_is_frame_dependent.
Print Assumptions aop_conjecture_needs_a_topological_term.
Print Assumptions aop_missing_term_is_exactly_the_first_cohomology.
