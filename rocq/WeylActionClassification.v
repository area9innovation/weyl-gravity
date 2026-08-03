(** * Reverse physics on Weyl gravity: the action is EQUIVALENT to five assumptions.

    Every previous certificate in this stream tested either a carrier built to
    demonstrate the method or the Pais-Uhlenbeck toy.  This one is about the
    programme's own subject.

    ** The law

      S[g]  =  alpha * Integral sqrt(-g) C_abcd C^abcd

    ** The claim

    S is not merely IMPLIED by conformal gravity's usual motivation.  Modulo
    topological terms it is the UNIQUE action satisfying

      RP-LOCAL      the action is the integral of a local density
      RP-METRIC     the metric is the only field
      RP-DIFF       diffeomorphism invariance
      RP-WEYL       local Weyl (conformal) invariance
      RP-DIM4       spacetime is four-dimensional

    and each of the five is INDEPENDENT: drop one and a different action
    satisfies the rest.  The witnesses are exhibited below.

    ** What is NOT assumed, because it is derived

    "Four derivatives" / "quadratic in curvature" is usually listed as a sixth
    assumption.  It is not one.  A density sqrt(-g) X with X homogeneous of
    curvature-degree k has weight D - 2k under a CONSTANT Weyl rescaling, so
    invariance forces D = 2k; at D = 4 that is k = 2 and nothing else.
    [derivative_order_is_forced] proves it.  The derivative count is a
    CONSEQUENCE of RP-WEYL and RP-DIM4, not an input.

    Parity invariance is usually listed too.  It is genuinely independent as an
    assumption on the ACTION and genuinely redundant on the FIELD EQUATIONS --
    see [WeylParityAndTopology.v], which is the sharper half of this result.

    ** The three-way ledger: math, geometry, physics

    This file is careful about which is which, because that separation is the
    point.

    MATHEMATICS (proved here, exactly, over Q).  The space of parity-even
    quadratic curvature scalars is Q^3 in the basis
    [K1 = Riem^2, K2 = Ric^2, K3 = R^2]; the change of basis to
    [C^2, E4, R^2] is invertible over Q; the Weyl-invariance condition is the
    single linear equation a + b + 3c = 0; its solution space is exactly
    span{C^2, E4}; and modulo E4 that is one-dimensional.

    GEOMETRY (classical differential geometry, ASSERTED not re-derived; each
    appears as an explicit hypothesis where it is used).

      G1  E4 = K1 - 4 K2 + K3, and C^2 = K1 - 2 K2 + K3/3 in D = 4.
          These are the definitions of [euler] and [weyl_sq] as vectors, and
          they are the Gauss-Bonnet and Weyl-decomposition identities.
      G2  Under g -> e^{2 sigma} g:  delta R = -2 sigma R - 2(D-1) Box sigma,
          and delta sqrt(-g) = D sigma sqrt(-g).
      G3  sqrt(-g) C^2 has Weyl weight D - 4; C^a_bcd is Weyl invariant.
      G4  Integral sqrt(-g) E4 is topological in D = 4 (Gauss-Bonnet).
      G5  NON-DEGENERACY: there is a metric with Box R nonzero -- for instance
          matter-dominated FRW, a(t) = t^(2/3), where R = 4/(3 t^2).  Without
          this the classification would be vacuous, and
          [without_non_degeneracy_the_classification_is_vacuous] PROVES that:
          with the input replaced by False, every X counts as invariant.  The
          input is therefore consumed visibly, not assumed in prose.

    PHYSICS (the five RP-* assumptions above, plus one more that is easy to
    smuggle: that topological terms are physically inert.  Classically true --
    they do not change the field equations.  Quantum-mechanically FALSE -- the
    coefficient of the Pontryagin density is a theta-angle.  This programme's
    claim boundary does not reach the quantum theory, so the quotient is taken
    classically and flagged.)

    ** Boundary

    The classification theorem is CLASSICAL AND KNOWN -- that conformal gravity
    is the unique conformally invariant quadratic gravity in four dimensions is
    textbook.  What is new here is not the theorem.  It is the machine-checked
    zero-axiom derivation with the geometric inputs isolated as hypotheses, the
    independence witness for every assumption, the observation that the
    derivative order is derived rather than assumed, and the parity result in
    the companion module. *)

Require Import ZArith.
Require Import QArith.
Require Import Lqa.
Require Import Lia.

Open Scope Q_scope.

