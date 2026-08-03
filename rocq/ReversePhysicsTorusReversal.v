(** * A reversal: the law is EQUIVALENT to three independent assumptions.

    Everything in this stream so far has been one-directional: assumptions imply
    the law, or one level of the chain implies the next.  That is the forward
    half of reverse physics.  This file supplies the other half.

    ** What a reversal needs

    Reverse mathematics proves [T <-> A] over a weak base theory, and then shows
    [A] is INDEPENDENT -- dropping it admits a counterexample.  The equivalence
    is what pins [A] as the content of [T] rather than merely sufficient for it;
    the independence is what stops the axiom set from being padded.

    ** The base theory

    The role played by RCA_0 is played here by the CARRIER DECLARATION, and it is
    definitional context rather than an axiom schema.  Made explicit:

      - the state space is T^4 with coordinates ordered (q1, p1, q2, p2);
      - the symplectic form omega = dq1^dp1 + dq2^dp2 is FIXED;
      - the degree-of-freedom split into the pairs (q1,p1) and (q2,p2) is FIXED
        and is part of the structure, NOT derived -- see
        [marginal_depends_on_the_dof_split], which proves the first assumption
        below is genuinely relative to this choice;
      - fields are trigonometric polynomials, treated one Fourier mode at a time;
      - coefficients are rational, so every statement is exact.

    Honesty about this: a genuine reverse-mathematics base is an axiom system one
    can weaken and compare against.  The list above is a definitional context.
    Turning it into a real parameterised base -- quantifying over DOF splits and
    over symplectic forms -- is not done here, and the single result that gestures
    at it is the split-dependence theorem at the end.

    ** The three assumptions

      A1  [marginal]           each degree of freedom independently conserves its
                               own phase-space area.  A physical postulate.
      A2  [inter_dof_closed]   the cross-degree-of-freedom closedness equations.
      A3  [no_uniform_drift]   at the zero mode the field vanishes; equivalently,
                               no uniform translation component.  Topological.

    ** The result

      [hamiltonian_iff_three_assumptions]  law <-> A1 /\ A2 /\ A3
      [A1_is_independent] [A2_is_independent] [A3_is_independent]

    ** The finding to be honest about

    A1 is a physical postulate and A3 is a clean topological one.  A2 is neither:
    it is a geometric consistency condition between degrees of freedom with no
    physical reading offered here.  So the law decomposes into three independent
    pieces, only two of which this stream can state in physical vocabulary.  That
    is a result about how much of Hamiltonian structure is physically
    axiomatisable, and it is not a comfortable one. *)

Require Import QArith.
Require Import Setoid.
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.

Open Scope Q_scope.

(** ** A small arithmetic helper *)

Lemma Qopp_eq_zero : forall x : Q, - x == 0 -> x == 0.
Proof.
  intros x H.
  setoid_replace x with (0 - (- x)) by ring.
  rewrite H. ring.
Qed.

(** ** The three assumptions *)

(** A1 is [marginal], already defined in the chain development.  It is stated in
    physical vocabulary: each conjugate pair has vanishing partial divergence. *)

(** A2: the four CROSS-degree-of-freedom closedness equations, the ones
    [marginal] provably cannot see. *)
Definition inter_dof_closed (k : Mode) (A B : Form) : Prop :=
  (k i0 * A i2 == k i2 * A i0) /\ (k i0 * B i2 == k i2 * B i0) /\
  (k i0 * A i3 == k i3 * A i0) /\ (k i0 * B i3 == k i3 * B i0) /\
  (k i1 * A i2 == k i2 * A i1) /\ (k i1 * B i2 == k i2 * B i1) /\
  (k i1 * A i3 == k i3 * A i1) /\ (k i1 * B i3 == k i3 * B i1).

(** A3: no uniform drift.  At the zero mode the field vanishes.  Away from the
    zero mode the condition is vacuous, which is exactly right: the obstruction
    it removes is the one carried by the constants. *)
Definition no_uniform_drift (k : Mode) (a b : Form) : Prop :=
  zero_mode k -> forall j, a j == 0 /\ b j == 0.

(** ** A1 is exactly the intra-DOF closedness, in physical vocabulary *)

(** This is what licenses calling the first assumption a physical postulate: the
    marginal condition and the intra-DOF closedness equations are the same
    statement, not merely one implying the other. *)
Theorem marginal_iff_intra_dof_closed :
  forall k a b,
    marginal k a b <-> intra_dof_closed k (alpha_of a) (alpha_of b).
Proof.
  intros k a b. split.
  - intros [Ha01 [Hb01 [Ha23 Hb23]]].
    unfold intra_dof_closed. simpl. repeat split.
    + transitivity (k i0 * a i0 + k i1 * a i1 - k i1 * a i1). ring.
      rewrite Ha01. ring.
    + transitivity (k i0 * b i0 + k i1 * b i1 - k i1 * b i1). ring.
      rewrite Hb01. ring.
    + transitivity (k i2 * a i2 + k i3 * a i3 - k i3 * a i3). ring.
      rewrite Ha23. ring.
    + transitivity (k i2 * b i2 + k i3 * b i3 - k i3 * b i3). ring.
      rewrite Hb23. ring.
  - apply intra_dof_closed_implies_marginal.
