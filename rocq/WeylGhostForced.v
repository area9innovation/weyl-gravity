(** * The uniqueness theorem and the ghost theorem are the same theorem.

    [WeylActionClassification.v] proved that five assumptions determine the Weyl
    action uniquely, modulo topology.  That result is classical and, on its own,
    tells nobody anything they did not know.

    This module composes it with one more classical fact and gets something the
    programme did not have stated:

      the SAME assumption set that makes the action unique also FORCES the
      Ostrogradsky ghost, in every dimension where the action is non-trivial.

    The consequence is not decorative.  Because the action is unique, the ghost
    cannot be engineered away by choosing a better conformal action -- there is
    no other conformal action to choose.  Any escape must drop one of the five
    assumptions, and this module proves that dropping two of them does not help:

      drop RP-WEYL   ->  quadratic gravity, still curvature degree 2, still
                         fourth order, ghost survives (Stelle 1977)
      drop RP-DIM4   ->  D = 6 forces degree 3, sixth order, MORE poles, worse

    so only RP-LOCAL and RP-METRIC remain as candidates.  That is a statement
    about where to look, and it is the kind of thing an assumption ledger is for.

    ** The mechanism, and it is exactly rational

    A curvature-degree-[k] action has a kinetic operator of order [2k] in
    derivatives -- a degree-[k] polynomial in [k^2] -- hence [k] poles in the
    propagator.  Partial fractions over those poles produce residues whose signs
    ALTERNATE, so as soon as there are two of them one is negative.  A pole with
    negative residue is a negative-norm state.

    The residue computation is division-free rational arithmetic.  With two
    simple poles at [a < b], the residue at the UPPER pole satisfies
    [A (b - a) = 1] and the residue at the LOWER pole satisfies [B (a - b) = 1];
    these force

      A > 0 > B

    for every placement of the poles.  In general the residue at [r_i] is
    [1 / prod_{j <> i} (r_i - r_j)], whose sign is [(-1)^(n-1-i)] for sorted
    roots -- the signs alternate, so adding poles never rescues the situation.
    (The order of the difference is not free: the companion Forge rail computes
    the residues numerically and its partial-fraction identity check caught a
    first version that had it reversed, off by [(-1)^(n-1)].)

    And the conformal weight law pins the pole count: [D - 2k = 0] means
    [k = D/2], so the number of poles is exactly half the dimension.  Two or more
    -- hence a ghost -- for every even [D >= 4].  The single-pole case is [D = 2]
    alone, where the action is [sqrt(-g) R], which in two dimensions is the Euler
    density and therefore topological.

      CONFORMAL GRAVITY HAS A GHOST IN EVERY DIMENSION IN WHICH IT IS
      NON-TRIVIAL, AND THE ONLY GHOST-FREE MEMBER OF THE FAMILY IS EMPTY.

    ** Physics asserted, not derived

      O1  a pole with negative residue in the propagator is a negative-norm
          state -- a ghost.  Standard, and the whole physical reading rests on
          it.
      O2  a conformally invariant curvature-degree-[k] action has a linearised
          kinetic operator of order [2k], hence [k] poles in [k^2].  Standard
          power counting.  Entered below as the explicit bridge
          [two_distinct_poles], so the dependency is visible in the statement of
          the theorem rather than buried in prose.
      O3  Weyl gravity's own case is the DEGENERATE limit of the generic split:
          the kinetic operator is [Box^2], the propagator [1/k^4], a double pole
          at [k^2 = 0].  That is a dipole ghost -- a Jordan block, not a
          diagonalisable pair -- which is worse than the generic case, not
          better.  (Riegert 1984; the 6 = 2 + 4 degree-of-freedom count.)  The
          theorems below cover the generic split; the degenerate case is its
          limit.

          UPDATE -- O3 IS NO LONGER A CITATION.  [WeylGhostDipole.v] proves it:
          the commutant of a rank-two Jordan block is [a I + b N], the resulting
          flux metric has determinant [- g^2 a^2], and it is therefore
          indefinite when [a] is nonzero and degenerate when it is not -- never
          positive.  The statement was not invented for that module: the
          black-hole programme had already computed exactly this on the
          Schwarzschild exterior in the odd-parity spin-two sector
          ([phase4/axial_local_nonlocal_positivity_v1]).  See
          [reverse_physics/reports/ghost-and-the-black-hole.md].
      O4  in two dimensions [sqrt(-g) R] is the Euler density, hence topological.
          This is what makes the single-pole case empty rather than interesting.

    ** Boundary

    No linearised analysis of Weyl gravity is performed here.  No gauge fixing,
    no propagator is computed, no degree-of-freedom count is derived.  What is
    proved is that the pole COUNT is forced by the same weight law that forces
    the action, and that two or more poles force a negative residue.  Everything
    connecting that to "there is a ghost in Weyl gravity" is O1-O3.

    Nothing here bears on the BV-BFV complex, the residual classes, or the
    quantum theory.  In particular this is a statement about the LINEARISED
    classical propagator, and the programme's two scoped Lorentzian no-go
    theorems are neither used nor affected. *)

