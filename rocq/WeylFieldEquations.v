(** * The other half: reverse physics on the FIELD EQUATIONS.

    [WeylActionClassification.v] and [WeylParityAndTopology.v] classified the
    ACTION.  A physicist works with the field equation, and the assumption list
    looks different there.  This module does that side, and records what the
    translation costs.

    ** The two ledgers

      on the ACTION                      on the FIELD EQUATIONS
      ---------------------------------  ---------------------------------
      RP-LOCAL                           RP-LOCAL
      RP-METRIC                          RP-METRIC
      RP-DIFF                            RP-DIFF
      RP-WEYL   (action Weyl invariant)  RP-TRACELESS  (equations traceless)
      RP-DIM4                            RP-DIM4
      RP-TOPO-INERT                      -- not needed: topological terms have
                                            no field equations at all
                                         RP-DIVFREE -- NOT an assumption; see N1

    Both select the same one-dimensional space, whose generator is the Bach
    tensor.  Two things are worth saying about the translation.

    First, the topological quotient DISAPPEARS.  On the action side it is an
    assumption with an independence witness (the Euler density).  On the field
    equation side it is nothing at all: the variation of a topological term
    vanishes identically, so the quotient has already been taken by the time you
    write down an equation.  An assumption in one vocabulary is invisible in the
    other.

    Second, divergence-freedom is FREE.  It is a consequence of RP-DIFF via
    Noether's second theorem, so it cannot be dropped while keeping RP-DIFF and
    therefore has no independence witness.  It does not belong in the ledger as
    an assumption, even though it is always quoted as a property of the Bach
    tensor.

    ** Geometry asserted, not re-derived

      N1  (Noether, diffeomorphisms)  the metric variation of a local
          diff-invariant action is identically divergence-free.
      N2  (Noether, Weyl)  the TRACE of the metric variation is proportional to
          the conformal anomaly of the action, with a nonzero constant of
          proportionality.  This is the bridge between the two ledgers, and the
          nonzero-ness is load-bearing: [with_zero_kappa_tracelessness_is_vacuous]
          proves that if the constant vanished, every action would have traceless
          field equations and RP-TRACELESS would select nothing.
      N3  a topological term has identically vanishing metric variation.  This is
          RP-TOPO-INERT, and it is what makes the quotient disappear.

    ** Boundary

    The Bach tensor is never computed here.  Nothing in this development
    evaluates a metric variation; what is proved is that the SPACE of field
    equations reachable from this action space is one-dimensional, and that the
    two assumption vocabularies pick out the same line.  Calling its generator
    "the Bach tensor" is an identification made in the prose, on the strength of
    N1-N3, not a theorem here. *)

Require Import ZArith.
Require Import QArith.
Require Import Lqa.
Require Import Lia.
Require Import WeylActionClassification.
Require Import WeylParityAndTopology.

Open Scope Q_scope.

(** ** N2: the trace of the field equations

    [kappa] is the constant of proportionality.  It is carried explicitly rather
    than set to 1, so that its non-vanishing is visible as a hypothesis. *)

Definition trace_of (kappa : Q) (X : Quad4) : Q := kappa * anomaly4 X.

(** RP-TRACELESS on the field equations IS RP-WEYL on the action. *)
Theorem traceless_iff_action_is_weyl_invariant :
  forall kappa X, ~ kappa == 0 ->
    (trace_of kappa X == 0 <-> anomaly4 X == 0).
Proof.
  intros kappa X Hk. unfold trace_of. split.
  - intro H. destruct (Qmult_integral kappa (anomaly4 X) H) as [Hc | Ha].
    + contradiction.
    + exact Ha.
  - intro H. rewrite H. ring.
Qed.

(** And the bridge is load-bearing.  If N2's constant vanished, every action
    would have traceless field equations and the assumption would select
    nothing -- the same shape of check as G5 on the action side. *)
Theorem with_zero_kappa_tracelessness_is_vacuous :
  forall X, trace_of 0 X == 0.
Proof. intros X. unfold trace_of. ring. Qed.

(** ** The field-equation classification

    Every action whose field equations are traceless has the field equations of a
    multiple of the Weyl action.  With N1 supplying divergence-freedom and N3
    collapsing the topological directions, that line is the Bach equation. *)

Theorem traceless_field_equations_are_bach :
  forall kappa X, ~ kappa == 0 -> trace_of kappa X == 0 ->
    exists al : Q, same_field_equations X (q4scale al weyl_sq4).
Proof.
  intros kappa X Hk Ht.
  apply classification_survives_dropping_parity.
  apply (traceless_iff_action_is_weyl_invariant kappa X Hk). exact Ht.
Qed.

