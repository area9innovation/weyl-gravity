(** * Parity in Weyl gravity: independent on the action, redundant on the field
      equations -- and physical again only in the quantum theory.

    [WeylActionClassification.v] classified the PARITY-EVEN quadratic curvature
    scalars.  Parity invariance is normally listed as one more assumption behind
    the Weyl action.  This module adds the parity-odd generator and asks whether
    that assumption is doing any work.

    The answer is the interesting kind: it depends on what you are classifying.

      on the space of ACTIONS        parity is INDEPENDENT
      on the space of FIELD EQUATIONS parity is REDUNDANT

    and the gap between the two is exactly a topological term -- classically
    inert, quantum-mechanically a gravitational theta-angle.  So the assumption
    is real, but the level at which it becomes physical is one this programme's
    claim boundary does not reach.

    ** Why this connects to the rest of the repository

    In four dimensions the Weyl tensor splits into self-dual and anti-self-dual
    parts, and

      C^2  =  W_+^2 + W_-^2          (parity even)
      P    =  W_+^2 - W_-^2          (parity odd, topological)

    so [W_+^2] and [W_-^2] -- the programme's two certified residual classes --
    are precisely the parity eigenbasis of this sector.  The result below says
    that the one-parameter family they span has, modulo topology, a single
    field equation: the Bach equation.  Parity invariance is the assumption
    that ties the two classes together, and it is free of charge classically.

    Per AGENTS.md these classes are centered deformation/vertex classes, not
    one-particle graviton states, and nothing here changes that.

    ** Geometry asserted, not re-derived

      G6  The parity-odd quadratic curvature invariants are spanned by the
          Pontryagin density P = R_abcd Rdual^abcd, and in four dimensions
          P = C_abcd Cdual^abcd (the Ricci parts drop out of the contraction).
      G7  Integral sqrt(-g) P is topological (the first Pontryagin number), hence
          Weyl invariant and with identically vanishing metric variation.
      G8  W_+^2 = (C^2 + P)/2 and W_-^2 = (C^2 - P)/2.

    ** Physics asserted, and flagged

      RP-TOPO-INERT  a topological term does not change the field equations.
                     Classically true.  QUANTUM-MECHANICALLY FALSE: the
                     coefficient of P is a theta-angle and is observable in
                     principle.  Everything called "redundant" below is
                     redundant only modulo this assumption. *)

Require Import QArith.
Require Import Lqa.

Open Scope Q_scope.

(** ** The four-dimensional space

    [X = a Riem^2 + b Ric^2 + c R^2 + p P].  The first three coordinates match
    [WeylActionClassification.v] exactly. *)

Record Quad4 : Set := mk4 { r4 : Q; c4 : Q; s4 : Q; p4 : Q }.

Definition q4eq (X Y : Quad4) : Prop :=
  r4 X == r4 Y /\ c4 X == c4 Y /\ s4 X == s4 Y /\ p4 X == p4 Y.

Definition q4add (X Y : Quad4) : Quad4 :=
  mk4 (r4 X + r4 Y) (c4 X + c4 Y) (s4 X + s4 Y) (p4 X + p4 Y).

Definition q4sub (X Y : Quad4) : Quad4 :=
  mk4 (r4 X - r4 Y) (c4 X - c4 Y) (s4 X - s4 Y) (p4 X - p4 Y).

Definition q4scale (t : Q) (X : Quad4) : Quad4 :=
  mk4 (t * r4 X) (t * c4 X) (t * s4 X) (t * p4 X).