Qed.

(** ** A1 and A2 together are exactly closedness *)

Lemma closed_of_intra_and_inter :
  forall k A B,
    intra_dof_closed k A B -> inter_dof_closed k A B -> closed k A B.
Proof.
  intros k A B [H01A [H01B [H23A H23B]]]
               [H02A [H02B [H03A [H03B [H12A [H12B [H13A H13B]]]]]]].
  intros i j. destruct i; destruct j; split;
    solve [ reflexivity | assumption | symmetry; assumption ].
Qed.

Lemma inter_of_closed :
  forall k A B, closed k A B -> inter_dof_closed k A B.
Proof.
  intros k A B H.
  destruct (H i0 i2) as [A02 B02]. destruct (H i0 i3) as [A03 B03].
  destruct (H i1 i2) as [A12 B12]. destruct (H i1 i3) as [A13 B13].
  repeat split; assumption.
Qed.

(** ** The zero mode: the field vanishes iff its 1-form does *)

Lemma alpha_vanishes_iff :
  forall a, (forall j, alpha_of a j == 0) <-> (forall j, a j == 0).
Proof.
  intros a. split.
  - intros H j. destruct j; simpl.
    + exact (H i1).
    + apply Qopp_eq_zero. exact (H i0).
    + exact (H i3).
    + apply Qopp_eq_zero. exact (H i2).
  - intros H j. destruct j; simpl.
    + rewrite (H i1). ring.
    + exact (H i0).
    + rewrite (H i3). ring.
    + exact (H i2).
Qed.

(** ** THE REVERSAL *)

(** The law is equivalent to the conjunction of the three assumptions.  The
    forward direction is the reversal proper: from the law alone, each assumption
    is derived. *)
Theorem hamiltonian_iff_three_assumptions :
  forall k a b,
    hamiltonian k a b <->
      (marginal k a b /\
       inter_dof_closed k (alpha_of a) (alpha_of b) /\
       no_uniform_drift k a b).
Proof.
  intros k a b. split.
  - (* the law implies each assumption *)
    intros Hham.
    assert (Hclosed : closed k (alpha_of a) (alpha_of b))
      by (apply exact_implies_closed; exact Hham).
    split; [| split].
    + apply symplectic_implies_marginal. exact Hclosed.
    + apply inter_of_closed. exact Hclosed.
    + intros Hz.
      pose proof (proj1 (exact_at_zero_mode_iff_vanishing
                           k (alpha_of a) (alpha_of b) Hz) Hham) as Hv.
      assert (Ha : forall j, a j == 0).
      { apply (proj1 (alpha_vanishes_iff a)). intros j'. exact (proj1 (Hv j')). }
      assert (Hb : forall j, b j == 0).
      { apply (proj1 (alpha_vanishes_iff b)). intros j'. exact (proj2 (Hv j')). }
      intros j. split; [exact (Ha j) | exact (Hb j)].
  - (* the three assumptions imply the law *)
    intros [Hm [Hi Hd]].
    assert (Hclosed : closed k (alpha_of a) (alpha_of b)).
    { apply closed_of_intra_and_inter.
      - exact (proj1 (marginal_iff_intra_dof_closed k a b) Hm).
      - exact Hi. }
    destruct (mode_dichotomy k) as [Hz | Hnz].
    + (* zero mode: A3 forces the field, hence its 1-form, to vanish *)
      apply (proj2 (exact_at_zero_mode_iff_vanishing k (alpha_of a) (alpha_of b) Hz)).
      assert (Ha : forall j, alpha_of a j == 0).
      { apply (proj2 (alpha_vanishes_iff a)). intros j'. exact (proj1 (Hd Hz j')). }
      assert (Hb : forall j, alpha_of b j == 0).
      { apply (proj2 (alpha_vanishes_iff b)). intros j'. exact (proj2 (Hd Hz j')). }
      intros j. split; [exact (Ha j) | exact (Hb j)].
    + (* nonzero mode: closed = exact *)
      exact (proj1 (closed_iff_exact_at_nonzero k (alpha_of a) (alpha_of b) Hnz) Hclosed).
Qed.

(** ** Independence: dropping any one assumption admits a counterexample *)

(** Drop A1.  [X = cos(2 pi q1) d/dq1] at mode [e_{q1}]: the cross-DOF equations
    hold and there is no drift, but the first degree of freedom does not conserve
    its own area. *)
Definition k_selfdrive : Mode := mkmode 1 0 0 0.
Definition a_selfdrive : Form := mkform 1 0 0 0.

