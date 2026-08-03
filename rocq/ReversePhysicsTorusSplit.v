(** * Why the third assumption is not physical: the split-dependence cancels.

    [ReversePhysicsTorusReversal.v] proved [law <-> A1 /\ A2 /\ A3] with each
    assumption independent, and left an uncomfortable finding: A1 is a physical
    postulate (per-degree-of-freedom information conservation), A3 is cleanly
    topological, and A2 -- the cross-degree-of-freedom equations -- is neither.

    This file explains A2 rather than leaving it unexplained, and in doing so
    CORRECTS the billing of an earlier theorem.

    ** The correction

    [marginal_depends_on_the_dof_split] compared the standard pairing
    {(q1,p1),(q2,p2)} against {(q1,q2),(p1,p2)}.  That second pairing is
    ISOTROPIC -- omega vanishes on each of its blocks -- so it is not a
    decomposition into degrees of freedom at all, and the theorem showed only
    that [marginal] depends on an arbitrary coordinate pairing.  The theorem is
    true; its billing was too generous.  [alt_pairing_is_isotropic] below records
    this, and [marginal_not_invariant_under_admissible_splits] supplies the
    honest version: [marginal] is not invariant even across genuinely
    SYMPLECTIC splits.

    ** The explanation

    A1 depends on the split.  The law does not.  So the split-dependence has to
    cancel somewhere, and [split_dependence_cancels] shows where: for EVERY
    pairing of the four coordinates, [intra_P /\ inter_P] is the same
    proposition, namely closedness -- which mentions no split at all.

    So A2 is not a mysterious extra postulate.  It is the REMAINDER of a
    bookkeeping choice: having elected to call two of the six closedness
    equations "each degree of freedom conserves its own information", A2 is
    whatever is left over.  Choose a different split and the same content is
    divided differently.

    ** What this costs the programme

    A reverse-physics assumption ought not to depend on a coordinate choice.
    [marginal] does.  So "each degree of freedom independently conserves
    information" cannot be a fundamental assumption on its own; only its
    conjunction with the remainder is split-independent, and that conjunction is
    just "preserves omega".  The decomposition into a physical part and a
    geometric part is therefore NOT canonical -- which is a real limitation on
    reverse-physics-style axiomatisations of this law, not a defect of this
    formalisation. *)

Require Import QArith.
Require Import Setoid.
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
Require Import ReversePhysicsTorusReversal.

Open Scope Q_scope.

(** ** Which coordinate pairings are actually degree-of-freedom splits? *)

(** omega = dq1^dp1 + dq2^dp2 evaluated on two vectors. *)
Definition omega_of (u v : Form) : Q :=
  u i0 * v i1 - u i1 * v i0 + u i2 * v i3 - u i3 * v i2.

Definition e (d : Idx) : Form :=
  fun j => match j, d with
           | i0, i0 | i1, i1 | i2, i2 | i3, i3 => 1
           | _, _ => 0
           end.

(** A pair of directions spans a symplectic plane exactly when omega does not
    vanish on it.  A degree of freedom IS such a plane; an isotropic pair is
    not one. *)
Definition symplectic_pair (x y : Idx) : Prop := ~ (omega_of (e x) (e y) == 0).

(** The standard pairing is a genuine degree-of-freedom split. *)
Theorem standard_pairing_is_symplectic :
  symplectic_pair i0 i1 /\ symplectic_pair i2 i3.
Proof.
  split; intros H; compute in H; discriminate H.
Qed.

(** The pairing used by [marginal_depends_on_the_dof_split] is NOT: omega
    vanishes on both of its blocks, so it pairs directions that are not
    conjugate.  This is the correction. *)
Theorem alt_pairing_is_isotropic :
  omega_of (e i0) (e i2) == 0 /\ omega_of (e i1) (e i3) == 0.
Proof.
  split; compute; reflexivity.
Qed.

(** The third coordinate pairing is isotropic too, so among the three ways of
    pairing up four coordinates exactly ONE is a degree-of-freedom split. *)
Theorem third_pairing_is_isotropic :
  omega_of (e i0) (e i3) == 0 /\ omega_of (e i1) (e i2) == 0.
Proof.
  split; compute; reflexivity.
Qed.

(** ** An honestly admissible alternative split *)

(** V1' = span(e_q1 + e_q2, e_p1 + e_p2),  V2' = span(e_q1 - e_q2, e_p1 - e_p2).
    Each block is symplectic and the two are omega-orthogonal, so this IS a
    legitimate decomposition into two degrees of freedom -- just not the
    coordinate one. *)
Definition u1 : Form := fun j => match j with i0 => 1 | i1 => 0 | i2 => 1 | i3 => 0 end.
Definition v1 : Form := fun j => match j with i0 => 0 | i1 => 1 | i2 => 0 | i3 => 1 end.
Definition u2 : Form := fun j => match j with i0 => 1 | i1 => 0 | i2 => -1 | i3 => 0 end.
Definition v2 : Form := fun j => match j with i0 => 0 | i1 => 1 | i2 => 0 | i3 => -1 end.

