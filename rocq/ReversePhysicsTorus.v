(** * The torus Hamiltonian-privilege gap, for EVERY Fourier mode.

    The Forge gate [forge/examples/reverse_physics_torus_gate.forge] computes the
    symplectic-minus-Hamiltonian gap on T^4 at truncations N = 0,1,2,3 and finds 4
    every time, carried entirely by the zero mode.  Four values of N are not a
    theorem in N.  This file closes that gate, and closes it more strongly than an
    induction over N would: the statements below are quantified over ALL modes, so
    they hold for every truncation whatsoever, finite or not.

    The mathematical content is the closed-vs-exact structure of the 1-form
    [alpha = iota_X omega] in a single Fourier mode.  Writing a mode's 1-form as
    [alpha_j = A j * cos_k + B j * sin_k],

      - closed  (X is symplectic, i.e. locally Hamiltonian):
          k_i A_j = k_j A_i  and  k_i B_j = k_j B_i   for all i, j
      - exact   (X is globally Hamiltonian, alpha = dH with H = c cos_k + s sin_k):
          A_j = k_j s  and  B_j = - k_j c

    THE THREE RESULTS

      [closed_at_zero_mode]              at k = 0 every 1-form is closed
      [exact_at_zero_mode_iff_vanishing] at k = 0 the only exact 1-form is 0
      [closed_iff_exact_at_nonzero]      at every k <> 0, closed = exact exactly

    So every nonzero mode contributes nothing to the gap and the zero mode
    contributes its whole 4-dimensional space of constant 1-forms.  That is
    b_1(T^4) = 4, for every truncation, with no computation and no bound on N.

    BOUNDARY.  This file formalises the symplectic/Hamiltonian (closed/exact)
    structure only.  The marginal and volume-preserving levels, the per-mode rank
    computations, and the arithmetic that sums per-mode dimensions into the totals
    tabulated in the report are NOT formalised here; they remain the Forge gate's
    exact-rational computation.  Frequencies are modelled in Q (integer
    frequencies embed); nothing below needs them to be integral. *)

Require Import QArith.

Open Scope Q_scope.

(** ** The carrier *)

(** The four coordinate directions of T^4, ordered (q1, p1, q2, p2). *)
Inductive Idx : Set := i0 | i1 | i2 | i3.

(** A Fourier mode: one frequency per direction. *)
Definition Mode := Idx -> Q.

(** One trigonometric component of a 1-form: one rational per direction. *)
Definition Form := Idx -> Q.

(** [k] is the zero mode. *)
Definition zero_mode (k : Mode) : Prop := forall i, k i == 0.

(** [k] is some nonzero mode. *)
Definition nonzero_mode (k : Mode) : Prop := exists m, ~ (k m == 0).

(** The 1-form (A, B) at mode [k] is CLOSED: [d alpha = 0]. *)
Definition closed (k : Mode) (A B : Form) : Prop :=
  forall i j, (k i * A j == k j * A i) /\ (k i * B j == k j * B i).

(** The 1-form (A, B) at mode [k] is EXACT: [alpha = dH] for a potential
    [H = c cos_k + s sin_k] in the same mode. *)
Definition exact_form (k : Mode) (A B : Form) : Prop :=
  exists c s : Q, forall j, (A j == k j * s) /\ (B j == - (k j * c)).

(** ** Exact always implies closed, at every mode *)

Lemma exact_implies_closed :
  forall k A B, exact_form k A B -> closed k A B.
Proof.
  intros k A B [c [s H]] i j.
  destruct (H i) as [HAi HBi].
  destruct (H j) as [HAj HBj].
  split.
  - rewrite HAi, HAj. ring.
  - rewrite HBi, HBj. ring.
Qed.

(** ** The zero mode carries the whole gap *)

(** At [k = 0] the closedness equations are vacuous: every 1-form is closed.
    Physically, every constant vector field on the torus preserves omega. *)
Theorem closed_at_zero_mode :
  forall k A B, zero_mode k -> closed k A B.
Proof.
  intros k A B Hz i j.
  rewrite (Hz i), (Hz j).
  split; ring.
Qed.

(** At [k = 0] the potential is a constant and its differential vanishes, so the
    only exact 1-form is the zero one.  Combined with the previous theorem, the
    classes at the zero mode are ALL constant 1-forms: a copy of Q^4. *)
Theorem exact_at_zero_mode_iff_vanishing :
  forall k A B, zero_mode k ->
    (exact_form k A B <-> (forall j, A j == 0 /\ B j == 0)).
Proof.
  intros k A B Hz. split.
  - intros [c [s H]] j.
    destruct (H j) as [HA HB].
    rewrite HA, HB, (Hz j).
    split; ring.
  - intros H. exists 0, 0. intros j.
    destruct (H j) as [HA HB].
    rewrite HA, HB, (Hz j).
    split; ring.
Qed.

(** The four constant 1-forms are independent classes: a constant 1-form is
    exact iff every one of its four components vanishes.  This is the
    [b_1(T^4) = 4] statement in coordinates. *)
Corollary zero_mode_has_four_independent_classes :
  forall k A B, zero_mode k ->
    (exact_form k A B <->
       (A i0 == 0 /\ A i1 == 0 /\ A i2 == 0 /\ A i3 == 0 /\
        B i0 == 0 /\ B i1 == 0 /\ B i2 == 0 /\ B i3 == 0)).