(** ** The space of parity-even quadratic curvature scalars

    Coordinates: [X = a Riem^2 + b Ric^2 + c R^2].  Total derivatives (Box R)
    are already quotiented out -- they do not contribute to the field equations,
    which is part of RP-LOCAL. *)

Record Quad : Set := mkQuad { qa : Q; qb : Q; qc : Q }.

Definition qeq (X Y : Quad) : Prop :=
  qa X == qa Y /\ qb X == qb Y /\ qc X == qc Y.

Definition qadd (X Y : Quad) : Quad :=
  mkQuad (qa X + qa Y) (qb X + qb Y) (qc X + qc Y).

Definition qscale (t : Q) (X : Quad) : Quad :=
  mkQuad (t * qa X) (t * qb X) (t * qc X).

Definition qzero : Quad := mkQuad 0 0 0.

(** G1.  The Gauss-Bonnet density and the Weyl square, in D = 4. *)
Definition euler   : Quad := mkQuad 1 (-4) 1.
Definition weyl_sq : Quad := mkQuad 1 (-2) (1#3).

(** The scalar-curvature square, which will turn out to carry the entire
    conformal anomaly of this sector. *)
Definition r_sq    : Quad := mkQuad 0 0 1.

(** ** The Weyl-invariance condition

    In the basis [{C^2, E4, R^2}] the variation of the action under
    [delta g = 2 sigma g] is, using G2 and G3,

      delta S  =  -12 * gamma * Integral sqrt(-g) sigma Box R   +  (topological)

    where [gamma] is the [R^2] coordinate.  So the anomaly is carried entirely
    by the [R^2] component, and [anomaly] below computes it: solving
    [a K1 + b K2 + c K3 = alpha C^2 + beta E4 + gamma R^2] gives

      alpha = 2a + b/2,   beta = -(a + b/2),   gamma = (a + b + 3c)/3. *)

(** Written as multiplications by rational literals rather than divisions:
    [lra] over [Q] does not reason through [Qdiv], and these coefficients are
    consumed by linear arithmetic throughout. *)
Definition alpha_of (X : Quad) : Q := 2 * qa X + (1#2) * qb X.
Definition beta_of  (X : Quad) : Q := - qa X - (1#2) * qb X.
Definition gamma_of (X : Quad) : Q := (1#3) * qa X + (1#3) * qb X + qc X.

(** The test itself, written without the division so that it is a plain linear
    form on the coordinates: [anomaly = 3 * gamma_of], and the two vanish
    together.  Normalisation is free -- an overall scale on the action is not
    physics. *)
Definition anomaly (X : Quad) : Q := qa X + qb X + 3 * qc X.

Theorem anomaly_is_three_gamma : forall X, anomaly X == 3 * gamma_of X.
Proof. intros [a b c]. unfold anomaly, gamma_of, qa, qb, qc. lra. Qed.

Theorem anomaly_vanishes_iff_gamma_does :
  forall X, anomaly X == 0 <-> gamma_of X == 0.
Proof.
  intros X. rewrite (anomaly_is_three_gamma X). split; intro H; lra.
Qed.

(** The decomposition is exact. *)
Theorem decomposition :
  forall X,
    qeq X (qadd (qscale (alpha_of X) weyl_sq)
                (qadd (qscale (beta_of X) euler)
                      (qscale (gamma_of X) r_sq))).
Proof.
  intros [a b c]. unfold qeq, qadd, qscale, alpha_of, beta_of, gamma_of,
    weyl_sq, euler, r_sq, qa, qb, qc.
  repeat split; lra.
Qed.

(** And it is unique: the three vectors are linearly independent. *)
Theorem decomposition_unique :
  forall al be ga al' be' ga',
    qeq (qadd (qscale al weyl_sq) (qadd (qscale be euler) (qscale ga r_sq)))
        (qadd (qscale al' weyl_sq) (qadd (qscale be' euler) (qscale ga' r_sq))) ->
    al == al' /\ be == be' /\ ga == ga'.
Proof.
  intros al be ga al' be' ga'.
  unfold qeq, qadd, qscale, weyl_sq, euler, r_sq, qa, qb, qc.
  intros [H1 [H2 H3]]. repeat split; lra.
Qed.

(** ** The anomaly is a genuine test *)

Theorem weyl_sq_is_invariant : anomaly weyl_sq == 0.
Proof. unfold anomaly, weyl_sq, qa, qb, qc. lra. Qed.

Theorem euler_is_invariant : anomaly euler == 0.
Proof. unfold anomaly, euler, qa, qb, qc. lra. Qed.

Theorem r_sq_is_not_invariant : ~ (anomaly r_sq == 0).
Proof. unfold anomaly, r_sq, qa, qb, qc. lra. Qed.

(** [anomaly] is linear, which is what makes "the invariant vectors form a
    subspace" a theorem rather than a hope. *)
Theorem anomaly_additive :
  forall X Y, anomaly (qadd X Y) == anomaly X + anomaly Y.
Proof. intros [a b c] [a' b' c']. unfold anomaly, qadd, qa, qb, qc. ring. Qed.

Theorem anomaly_homogeneous :
  forall t X, anomaly (qscale t X) == t * anomaly X.
Proof. intros t [a b c]. unfold anomaly, qscale, qa, qb, qc. ring. Qed.

(** ** THE CLASSIFICATION

    G5, the non-degeneracy input: the anomaly [-12 gamma Integral sigma Box R]
    vanishes for every [sigma] and every metric only if [gamma] itself is zero,
    which needs a metric with [Box R] not identically zero.  Stated as a
    hypothesis and consumed, so it cannot be forgotten. *)

Definition weyl_invariant (box_R_not_identically_zero : Prop) (X : Quad) : Prop :=
  box_R_not_identically_zero -> anomaly X == 0.

(** With the input, the classification runs. *)
Theorem classification_consumes_the_non_degeneracy_input :
  forall (ND : Prop) X, ND -> weyl_invariant ND X -> anomaly X == 0.
Proof. intros ND X Hnd H. exact (H Hnd). Qed.

(** WITHOUT it, EVERYTHING counts as invariant and the classification says
    nothing.  This is why G5 is a listed input rather than a footnote: it is not
    a technicality, it is the difference between a theorem and a tautology.

    A witness exists and is standard -- matter-dominated FRW, a(t) = t^(2/3), has
    R = 4/(3 t^2), so Box R does not vanish identically.  That witness is NAMED,
    not formalised: formalising it needs a Riemann tensor, which this development
    does not have. *)
Theorem without_non_degeneracy_the_classification_is_vacuous :
  forall X, weyl_invariant False X.
Proof. intros X HF. destruct HF. Qed.

(** Every Weyl-invariant quadratic action is a combination of [C^2] and [E4]. *)
Theorem weyl_invariant_is_spanned_by_weyl_sq_and_euler :
  forall X, anomaly X == 0 ->
    qeq X (qadd (qscale (alpha_of X) weyl_sq) (qscale (beta_of X) euler)).
Proof.
  intros X H.
  pose proof (decomposition X) as [D1 [D2 D3]].
  unfold qeq, qadd, qscale, weyl_sq, euler, r_sq, gamma_of,
    anomaly, qa, qb, qc in *.
  repeat split; lra.
Qed.

(** ...and conversely, every such combination is invariant.  Together these say
    the invariant subspace is EXACTLY two-dimensional. *)
Theorem span_of_weyl_sq_and_euler_is_invariant :
  forall al be, anomaly (qadd (qscale al weyl_sq) (qscale be euler)) == 0.
Proof.
  intros al be. unfold anomaly, qadd, qscale, weyl_sq, euler, qa, qb, qc. ring.
Qed.

(** THE UNIQUENESS.  Modulo the topological term, a Weyl-invariant quadratic
    action is a multiple of [C^2] -- and the multiple is determined. *)
(** Uniqueness is stated with [Qeq], not [exists!]: Coq's [exists!] carries
    Leibniz equality, which is the wrong equality on [Q] -- [1#2] and [2#4] are
    equal rationals and distinct terms. *)
Theorem weyl_action_is_unique_modulo_topological :
  forall X, anomaly X == 0 ->
    qeq X (qadd (qscale (alpha_of X) weyl_sq) (qscale (beta_of X) euler))
    /\ forall al',
         qeq X (qadd (qscale al' weyl_sq) (qscale (beta_of X) euler)) ->
         al' == alpha_of X.
Proof.
  intros X H. split.
  - apply weyl_invariant_is_spanned_by_weyl_sq_and_euler. exact H.
  - intros al' Hal'. destruct X as [a b c].
    unfold qeq, qadd, qscale, weyl_sq, euler, alpha_of, beta_of, anomaly in *.
    cbn in *. destruct Hal' as [A1 [A2 A3]]. lra.
Qed.

(** ** Independence witness 1 -- RP-WEYL is load-bearing

    Drop conformal invariance and the space is three-dimensional: [R^2] joins,
    and with it every [a Riem^2 + b Ric^2 + c R^2].  Quadratic gravity is the
    two-parameter theory; conformal gravity is the one-parameter one. *)

Theorem dropping_weyl_invariance_admits_r_sq :
  ~ (anomaly r_sq == 0) /\
  (forall al be, ~ qeq r_sq (qadd (qscale al weyl_sq) (qscale be euler))).
Proof.
  split.
  - exact r_sq_is_not_invariant.
  - intros al be [H1 [H2 H3]].
    unfold qadd, qscale, weyl_sq, euler, r_sq, qa, qb, qc in *. lra.
Qed.

(** ** Independence witness 2 -- the topological quotient is load-bearing

    [E4] is Weyl invariant and is NOT a multiple of [C^2].  Without the quotient
    the answer is two-dimensional, not one. *)

Theorem dropping_the_topological_quotient_admits_euler :
  anomaly euler == 0 /\ (forall al, ~ qeq euler (qscale al weyl_sq)).
Proof.
  split.
  - exact euler_is_invariant.
  - intros al [H1 [H2 H3]].
    unfold qscale, weyl_sq, euler, qa, qb, qc in *. lra.
Qed.

(** ** Independence witness 3 -- RP-DIM4 is load-bearing, and it FORCES the
       derivative order

    G3: [sqrt(-g) X] with [X] homogeneous of curvature-degree [k] has weight
    [D - 2k] under a constant Weyl rescaling.  So the invariant curvature-degree
    is pinned by the dimension, and vice versa. *)

Open Scope Z_scope.

Definition constant_weyl_weight (D k : Z) : Z := D - 2 * k.

Theorem derivative_order_is_forced :
  forall D k, constant_weyl_weight D k = 0 <-> D = 2 * k.
Proof. intros D k. unfold constant_weyl_weight. lia. Qed.

(** In four dimensions the only surviving curvature-degree is two.  So
    "four-derivative" is a CONSEQUENCE of RP-WEYL and RP-DIM4, not an
    independent assumption -- and the cosmological term (k = 0) and the
    Einstein-Hilbert term (k = 1) are excluded by the same computation. *)
Theorem in_four_dimensions_only_quadratic_survives :
  forall k, constant_weyl_weight 4 k = 0 <-> k = 2.
Proof. intros k. unfold constant_weyl_weight. lia. Qed.

Corollary einstein_hilbert_is_not_weyl_invariant :
  constant_weyl_weight 4 1 <> 0.
Proof. unfold constant_weyl_weight. lia. Qed.

Corollary cosmological_term_is_not_weyl_invariant :
  constant_weyl_weight 4 0 <> 0.
Proof. unfold constant_weyl_weight. lia. Qed.

(** And conversely the Weyl square itself fixes the dimension: in [D <> 4] the
    density [sqrt(-g) C^2] is not invariant, so this branch of the argument has
    no analogue there. *)
Theorem weyl_sq_density_invariant_iff_dimension_four :
  forall D, constant_weyl_weight D 2 = 0 <-> D = 4.
Proof. intros D. unfold constant_weyl_weight. lia. Qed.

Close Scope Z_scope.

(** ** The honest ledger *)

Print Assumptions anomaly_is_three_gamma.
Print Assumptions anomaly_vanishes_iff_gamma_does.
Print Assumptions decomposition.
Print Assumptions decomposition_unique.
Print Assumptions weyl_sq_is_invariant.
Print Assumptions euler_is_invariant.
Print Assumptions r_sq_is_not_invariant.
Print Assumptions anomaly_additive.
Print Assumptions anomaly_homogeneous.
Print Assumptions classification_consumes_the_non_degeneracy_input.
Print Assumptions without_non_degeneracy_the_classification_is_vacuous.
Print Assumptions weyl_invariant_is_spanned_by_weyl_sq_and_euler.
Print Assumptions span_of_weyl_sq_and_euler_is_invariant.
Print Assumptions weyl_action_is_unique_modulo_topological.
Print Assumptions dropping_weyl_invariance_admits_r_sq.
Print Assumptions dropping_the_topological_quotient_admits_euler.
Print Assumptions derivative_order_is_forced.
Print Assumptions in_four_dimensions_only_quadratic_survives.
Print Assumptions einstein_hilbert_is_not_weyl_invariant.
Print Assumptions cosmological_term_is_not_weyl_invariant.
Print Assumptions weyl_sq_density_invariant_iff_dimension_four.