Theorem A1_is_independent :
  inter_dof_closed k_selfdrive (alpha_of a_selfdrive) (alpha_of b_zero) /\
  no_uniform_drift k_selfdrive a_selfdrive b_zero /\
  ~ marginal k_selfdrive a_selfdrive b_zero /\
  ~ hamiltonian k_selfdrive a_selfdrive b_zero.
Proof.
  split; [| split; [| split]].
  - repeat split; compute; reflexivity.
  - intros Hz. specialize (Hz i0). compute in Hz. discriminate Hz.
  - intros [Hm _]. compute in Hm. discriminate Hm.
  - intros Hham.
    destruct (proj1 (hamiltonian_iff_three_assumptions _ _ _) Hham) as [Hm _].
    destruct Hm as [Hm _]. compute in Hm. discriminate Hm.
Qed.

(** Drop A2.  [X = cos(2 pi q2) d/dq1] at mode [e_{q2}]: every degree of freedom
    conserves its own area and there is no drift, but a cross-DOF equation
    fails. *)
Theorem A2_is_independent :
  marginal k_shear a_shear b_zero /\
  no_uniform_drift k_shear a_shear b_zero /\
  ~ inter_dof_closed k_shear (alpha_of a_shear) (alpha_of b_zero) /\
  ~ hamiltonian k_shear a_shear b_zero.
Proof.
  split; [| split; [| split]].
  - exact (proj1 marginal_not_symplectic).
  - intros Hz. specialize (Hz i2). compute in Hz. discriminate Hz.
  - intros [_ [_ [_ [_ [H12A _]]]]]. compute in H12A. discriminate H12A.
  - intros Hham.
    destruct (proj1 (hamiltonian_iff_three_assumptions _ _ _) Hham) as [_ [Hi _]].
    destruct Hi as [_ [_ [_ [_ [H12A _]]]]]. compute in H12A. discriminate H12A.
Qed.

(** Drop A3.  Uniform translation [X = d/dq1] at the zero mode: every closedness
    equation holds vacuously, each degree of freedom conserves its area, and the
    field still admits no global Hamiltonian. *)
Definition k_rest : Mode := mkmode 0 0 0 0.

Theorem A3_is_independent :
  marginal k_rest a_shear b_zero /\
  inter_dof_closed k_rest (alpha_of a_shear) (alpha_of b_zero) /\
  ~ no_uniform_drift k_rest a_shear b_zero /\
  ~ hamiltonian k_rest a_shear b_zero.
Proof.
  split; [| split; [| split]].
  - repeat split; compute; reflexivity.
  - repeat split; compute; reflexivity.
  - intros Hd.
    assert (Hz : zero_mode k_rest) by (intros i; destruct i; compute; reflexivity).
    destruct (Hd Hz i0) as [Ha _]. compute in Ha. discriminate Ha.
  - intros Hham.
    destruct (proj1 (hamiltonian_iff_three_assumptions _ _ _) Hham) as [_ [_ Hd]].
    assert (Hz : zero_mode k_rest) by (intros i; destruct i; compute; reflexivity).
    destruct (Hd Hz i0) as [Ha _]. compute in Ha. discriminate Ha.
Qed.

(** ** The first assumption is relative to the degree-of-freedom split *)

(** The whole stream has carried "the DOF split is an input, not derived" as a
    declared assumption.  Here it is a theorem: the SAME field is marginal for
    the split {(q1,p1), (q2,p2)} and not marginal for the split
    {(q1,q2), (p1,p2)}.  So A1 is not a property of the dynamics alone -- it is a
    property of the dynamics together with a choice of what counts as a degree of
    freedom. *)
Definition marginal_alt (k : Mode) (a b : Form) : Prop :=
  (k i0 * a i0 + k i2 * a i2 == 0) /\ (k i0 * b i0 + k i2 * b i2 == 0) /\
  (k i1 * a i1 + k i3 * a i3 == 0) /\ (k i1 * b i1 + k i3 * b i3 == 0).

Definition k_pair : Mode := mkmode 1 1 0 0.
Definition a_pair : Form := mkform 1 (-1) 0 0.

Theorem marginal_depends_on_the_dof_split :
  marginal k_pair a_pair b_zero /\ ~ marginal_alt k_pair a_pair b_zero.
Proof.
  split.
  - repeat split; compute; reflexivity.
  - intros [H _]. compute in H. discriminate H.
Qed.

(** ** The honest ledger *)

Print Assumptions Qopp_eq_zero.
Print Assumptions marginal_iff_intra_dof_closed.
Print Assumptions closed_of_intra_and_inter.
Print Assumptions inter_of_closed.
Print Assumptions alpha_vanishes_iff.
Print Assumptions hamiltonian_iff_three_assumptions.
Print Assumptions A1_is_independent.
Print Assumptions A2_is_independent.
Print Assumptions A3_is_independent.
Print Assumptions marginal_depends_on_the_dof_split.