Proof.
  intros k A B Hz.
  rewrite (exact_at_zero_mode_iff_vanishing k A B Hz).
  split.
  - intros H.
    destruct (H i0) as [A0 B0]. destruct (H i1) as [A1 B1].
    destruct (H i2) as [A2 B2]. destruct (H i3) as [A3 B3].
    repeat split; assumption.
  - intros [A0 [A1 [A2 [A3 [B0 [B1 [B2 B3]]]]]]].
    intros j. destruct j; split; assumption.
Qed.

(** ** Every nonzero mode contributes nothing *)

(** The heart of the matter.  At any mode with some nonzero frequency, closed
    and exact coincide: there is no cohomology away from the constants.  The
    potential is built explicitly from the direction [m] whose frequency does not
    vanish, which is why no bound on the mode is ever needed. *)
Theorem closed_iff_exact_at_nonzero :
  forall k A B, nonzero_mode k -> (closed k A B <-> exact_form k A B).
Proof.
  intros k A B [m Hm]. split.
  - intros Hc.
    exists (- (B m / k m)), (A m / k m).
    intros j.
    destruct (Hc m j) as [HA HB].
    split.
    + (* A j == k j * (A m / k m), from k m * A j == k j * A m *)
      apply (Qmult_inj_l _ _ (k m) Hm).
      rewrite HA. field. exact Hm.
    + (* B j == - (k j * - (B m / k m)), from k m * B j == k j * B m *)
      apply (Qmult_inj_l _ _ (k m) Hm).
      rewrite HB. field. exact Hm.
  - apply exact_implies_closed.
Qed.

(** Restated as the gap statement: at a nonzero mode the quotient
    closed/exact is trivial, so such a mode contributes no class. *)
Corollary nonzero_mode_contributes_no_class :
  forall k A B, nonzero_mode k -> closed k A B -> exact_form k A B.
Proof.
  intros k A B Hnz Hc.
  exact (proj1 (closed_iff_exact_at_nonzero k A B Hnz) Hc).
Qed.

(** ** The gap, for every truncation at once *)

(** Every mode is either the zero mode or a nonzero one, so the two cases above
    are exhaustive: this is why quantifying over modes subsumes quantifying over
    truncations.  (Constructively we need the decidability of [k i == 0], which
    [Qeq_dec] supplies.) *)
Lemma mode_dichotomy :
  forall k : Mode, zero_mode k \/ nonzero_mode k.
Proof.
  intros k.
  destruct (Qeq_dec (k i0) 0) as [E0|N0]; [|right; exists i0; exact N0].
  destruct (Qeq_dec (k i1) 0) as [E1|N1]; [|right; exists i1; exact N1].
  destruct (Qeq_dec (k i2) 0) as [E2|N2]; [|right; exists i2; exact N2].
  destruct (Qeq_dec (k i3) 0) as [E3|N3]; [|right; exists i3; exact N3].
  left. intros i. destruct i; assumption.
Qed.

(** THE THEOREM.  For an arbitrary mode [k] and an arbitrary closed 1-form at
    that mode, either [k] is the zero mode -- and then the form need not be
    exact, which is exactly where the four classes live -- or [k] is nonzero and
    the form IS exact, contributing nothing.

    No truncation appears anywhere in the statement, so it holds for every N
    simultaneously.  The Forge gate's finding that the gap is 4 at N = 0,1,2,3
    and carried entirely by the zero mode is the N <= 3 shadow of this. *)
Theorem gap_is_carried_entirely_by_the_zero_mode :
  forall k A B, closed k A B ->
    (zero_mode k) \/ (exact_form k A B).
Proof.
  intros k A B Hc.
  destruct (mode_dichotomy k) as [Hz|Hnz].
  - left. exact Hz.
  - right. exact (nonzero_mode_contributes_no_class k A B Hnz Hc).
Qed.

(** And the zero mode really does carry something: a nonzero constant 1-form is
    closed but not exact.  Concretely, uniform translation X = d/dq1 on T^4 --
    deterministic, reversible, volume preserving globally and per degree of
    freedom, preserving omega -- admits no global Hamiltonian. *)
Definition unit_form (d : Idx) : Form :=
  fun j => match j, d with
           | i0, i0 | i1, i1 | i2, i2 | i3, i3 => 1
           | _, _ => 0
           end.

Definition zero_form : Form := fun _ => 0.

Theorem translation_is_closed_but_not_exact :
  forall k, zero_mode k ->
    closed k (unit_form i0) zero_form /\ ~ exact_form k (unit_form i0) zero_form.
Proof.
  intros k Hz. split.
  - apply closed_at_zero_mode. exact Hz.
  - intros Hex.
    pose proof (proj1 (exact_at_zero_mode_iff_vanishing k (unit_form i0) zero_form Hz) Hex)
      as Hvanish.
    destruct (Hvanish i0) as [HA _].
    (* HA : unit_form i0 i0 == 0, i.e. 1 == 0 *)
    compute in HA. discriminate HA.
Qed.

(** ** The honest ledger

    Every theorem this file claims must be closed under the global context: no
    axioms, no parameters, no admits.  The gate counts these and rejects unless
    all of them report "Closed under the global context". *)

Print Assumptions exact_implies_closed.
Print Assumptions closed_at_zero_mode.
Print Assumptions exact_at_zero_mode_iff_vanishing.
Print Assumptions zero_mode_has_four_independent_classes.
Print Assumptions closed_iff_exact_at_nonzero.
Print Assumptions nonzero_mode_contributes_no_class.
Print Assumptions mode_dichotomy.
Print Assumptions gap_is_carried_entirely_by_the_zero_mode.
Print Assumptions translation_is_closed_but_not_exact.