Definition weyl_sq4 : Quad4 := mk4 1 (-2) (1#3) 0.
Definition euler4   : Quad4 := mk4 1 (-4) 1 0.
Definition pont     : Quad4 := mk4 0 0 0 1.

(** G8.  The two certified residual classes, as actions. *)
Definition w_plus  : Quad4 := mk4 (1#2) (-1) (1#6) (1#2).
Definition w_minus : Quad4 := mk4 (1#2) (-1) (1#6) (-(1#2)).

(** The parity-even anomaly test, unchanged: [P] is Weyl invariant (G7), so it
    contributes nothing. *)
Definition anomaly4 (X : Quad4) : Q := r4 X + c4 X + 3 * s4 X.

(** ** The eigenbasis identities *)

Theorem w_plus_plus_w_minus_is_weyl_sq :
  q4eq (q4add w_plus w_minus) weyl_sq4.
Proof. unfold q4eq, q4add, w_plus, w_minus, weyl_sq4. cbn. repeat split; lra. Qed.

Theorem w_plus_minus_w_minus_is_pontryagin :
  q4eq (q4sub w_plus w_minus) pont.
Proof. unfold q4eq, q4sub, w_plus, w_minus, pont. cbn. repeat split; lra. Qed.

(** Both chiral halves are Weyl invariant, so neither is excluded by RP-WEYL. *)
Theorem w_plus_is_weyl_invariant : anomaly4 w_plus == 0.
Proof. unfold anomaly4, w_plus. cbn. lra. Qed.

Theorem w_minus_is_weyl_invariant : anomaly4 w_minus == 0.
Proof. unfold anomaly4, w_minus. cbn. lra. Qed.

Theorem pontryagin_is_weyl_invariant : anomaly4 pont == 0.
Proof. unfold anomaly4, pont. cbn. lra. Qed.

(** ** Topological terms, and on-shell equivalence *)

(** The topological subspace: Gauss-Bonnet and Pontryagin. *)
Definition topological (X : Quad4) : Prop :=
  exists be th : Q, q4eq X (q4add (q4scale be euler4) (q4scale th pont)).

(** RP-TOPO-INERT.  Two actions differing by a topological term have the same
    field equations. *)
Definition same_field_equations (X Y : Quad4) : Prop := topological (q4sub X Y).

Theorem same_field_equations_refl : forall X, same_field_equations X X.
Proof.
  intros [a b c p]. unfold same_field_equations, topological, q4sub, q4eq,
    q4add, q4scale, euler4, pont. exists 0, 0. cbn. repeat split; lra.
Qed.

Theorem same_field_equations_sym :
  forall X Y, same_field_equations X Y -> same_field_equations Y X.
Proof.
  intros [a b c p] [a' b' c' p'] [be [th H]].
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    euler4, pont in *. cbn in *.
  exists (- be), (- th). destruct H as [H1 [H2 [H3 H4]]]. repeat split; lra.
Qed.

Theorem same_field_equations_trans :
  forall X Y Z, same_field_equations X Y -> same_field_equations Y Z ->
                same_field_equations X Z.
Proof.
  intros [a b c p] [a' b' c' p'] [a'' b'' c'' p''] [be [th H]] [be' [th' H']].
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    euler4, pont in *. cbn in *.
  exists (be + be'), (th + th').
  destruct H as [H1 [H2 [H3 H4]]]. destruct H' as [K1 [K2 [K3 K4]]].
  repeat split; lra.
Qed.

(** ** PARITY IS INDEPENDENT ON THE SPACE OF ACTIONS

    [W_+^2] is a Weyl-invariant action that is NOT a combination of the
    parity-even generators.  Assuming parity therefore genuinely removes
    something. *)

Theorem parity_is_independent_on_actions :
  anomaly4 w_plus == 0 /\
  forall al be : Q, ~ q4eq w_plus (q4add (q4scale al weyl_sq4) (q4scale be euler4)).
Proof.
  split.
  - exact w_plus_is_weyl_invariant.
  - intros al be [H1 [H2 [H3 H4]]].
    unfold q4add, q4scale, weyl_sq4, euler4, w_plus in *. cbn in *. lra.
Qed.

(** The whole chiral family is a genuine two-parameter family of actions: the
    map [(al, be) -> al W_+^2 + be W_-^2] is injective. *)
Theorem chiral_family_is_two_dimensional :
  forall al be al' be',
    q4eq (q4add (q4scale al w_plus) (q4scale be w_minus))
         (q4add (q4scale al' w_plus) (q4scale be' w_minus)) ->
    al == al' /\ be == be'.
Proof.
  intros al be al' be' [H1 [H2 [H3 H4]]].
  unfold q4add, q4scale, w_plus, w_minus in *. cbn in *. split; lra.
Qed.

(** ** PARITY IS REDUNDANT ON THE SPACE OF FIELD EQUATIONS

    Every chiral action has the same field equations as a multiple of [C^2].
    The two-parameter family of actions has a ONE-parameter family of field
    equations, and the fibre is the theta-angle direction. *)

Theorem parity_is_redundant_on_field_equations :
  forall al be : Q,
    same_field_equations
      (q4add (q4scale al w_plus) (q4scale be w_minus))
      (q4scale ((1#2) * (al + be)) weyl_sq4).
Proof.
  intros al be.
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    w_plus, w_minus, weyl_sq4, euler4, pont. cbn.
  exists 0, ((1#2) * (al - be)). repeat split; lra.
Qed.

(** The fibre is exactly one-dimensional and exactly the Pontryagin direction:
    two chiral actions have the same field equations iff their coefficients have
    the same sum. *)
Theorem chiral_actions_agree_on_shell_iff_same_sum :
  forall al be al' be' : Q,
    al + be == al' + be' ->
    same_field_equations
      (q4add (q4scale al w_plus) (q4scale be w_minus))
      (q4add (q4scale al' w_plus) (q4scale be' w_minus)).
Proof.
  intros al be al' be' Hsum.
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    w_plus, w_minus, euler4, pont. cbn.
  exists 0, ((1#2) * ((al - be) - (al' - be'))). repeat split; lra.
Qed.

(** ** The classification survives dropping parity

    Adding the parity-odd generator does not enlarge the answer: modulo
    topological terms, every Weyl-invariant quadratic action -- of either parity
    -- still has the field equations of a multiple of [C^2].  This is the
    statement that RP-PARITY may be deleted from the assumption list without
    changing the classical theory. *)

Theorem classification_survives_dropping_parity :
  forall X, anomaly4 X == 0 ->
    exists al : Q, same_field_equations X (q4scale al weyl_sq4).
Proof.
  intros [a b c p] H.
  unfold anomaly4 in H. cbn in H.
  exists (2 * a + (1#2) * b).
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    weyl_sq4, euler4, pont. cbn.
  exists (- a - (1#2) * b), p. repeat split; lra.
Qed.

(** ** Non-vacuity: the topological subspace is not everything

    Without this, "same field equations" would be trivially true of every pair
    and every theorem above would say nothing. *)

Theorem weyl_sq_is_not_topological : ~ topological weyl_sq4.
Proof.
  intros [be [th [H1 [H2 [H3 H4]]]]].
  unfold q4add, q4scale, weyl_sq4, euler4, pont in *. cbn in *. lra.
Qed.

Theorem w_plus_is_not_topological : ~ topological w_plus.
Proof.
  intros [be [th [H1 [H2 [H3 H4]]]]].
  unfold q4add, q4scale, w_plus, euler4, pont in *. cbn in *. lra.
Qed.

(** And the two topological generators are themselves independent, so the
    quotient really does remove two dimensions, not one. *)
Theorem euler_and_pontryagin_are_independent :
  forall be th : Q,
    q4eq (q4add (q4scale be euler4) (q4scale th pont)) (mk4 0 0 0 0) ->
    be == 0 /\ th == 0.
Proof.
  intros be th [H1 [H2 [H3 H4]]].
  unfold q4add, q4scale, euler4, pont in *. cbn in *. split; lra.
Qed.

(** ** The honest ledger *)

Print Assumptions w_plus_plus_w_minus_is_weyl_sq.
Print Assumptions w_plus_minus_w_minus_is_pontryagin.
Print Assumptions w_plus_is_weyl_invariant.
Print Assumptions w_minus_is_weyl_invariant.
Print Assumptions pontryagin_is_weyl_invariant.
Print Assumptions same_field_equations_refl.
Print Assumptions same_field_equations_sym.
Print Assumptions same_field_equations_trans.
Print Assumptions parity_is_independent_on_actions.
Print Assumptions chiral_family_is_two_dimensional.
Print Assumptions parity_is_redundant_on_field_equations.
Print Assumptions chiral_actions_agree_on_shell_iff_same_sum.
Print Assumptions classification_survives_dropping_parity.
Print Assumptions weyl_sq_is_not_topological.
Print Assumptions w_plus_is_not_topological.
Print Assumptions euler_and_pontryagin_are_independent.