(** The two vocabularies pick out the same line, in both directions. *)
Theorem the_two_ledgers_agree :
  forall kappa X, ~ kappa == 0 ->
    (trace_of kappa X == 0 <-> exists al : Q, same_field_equations X (q4scale al weyl_sq4)).
Proof.
  intros kappa X Hk. split.
  - apply (traceless_field_equations_are_bach kappa X Hk).
  - intros [al Hal].
    apply (traceless_iff_action_is_weyl_invariant kappa X Hk).
    (* running the equivalence backwards: X differs from a multiple of C^2 by a
       topological term, and both C^2 and the topological generators have zero
       anomaly, so X does too. *)
    destruct X as [a b c p]. destruct Hal as [be [th [H1 [H2 [H3 H4]]]]].
    unfold anomaly4, q4sub, q4add, q4scale, weyl_sq4, euler4, pont in *.
    cbn in *. lra.
Qed.

(** ** RP-TOPO-INERT disappears on this side

    On the action side, dropping the topological quotient enlarges the answer
    from one dimension to two.  On the field-equation side there is nothing to
    drop: a topological term and zero have the same field equations, by N3. *)

Theorem topological_terms_have_the_field_equations_of_zero :
  forall be th : Q,
    same_field_equations (q4add (q4scale be euler4) (q4scale th pont))
                         (q4scale 0 weyl_sq4).
Proof.
  intros be th.
  unfold same_field_equations, topological, q4sub, q4eq, q4add, q4scale,
    euler4, pont, weyl_sq4. cbn.
  exists be, th. repeat split; lra.
Qed.

(** Non-vacuity, again: the Weyl action itself does NOT have the field equations
    of zero.  Without this the previous theorem would be about an empty theory. *)
Theorem the_weyl_action_has_nontrivial_field_equations :
  ~ same_field_equations weyl_sq4 (q4scale 0 weyl_sq4).
Proof.
  intros [be [th [H1 [H2 [H3 H4]]]]].
  unfold q4sub, q4add, q4scale, weyl_sq4, euler4, pont in *. cbn in *. lra.
Qed.

Close Scope Q_scope.

(** ** A prediction, and it is cheap to check

    The constant-Weyl weight of a curvature-degree-[k] density in [D] dimensions
    is [D - 2k], so a conformally invariant local curvature action exists only at
    [k = D/2].  In ODD dimension there is no such [k].

    So: no conformally invariant local action built polynomially from curvature
    exists in any odd-dimensional spacetime -- not at any derivative order.
    Weyl gravity is a four-dimensional accident in a precise sense. *)

Open Scope Z_scope.

Theorem no_conformal_curvature_action_in_odd_dimension :
  forall D k, Z.Odd D -> constant_weyl_weight D k <> 0.
Proof.
  intros D k [m Hm] H. unfold constant_weyl_weight in H. lia.
Qed.

(** ...and in even dimension there is exactly one degree, [k = D/2]. *)
Theorem exactly_one_degree_in_even_dimension :
  forall D, Z.Even D -> forall k, constant_weyl_weight D k = 0 <-> 2 * k = D.
Proof.
  intros D [m Hm] k. unfold constant_weyl_weight. lia.
Qed.

(** The four-dimensional case, and the six-dimensional one the next gate is
    about: quadratic in curvature at D = 4, CUBIC at D = 6. *)
Corollary degree_two_at_dimension_four :
  forall k, constant_weyl_weight 4 k = 0 <-> k = 2.
Proof. intros k. unfold constant_weyl_weight. lia. Qed.

Corollary degree_three_at_dimension_six :
  forall k, constant_weyl_weight 6 k = 0 <-> k = 3.
Proof. intros k. unfold constant_weyl_weight. lia. Qed.

(** This meets the conformal degree-of-freedom result from the other end.  There,
    no conformally invariant DOF DENSITY exists on an odd-dimensional slice,
    because curvature weights are always even and the volume weight is the
    dimension.  Here, no conformally invariant curvature ACTION exists in an
    odd-dimensional spacetime, because the weight is [D - 2k].

    Two different parity obstructions, two different objects, the same shape of
    conclusion -- and the four-dimensional case is where both are satisfied at
    once, by [C_abcd C^abcd]. *)

Close Scope Z_scope.

(** ** The honest ledger *)

Print Assumptions traceless_iff_action_is_weyl_invariant.
Print Assumptions with_zero_kappa_tracelessness_is_vacuous.
Print Assumptions traceless_field_equations_are_bach.
Print Assumptions the_two_ledgers_agree.
Print Assumptions topological_terms_have_the_field_equations_of_zero.
Print Assumptions the_weyl_action_has_nontrivial_field_equations.
Print Assumptions no_conformal_curvature_action_in_odd_dimension.
Print Assumptions exactly_one_degree_in_even_dimension.
Print Assumptions degree_two_at_dimension_four.
Print Assumptions degree_three_at_dimension_six.