Theorem rotated_split_is_admissible :
  (~ omega_of u1 v1 == 0) /\ (~ omega_of u2 v2 == 0) /\
  omega_of u1 u2 == 0 /\ omega_of u1 v2 == 0 /\
  omega_of v1 u2 == 0 /\ omega_of v1 v2 == 0.
Proof.
  repeat split;
    try (intros H; compute in H; discriminate H);
    compute; reflexivity.
Qed.

(** The marginal condition for the rotated split.  For a splitting with
    projector pi, the per-degree-of-freedom divergence in a Fourier mode is
    k^T pi a; for the standard split that is [k0 a0 + k1 a1], and for this one
    it is the expression below (the overall factor 1/2 is dropped, harmless). *)
Definition marginal_rot (k : Mode) (a b : Form) : Prop :=
  ((k i0 + k i2) * (a i0 + a i2) + (k i1 + k i3) * (a i1 + a i3) == 0) /\
  ((k i0 + k i2) * (b i0 + b i2) + (k i1 + k i3) * (b i1 + b i3) == 0) /\
  ((k i0 - k i2) * (a i0 - a i2) + (k i1 - k i3) * (a i1 - a i3) == 0) /\
  ((k i0 - k i2) * (b i0 - b i2) + (k i1 - k i3) * (b i1 - b i3) == 0).

(** [X = cos(2 pi q1) d/dq2]: one degree of freedom drives the other's
    coordinate. *)
Definition k_drive : Mode := mkmode 1 0 0 0.
Definition a_drive : Form := mkform 0 0 1 0.

(** THE HONEST SPLIT-DEPENDENCE.  The same field conserves information in every
    degree of freedom of the standard split and fails to in the rotated one --
    and BOTH splits are genuine symplectic decompositions. *)
Theorem marginal_not_invariant_under_admissible_splits :
  marginal k_drive a_drive b_zero /\ ~ marginal_rot k_drive a_drive b_zero.
Proof.
  split.
  - repeat split; compute; reflexivity.
  - intros [H _]. compute in H. discriminate H.
Qed.

(** ** The cancellation *)

Definition eqn (k : Mode) (F : Form) (i j : Idx) : Prop := k i * F j == k j * F i.

(** Closedness is exactly the twelve pair equations -- and it mentions no
    split whatsoever. *)
Lemma closed_iff_pairs :
  forall k A B, closed k A B <->
    (eqn k A i0 i1 /\ eqn k B i0 i1 /\ eqn k A i0 i2 /\ eqn k B i0 i2 /\
     eqn k A i0 i3 /\ eqn k B i0 i3 /\ eqn k A i1 i2 /\ eqn k B i1 i2 /\
     eqn k A i1 i3 /\ eqn k B i1 i3 /\ eqn k A i2 i3 /\ eqn k B i2 i3).
Proof.
  intros k A B. split.
  - intros H.
    destruct (H i0 i1) as [a01 b01]. destruct (H i0 i2) as [a02 b02].
    destruct (H i0 i3) as [a03 b03]. destruct (H i1 i2) as [a12 b12].
    destruct (H i1 i3) as [a13 b13]. destruct (H i2 i3) as [a23 b23].
    repeat split; assumption.
  - intros [a01 [b01 [a02 [b02 [a03 [b03 [a12 [b12 [a13 [b13 [a23 b23]]]]]]]]]]].
    intros i j. destruct i; destruct j; split;
      solve [ reflexivity | assumption | symmetry; assumption ].
Qed.

(** The three ways of pairing the four coordinates.  For each, [intra] is the
    two equations INSIDE the blocks and [inter] the four BETWEEN them. *)

Definition intra_P1 k A B := eqn k A i0 i1 /\ eqn k B i0 i1 /\ eqn k A i2 i3 /\ eqn k B i2 i3.
Definition inter_P1 k A B :=
  eqn k A i0 i2 /\ eqn k B i0 i2 /\ eqn k A i0 i3 /\ eqn k B i0 i3 /\
  eqn k A i1 i2 /\ eqn k B i1 i2 /\ eqn k A i1 i3 /\ eqn k B i1 i3.

Definition intra_P2 k A B := eqn k A i0 i2 /\ eqn k B i0 i2 /\ eqn k A i1 i3 /\ eqn k B i1 i3.
Definition inter_P2 k A B :=
  eqn k A i0 i1 /\ eqn k B i0 i1 /\ eqn k A i0 i3 /\ eqn k B i0 i3 /\
  eqn k A i1 i2 /\ eqn k B i1 i2 /\ eqn k A i2 i3 /\ eqn k B i2 i3.

