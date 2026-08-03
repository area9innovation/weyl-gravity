(** * The fourth desideratum: conformal invariance, and a parity obstruction.

    Carcassi and Aidala's talk (Reverse Physics for GR, Michigan, 16 Nov 2024)
    presents a TRILEMMA for counting degrees of freedom in a region U of a
    Cauchy surface:

      1. every point is a single DOF          mu({x}) = 1
      2. finite volume carries finitely many  mu(U) < infinity
      3. the count is additive                mu(union U_i) = sum mu(U_i)

    "Pick two!"  Their three resolutions: drop 1 and get a density (Lebesgue-
    like) measure, drop 2 and get the counting measure, drop 3 and get a
    non-additive "quantum measure".  For quantum mechanics they drop 3, and
    conjecture quantum gravity does the same for the DOF count.

    ** The fourth desideratum

    Conformal invariance is not a fourth item in the trilemma.  It is a FILTER on
    which resolutions are admissible: in a conformally invariant theory, a
    rescaling g -> Omega^2 g does not change the physical configuration, so it
    must not change the count.

    This file shows the filter is not idle.  It EXCLUDES the density branch --
    the one their GR proposal uses -- on a Cauchy surface, and it does so by
    parity rather than by accident.

    ** The obstruction

    Under a constant rescaling g -> Omega^2 g:

      g_ab -> Omega^2 g_ab          g^ab -> Omega^-2 g^ab
      R^a_bcd invariant, so R_abcd -> Omega^2 R_abcd

    A local scalar built polynomially from the metric, its inverse, the Riemann
    tensor and covariant derivatives is fixed, FOR WEIGHT PURPOSES, by two
    numbers: m curvature factors (four indices each) and D derivative indices.
    Every index is contracted in a pair, so 4m + D is even, hence D is even, and

      weight = 2m - 2 * (4m + D)/2 = -(2m + D),

    which is even.  The volume element on a d-manifold has weight +d.  A density
    mu(U) = integral over U of rho times dvol is conformally invariant exactly
    when the weights cancel, i.e. when 2m + D = d.  For ODD d that has no
    solution.

    A Cauchy surface is three-dimensional.  Three is odd.

    ** What this does and does not settle

    It settles the density branch, and only for densities built from the METRIC
    ALONE.  Introducing extra structure -- a compensator or dilaton of nonzero
    weight -- evades the parity argument, but only by choosing a scale, which is
    precisely what conformal invariance forbids.  That fork is real physics, not
    a loophole, and it is stated rather than hidden.

    Realisability is also not addressed: the arithmetic says which weights are
    available, not which (m, D) are actually realised by some invariant. *)

Require Import ZArith.
Require Import Lia.

Open Scope Z_scope.

(** ** Parity, self-contained *)

Definition even_nat (n : nat) : Prop := exists k, n = (2 * k)%nat.
Definition odd_nat (n : nat) : Prop := exists k, n = (2 * k + 1)%nat.
Definition even_Z (z : Z) : Prop := exists k, z = 2 * k.

(** ** Curvature scalars, for weight purposes only *)

(** [m] curvature factors and [D] derivative indices.  Every index must be
    contracted in a pair, which forces [D] even -- that is the only structural
    fact the argument uses. *)
Record CurvScalar : Set := mkCurv {
  cs_m : nat;
  cs_D : nat;
  cs_D_even : even_nat cs_D
}.

(** The conformal weight of such a scalar: +2 for each curvature factor,
    -2 for each of the (4m + D)/2 contractions. *)
Definition cs_weight (c : CurvScalar) : Z :=
  - Z.of_nat (2 * cs_m c + cs_D c).

(** ** Every curvature-scalar weight is even *)

Theorem curvature_scalar_weight_is_even :
  forall c, even_Z (cs_weight c).
Proof.
  intros [m D [k Hk]]. subst D. unfold cs_weight, even_Z. cbn [cs_m cs_D].
  exists (- (Z.of_nat m + Z.of_nat k)). lia.
Qed.

(** ** A conformally invariant density needs the weights to cancel *)

(** The volume element of a d-manifold has weight +d. *)
Definition volume_weight (d : nat) : Z := Z.of_nat d.

