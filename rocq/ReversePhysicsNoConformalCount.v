(** * The last branch falls: no informative conformally invariant DOF count.

    [ReversePhysicsConformalCount.v] closed the DENSITY branch of the
    Carcassi-Aidala degree-of-freedom counting trilemma by parity: in odd
    dimension no polynomial curvature scalar balances the volume weight, and a
    Cauchy surface is three-dimensional.  That left the NON-ADDITIVE branch --
    the one their quantum-measure resolution points at -- as the only place an
    answer could live.

    This file closes it too, and closes it without ever using additivity.

    ** The argument

    Work on FLAT space.  A Minkowski slice is certainly a physical
    configuration, so any proposed count must behave sensibly there.

    A dilation phi_lam(x) = lam x pulls the flat metric back to a CONSTANT
    rescaling of itself, phi_lam^* delta = lam^2 delta.  So for any count that
    is natural under diffeomorphisms and invariant under constant Weyl
    rescaling,

      mu(phi_lam U) = mu_{phi_lam^* delta}(U) = mu_{lam^2 delta}(U) = mu(U).

    Taking U to be the unit ball: every ball has the same count as the unit
    ball, whatever its radius.  Add monotonicity and mu({x}) = 1 and every
    nonempty bounded region is squeezed between 1 and that one constant.

    A quantity that assigns the same value to a ball of radius one and a ball of
    radius 10^100 is not counting anything.

    ** What this settles

    All three branches of the trilemma are now closed under conformal
    invariance: the density branch by parity, the counting branch because it
    carries no information, and the non-additive branch here.  Additivity is
    never used below, which is exactly why the non-additive resolution does not
    escape.

    The honest reading is not "the count is hard to construct".  It is that in a
    conformally invariant theory, "how many degrees of freedom are in this
    region" is not a well-posed question.

    ** Modelling boundary

    The geometric inputs -- that a dilation pulls the flat metric back to a
    constant multiple of itself, that balls are dilations of the unit ball, that
    a bounded region sits inside some ball and contains a point -- are stated as
    HYPOTHESES of the theorems, not derived from differential geometry here.
    Everything else is the group-action consequence.  Only CONSTANT rescalings
    are used, the same minimal input as the parity file. *)

Require Import QArith.
Require Import Lqa.

Open Scope Q_scope.

(** ** Step 1: naturality plus Weyl invariance give dilation invariance *)

(** [Metric] and [Region] are abstract; [scale lam m] is the metric [lam^2 m],
    [dil lam U] is the image of [U] under the dilation by [lam]. *)
Theorem dilation_invariance :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric),
    (* naturality: pushing the region forward equals pulling the metric back,
       and the pullback of flat under a dilation is a constant rescaling *)
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (* conformal invariance, constant factor *)
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    forall lam U, 0 < lam -> mu flat (dil lam U) == mu flat U.
Proof.
  intros Metric Region mu scale dil flat Hnat Hweyl lam U Hlam.
  rewrite (Hnat lam U Hlam). apply Hweyl. exact Hlam.
Qed.

(** ** Step 2: every ball has the count of the unit ball *)

Theorem every_ball_has_the_same_count :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric)
         (ball : Q -> Region),
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    (* balls are dilations of the unit ball *)
    (forall r, 0 < r -> ball r = dil r (ball 1)) ->
    forall r, 0 < r -> mu flat (ball r) == mu flat (ball 1).
Proof.
  intros Metric Region mu scale dil flat ball Hnat Hweyl Hball r Hr.
  rewrite (Hball r Hr).
  apply (dilation_invariance Metric Region mu scale dil flat Hnat Hweyl r (ball 1) Hr).
Qed.

(** ** Step 3: the collapse *)

(** Every nonempty bounded region is squeezed between a point and a ball, so its
    count lies in a fixed interval that does not depend on the region at all. *)
Theorem count_is_bounded_independently_of_the_region :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric)
         (ball : Q -> Region)
         (subs : Region -> Region -> Prop)
         (point : Region -> Region),
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    (forall r, 0 < r -> ball r = dil r (ball 1)) ->
    (* monotone *)
    (forall U V, subs U V -> mu flat U <= mu flat V) ->
    (* a point is a single DOF *)
    (forall U, mu flat (point U) == 1) ->
    (* a nonempty region contains a point and sits inside some ball *)
    (forall U, subs (point U) U) ->
    (forall U, exists r, 0 < r /\ subs U (ball r)) ->
    forall U, 1 <= mu flat U /\ mu flat U <= mu flat (ball 1).
Proof.
  intros Metric Region mu scale dil flat ball subs point
         Hnat Hweyl Hball Hmono Hpoint Hin Hbound U.
  destruct (Hbound U) as [r [Hr Hsub]].
  assert (Hlow : mu flat (point U) <= mu flat U) by (apply Hmono; apply Hin).
  rewrite (Hpoint U) in Hlow.
  assert (Hhigh : mu flat U <= mu flat (ball r)) by (apply Hmono; exact Hsub).
  assert (Heq : mu flat (ball r) == mu flat (ball 1))
    by (apply (every_ball_has_the_same_count Metric Region mu scale dil flat ball
                 Hnat Hweyl Hball r Hr)).
  split; [exact Hlow | rewrite <- Heq; exact Hhigh].
Qed.

(** ** THE REFUTATION *)

(** A count that cannot distinguish a ball of radius one from a ball of any
    other radius is not counting degrees of freedom.  Additivity appears nowhere
    above, which is precisely why the non-additive resolution does not escape. *)
Theorem no_informative_conformal_count :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric)
         (ball : Q -> Region),
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    (forall r, 0 < r -> ball r = dil r (ball 1)) ->
    forall r s, 0 < r -> 0 < s -> mu flat (ball r) == mu flat (ball s).
Proof.
  intros Metric Region mu scale dil flat ball Hnat Hweyl Hball r s Hr Hs.
  rewrite (every_ball_has_the_same_count Metric Region mu scale dil flat ball
             Hnat Hweyl Hball r Hr).
  symmetry.
  apply (every_ball_has_the_same_count Metric Region mu scale dil flat ball
           Hnat Hweyl Hball s Hs).
Qed.

(** The concrete form: a unit ball and a ball of radius 10^100 receive the same
    count.  Nothing about the numbers matters; they are there to make the
    failure legible. *)
Theorem a_unit_ball_and_a_cosmological_ball_count_the_same :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric)
         (ball : Q -> Region),
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    (forall r, 0 < r -> ball r = dil r (ball 1)) ->
    mu flat (ball 1) == mu flat (ball (10 ^ 100)).
Proof.
  intros Metric Region mu scale dil flat ball Hnat Hweyl Hball.
  apply (no_informative_conformal_count Metric Region mu scale dil flat ball
           Hnat Hweyl Hball 1 (10 ^ 100)); reflexivity.
Qed.

(** ** The honest ledger *)

Print Assumptions dilation_invariance.
Print Assumptions every_ball_has_the_same_count.
Print Assumptions count_is_bounded_independently_of_the_region.
Print Assumptions no_informative_conformal_count.
Print Assumptions a_unit_ball_and_a_cosmological_ball_count_the_same.