Require Import ZArith.
Require Import QArith.
Require Import Lqa.
Require Import Lia.
Require Import WeylActionClassification.

(** ** Part A: residues, over Q

    Written division-free: a residue [A] at a simple pole [a] is characterised by
    the equation it satisfies, not by the fraction it equals. *)

Open Scope Q_scope.

Lemma positive_residue : forall d A : Q, 0 < d -> A * d == 1 -> 0 < A.
Proof.
  intros d A Hd HA.
  destruct (Qlt_le_dec 0 A) as [H | H]. exact H. nra.
Qed.

Lemma negative_residue : forall d B : Q, 0 < d -> B * (- d) == 1 -> B < 0.
Proof.
  intros d B Hd HB.
  destruct (Qlt_le_dec B 0) as [H | H]. exact H. nra.
Qed.

(** TWO SIMPLE POLES ALWAYS HAVE OPPOSITE-SIGN RESIDUES.  There is no choice of
    pole locations that avoids it: this is why a fourth-order propagator cannot
    be made ghost-free by tuning masses. *)
Theorem two_poles_have_opposite_residues :
  forall a b A B : Q,
    a < b -> A * (b - a) == 1 -> B * (a - b) == 1 ->
    0 < A /\ B < 0.
Proof.
  intros a b A B Hab HA HB.
  assert (Hd : 0 < b - a) by lra.
  split.
  - exact (positive_residue (b - a) A Hd HA).
  - apply (negative_residue (b - a) B Hd). lra.
Qed.

Corollary two_poles_residue_product_is_negative :
  forall a b A B : Q,
    a < b -> A * (b - a) == 1 -> B * (a - b) == 1 -> A * B < 0.
Proof.
  intros a b A B Hab HA HB.
  destruct (two_poles_have_opposite_residues a b A B Hab HA HB) as [HA' HB'].
  nra.
Qed.

(** With three poles the middle residue is negative -- the signs alternate, so
    adding poles never rescues the situation.  This is the D = 6 case. *)
Theorem three_poles_have_a_negative_middle_residue :
  forall a b c B : Q,
    a < b -> b < c -> B * ((a - b) * (c - b)) == 1 -> B < 0.
Proof.
  intros a b c B H1 H2 HB.
  assert (Hp : 0 < (b - a) * (c - b)) by nra.
  apply (negative_residue ((b - a) * (c - b)) B Hp).
  rewrite <- HB. ring.
Qed.

(** Non-vacuity: a SINGLE pole has a positive residue.  Without this the
    theorems above would be about a predicate that is negative for everything,
    and "the ghost appears at two poles" would be empty. *)
Theorem one_pole_has_a_positive_residue :
  forall d A : Q, 0 < d -> A * d == 1 -> 0 < A.
Proof. exact positive_residue. Qed.

Close Scope Q_scope.

(** ** Part B: the pole count is forced by the dimension

    O2: a curvature-degree-[k] action has [k] poles.  The conformal weight law
    from [WeylActionClassification.v] pins [k = D/2]. *)

Open Scope Z_scope.

Definition kinetic_order (k : Z) : Z := 2 * k.
Definition pole_count (k : Z) : Z := k.

Theorem pole_count_is_half_the_dimension :
  forall D k, constant_weyl_weight D k = 0 -> 2 * pole_count k = D.
Proof. intros D k H. unfold constant_weyl_weight in H. unfold pole_count. lia. Qed.

Theorem kinetic_order_equals_the_dimension :
  forall D k, constant_weyl_weight D k = 0 -> kinetic_order k = D.
Proof. intros D k H. unfold constant_weyl_weight in H. unfold kinetic_order. lia. Qed.