Definition is_conformal_density (d : nat) (c : CurvScalar) : Prop :=
  cs_weight c + volume_weight d = 0.

Lemma conformal_density_iff_balance :
  forall d c, is_conformal_density d c <-> (2 * cs_m c + cs_D c)%nat = d.
Proof.
  intros d c. destruct c as [m D HD].
  unfold is_conformal_density, cs_weight, volume_weight. cbn [cs_m cs_D].
  split; intros H; lia.
Qed.

(** ** THE OBSTRUCTION *)

Theorem conformal_density_forces_even_dimension :
  forall d c, is_conformal_density d c -> even_nat d.
Proof.
  intros d c H.
  apply conformal_density_iff_balance in H.
  destruct c as [m D [k Hk]]. cbn [cs_m cs_D] in H.
  unfold even_nat. exists (m + k)%nat. lia.
Qed.

Theorem no_conformal_density_in_odd_dimension :
  forall d, odd_nat d -> forall c, ~ is_conformal_density d c.
Proof.
  intros d [j Hj] c H.
  apply conformal_density_forces_even_dimension in H.
  destruct H as [i Hi]. lia.
Qed.

(** A Cauchy surface is three-dimensional, and three is odd.  So the density
    branch of the trilemma -- the branch their GR proposal uses, counting
    degrees of freedom by a spatial volume -- admits NO conformally invariant
    representative built from the metric alone. *)
Corollary no_conformal_dof_density_on_a_cauchy_surface :
  forall c, ~ is_conformal_density 3 c.
Proof.
  apply no_conformal_density_in_odd_dimension.
  unfold odd_nat. exists 1%nat. reflexivity.
Qed.

(** ** The even-dimensional counterpart *)

(** In even dimension the balance is achievable.  In dimension four it requires
    weight -4, i.e. 2m + D = 4 -- and the quadratic-curvature solution (m = 2,
    D = 0) is the weight carried by the Weyl-squared invariant, the conformally
    invariant action of the theory this repository studies.  So conformal
    gravity is precisely the even-dimensional case where a conformal density
    does exist; a Cauchy surface is the odd-dimensional case where it does not. *)
Theorem dimension_four_balance :
  forall c, is_conformal_density 4 c <-> (2 * cs_m c + cs_D c)%nat = 4%nat.
Proof. intros c. apply conformal_density_iff_balance. Qed.

Definition weyl_squared_weights : CurvScalar.
Proof. refine (mkCurv 2 0 _). unfold even_nat. exists 0%nat. reflexivity. Defined.

Theorem weyl_squared_is_a_conformal_density_in_dimension_four :
  is_conformal_density 4 weyl_squared_weights.
Proof. unfold is_conformal_density. compute. reflexivity. Qed.

Theorem weyl_squared_is_not_one_in_dimension_three :
  ~ is_conformal_density 3 weyl_squared_weights.
Proof. apply no_conformal_dof_density_on_a_cauchy_surface. Qed.

(** ** What survives the filter *)

(** The trilemma's three resolutions, filtered by conformal invariance:

      drop 1  a density measure     EXCLUDED in odd dimension, above
      drop 2  the counting measure  invariant (it never sees the metric) but
                                    uninformative: every infinite region gets
                                    the same value
      drop 3  a non-additive count  not excluded by this argument

    So an informative, conformally invariant degree-of-freedom count must be
    NON-ADDITIVE.  That is the same branch quantum mechanics forced them to, and
    it is forced here by a classical symmetry, with no quantum input at all.

    The formal content of that statement is the exclusion above; the reading of
    the other two branches is prose, and is not proved here. *)

(** ** The honest ledger *)

Print Assumptions curvature_scalar_weight_is_even.
Print Assumptions conformal_density_iff_balance.
Print Assumptions conformal_density_forces_even_dimension.
Print Assumptions no_conformal_density_in_odd_dimension.
Print Assumptions no_conformal_dof_density_on_a_cauchy_surface.
Print Assumptions dimension_four_balance.
Print Assumptions weyl_squared_is_a_conformal_density_in_dimension_four.
Print Assumptions weyl_squared_is_not_one_in_dimension_three.