Definition intra_P3 k A B := eqn k A i0 i3 /\ eqn k B i0 i3 /\ eqn k A i1 i2 /\ eqn k B i1 i2.
Definition inter_P3 k A B :=
  eqn k A i0 i1 /\ eqn k B i0 i1 /\ eqn k A i0 i2 /\ eqn k B i0 i2 /\
  eqn k A i1 i3 /\ eqn k B i1 i3 /\ eqn k A i2 i3 /\ eqn k B i2 i3.

(** THE CANCELLATION.  Whichever pairing is chosen, the conjunction of "inside
    the blocks" and "between the blocks" is the SAME proposition: closedness.
    The split is visible in each conjunct and invisible in the conjunction. *)
Lemma cancel_P1 :
  forall k A B, intra_P1 k A B /\ inter_P1 k A B <-> closed k A B.
Proof.
  intros k A B. assert (E := closed_iff_pairs k A B).
  unfold intra_P1, inter_P1. tauto.
Qed.

Lemma cancel_P2 :
  forall k A B, intra_P2 k A B /\ inter_P2 k A B <-> closed k A B.
Proof.
  intros k A B. assert (E := closed_iff_pairs k A B).
  unfold intra_P2, inter_P2. tauto.
Qed.

Lemma cancel_P3 :
  forall k A B, intra_P3 k A B /\ inter_P3 k A B <-> closed k A B.
Proof.
  intros k A B. assert (E := closed_iff_pairs k A B).
  unfold intra_P3, inter_P3. tauto.
Qed.

Theorem split_dependence_cancels :
  forall k A B,
    (intra_P1 k A B /\ inter_P1 k A B <-> closed k A B) /\
    (intra_P2 k A B /\ inter_P2 k A B <-> closed k A B) /\
    (intra_P3 k A B /\ inter_P3 k A B <-> closed k A B).
Proof.
  intros k A B.
  split; [apply cancel_P1 | split; [apply cancel_P2 | apply cancel_P3]].
Qed.

(** Consequently the law admits three different decompositions of the same
    shape, differing only in how the labour is divided between the "physical"
    conjunct and the "geometric" one. *)
Theorem law_decomposes_three_ways :
  forall k a b,
    (hamiltonian k a b <->
       (intra_P1 k (alpha_of a) (alpha_of b) /\ inter_P1 k (alpha_of a) (alpha_of b)
        /\ no_uniform_drift k a b)) /\
    (hamiltonian k a b <->
       (intra_P2 k (alpha_of a) (alpha_of b) /\ inter_P2 k (alpha_of a) (alpha_of b)
        /\ no_uniform_drift k a b)) /\
    (hamiltonian k a b <->
       (intra_P3 k (alpha_of a) (alpha_of b) /\ inter_P3 k (alpha_of a) (alpha_of b)
        /\ no_uniform_drift k a b)).
Proof.
  intros k a b.
  destruct (split_dependence_cancels k (alpha_of a) (alpha_of b)) as [C1 [C2 C3]].
  assert (L : hamiltonian k a b <->
              (closed k (alpha_of a) (alpha_of b) /\ no_uniform_drift k a b)).
  { split.
    - intros H. split.
      + apply exact_implies_closed. exact H.
      + exact (proj2 (proj2 (proj1 (hamiltonian_iff_three_assumptions k a b) H))).
    - intros [Hc Hd].
      apply (proj2 (hamiltonian_iff_three_assumptions k a b)).
      split; [| split].
      + apply symplectic_implies_marginal. exact Hc.
      + apply inter_of_closed. exact Hc.
      + exact Hd. }
  split; [| split].
  - split.
    + intros Hh. apply L in Hh. destruct Hh as [Hc Hd].
      destruct (proj2 C1 Hc) as [Hi Hn].
      split; [exact Hi | split; [exact Hn | exact Hd]].
    + intros [Hi [Hn Hd]]. apply L.
      split; [apply (proj1 C1); split; assumption | exact Hd].
  - split.
    + intros Hh. apply L in Hh. destruct Hh as [Hc Hd].
      destruct (proj2 C2 Hc) as [Hi Hn].
      split; [exact Hi | split; [exact Hn | exact Hd]].
    + intros [Hi [Hn Hd]]. apply L.
      split; [apply (proj1 C2); split; assumption | exact Hd].
  - split.
    + intros Hh. apply L in Hh. destruct Hh as [Hc Hd].
      destruct (proj2 C3 Hc) as [Hi Hn].
      split; [exact Hi | split; [exact Hn | exact Hd]].
    + intros [Hi [Hn Hd]]. apply L.
      split; [apply (proj1 C3); split; assumption | exact Hd].
Qed.

(** ** The honest ledger *)

Print Assumptions standard_pairing_is_symplectic.
Print Assumptions alt_pairing_is_isotropic.
Print Assumptions third_pairing_is_isotropic.
Print Assumptions rotated_split_is_admissible.
Print Assumptions marginal_not_invariant_under_admissible_splits.
Print Assumptions closed_iff_pairs.
Print Assumptions split_dependence_cancels.
Print Assumptions law_decomposes_three_ways.