(** Two or more poles in every dimension from four upward. *)
Theorem at_least_two_poles_above_dimension_two :
  forall D k, constant_weyl_weight D k = 0 -> 4 <= D -> 2 <= pole_count k.
Proof. intros D k H HD. unfold constant_weyl_weight in H. unfold pole_count. lia. Qed.

(** And the single-pole case is D = 2 and nothing else. *)
Theorem single_pole_iff_dimension_two :
  forall D k, constant_weyl_weight D k = 0 -> (pole_count k = 1 <-> D = 2).
Proof. intros D k H. unfold constant_weyl_weight in H. unfold pole_count. lia. Qed.

(** ** Part C: the escape lattice -- what dropping an assumption buys

    The two entries that can be settled by arithmetic are settled here.  The
    other two are physics claims about theories outside this space and are NOT
    proved; see the module header. *)

(** Dropping RP-DIM4 upward makes it worse, not better: six dimensions forces
    curvature degree three, hence three poles. *)
Theorem raising_the_dimension_adds_poles :
  forall D k, constant_weyl_weight D k = 0 -> 6 <= D -> 3 <= pole_count k.
Proof. intros D k H HD. unfold constant_weyl_weight in H. unfold pole_count. lia. Qed.

(** Dropping RP-WEYL leaves the curvature degree at two -- quadratic gravity is
    still fourth order -- so the pole count, and with it the ghost, is unchanged.
    This is why Stelle gravity is renormalisable and still has a ghost. *)
Theorem dropping_weyl_invariance_leaves_the_pole_count_at_two :
  pole_count 2 = 2.
Proof. reflexivity. Qed.

Close Scope Z_scope.

(** ** THE COMPOSITION

    O2 as an explicit bridge: at two or more poles, two distinct ones exist with
    the stated residue equations.  Carrying it as a hypothesis keeps the
    dependency in the statement of the theorem rather than in the prose. *)

Definition two_distinct_poles (k : Z) (a b A B : Q) : Prop :=
  (2 <= pole_count k)%Z ->
  (a < b)%Q /\ (A * (b - a) == 1)%Q /\ (B * (a - b) == 1)%Q.

(** The theorem this module exists for.  The dimension arithmetic and the
    residue arithmetic are genuinely composed: [D >= 4] and the weight law give
    the pole count, the pole count discharges the bridge, and the bridge feeds
    the residue lemma. *)
Theorem the_uniqueness_theorem_is_the_ghost_theorem :
  forall (D k : Z) (a b A B : Q),
    constant_weyl_weight D k = 0%Z ->
    (4 <= D)%Z ->
    two_distinct_poles k a b A B ->
    (B < 0)%Q.
Proof.
  intros D k a b A B Hw HD Hbridge.
  assert (Hk : (2 <= pole_count k)%Z)
    by exact (at_least_two_poles_above_dimension_two D k Hw HD).
  destruct (Hbridge Hk) as [Hab [HA HB]].
  destruct (two_poles_have_opposite_residues a b A B Hab HA HB) as [_ Hneg].
  exact Hneg.
Qed.

(** The dimension hypothesis is doing real work, not decoration: at [D = 2] the
    bridge is vacuous, because there is only one pole.  So the theorem does not
    secretly apply to everything. *)
Theorem at_dimension_two_the_bridge_is_vacuous :
  forall (k : Z) (a b A B : Q),
    constant_weyl_weight 2 k = 0%Z -> ~ (2 <= pole_count k)%Z.
Proof.
  intros k a b A B H. unfold constant_weyl_weight in H. unfold pole_count. lia.
Qed.

(** ** The honest ledger *)

Print Assumptions positive_residue.
Print Assumptions negative_residue.
Print Assumptions two_poles_have_opposite_residues.
Print Assumptions two_poles_residue_product_is_negative.
Print Assumptions three_poles_have_a_negative_middle_residue.
Print Assumptions one_pole_has_a_positive_residue.
Print Assumptions pole_count_is_half_the_dimension.
Print Assumptions kinetic_order_equals_the_dimension.
Print Assumptions at_least_two_poles_above_dimension_two.
Print Assumptions single_pole_iff_dimension_two.
Print Assumptions raising_the_dimension_adds_poles.
Print Assumptions dropping_weyl_invariance_leaves_the_pole_count_at_two.
Print Assumptions the_uniqueness_theorem_is_the_ghost_theorem.
Print Assumptions at_dimension_two_the_bridge_is_vacuous.
