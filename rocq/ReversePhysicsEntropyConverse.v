(** * The converse: no entropy production forces reversibility.

    [ReversePhysicsEntropyEquality.v] proved that reversible evolution preserves
    purity exactly, and recorded the converse as NOT DONE -- the first attempt
    exhausted memory by case-splitting with the test distribution's values
    expanded.  This file takes the cheaper route named there: keep the deficit
    terms OPAQUE and split the sum ONCE rather than per case.

      [total_deficit]        purity p - purity (M p) = the sum of the four row
                             deficits, given unit row and column sums
      [row_is_point_mass]    a nonnegative row summing to one whose off-diagonal
                             products all vanish is a point mass
      [purity_preserved_forces_reversible]
                             preserving purity on ONE distribution with distinct
                             entries forces the evolution to be reversible
      [no_entropy_production_iff_reversible]
                             THE BICONDITIONAL

    ** Why one test distribution suffices

    The deficit is a sum of terms M_ij M_ik (p_j - p_k)^2.  If the test
    distribution has pairwise DISTINCT entries then no squared difference can be
    the vanishing factor, so the whole content falls on the coefficients.  A
    single such p detects every failure; no quantification over distributions is
    needed.

    ** Boundary

    Four states, one step, Renyi-2 purity -- the same restrictions as the
    companion files. *)

Require Import QArith.
Require Import Lqa.
Require Import ReversePhysicsStochastic.
Require Import ReversePhysicsSecondLaw.
Require Import ReversePhysicsEntropyEquality.

Open Scope Q_scope.

(** ** Cancellation *)

Lemma cancel_pos_r : forall a c : Q, 0 < c -> a * c == 0 -> a == 0.
Proof.
  intros a c Hc H.
  destruct (Q_dec a 0) as [[Hl | Hg] | He]; [nra | nra | exact He].
Qed.

Lemma cancel_pos_l : forall a c : Q, 0 < a -> a * c == 0 -> c == 0.
Proof.
  intros a c Ha H. apply (cancel_pos_r c a Ha). rewrite Qmult_comm. exact H.
Qed.

(** ** The total deficit *)

Lemma row_deficit_nonneg :
  forall M p i, (forall a b, 0 <= M a b) -> 0 <= row_deficit_expr M p i.
Proof.
  intros M p i Hnn. unfold row_deficit_expr.
  assert (R : forall u v, 0 <= M i u * M i v * ((p u - p v) * (p u - p v)))
    by (intros; apply mul_nonneg; [apply mul_nonneg; apply Hnn | apply sq_nonneg]).
  assert (R01 := R s0 s1). assert (R02 := R s0 s2). assert (R03 := R s0 s3).
  assert (R12 := R s1 s2). assert (R13 := R s1 s3). assert (R23 := R s2 s3).
  lra.
Qed.

(** Purity lost overall is purity lost row by row.  Column sums enter here and
    only here: they are what lets the input purity be rewritten as a double sum. *)
Lemma total_deficit :
  forall M p,
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity p - purity (evolve M p)
    == row_deficit_expr M p s0 + row_deficit_expr M p s1
     + row_deficit_expr M p s2 + row_deficit_expr M p s3.
Proof.
  intros M p Hcol Hrow.
  assert (D0 := row_deficit M p s0 (Hrow s0)).
  assert (D1 := row_deficit M p s1 (Hrow s1)).
  assert (D2 := row_deficit M p s2 (Hrow s2)).
  assert (D3 := row_deficit M p s3 (Hrow s3)).
  assert (K0 := Hcol s0). assert (K1 := Hcol s1).
  assert (K2 := Hcol s2). assert (K3 := Hcol s3).
  unfold col_sum, sum4 in K0, K1, K2, K3.
  assert (C : p s0 * p s0 + p s1 * p s1 + p s2 * p s2 + p s3 * p s3
    == (M s0 s0 * (p s0 * p s0) + M s0 s1 * (p s1 * p s1)
        + M s0 s2 * (p s2 * p s2) + M s0 s3 * (p s3 * p s3))
     + (M s1 s0 * (p s0 * p s0) + M s1 s1 * (p s1 * p s1)
        + M s1 s2 * (p s2 * p s2) + M s1 s3 * (p s3 * p s3))
     + (M s2 s0 * (p s0 * p s0) + M s2 s1 * (p s1 * p s1)
        + M s2 s2 * (p s2 * p s2) + M s2 s3 * (p s3 * p s3))
     + (M s3 s0 * (p s0 * p s0) + M s3 s1 * (p s1 * p s1)
        + M s3 s2 * (p s2 * p s2) + M s3 s3 * (p s3 * p s3))).
  { assert (E :
      (M s0 s0 * (p s0 * p s0) + M s0 s1 * (p s1 * p s1)
       + M s0 s2 * (p s2 * p s2) + M s0 s3 * (p s3 * p s3))
      + (M s1 s0 * (p s0 * p s0) + M s1 s1 * (p s1 * p s1)
         + M s1 s2 * (p s2 * p s2) + M s1 s3 * (p s3 * p s3))
      + (M s2 s0 * (p s0 * p s0) + M s2 s1 * (p s1 * p s1)
         + M s2 s2 * (p s2 * p s2) + M s2 s3 * (p s3 * p s3))
      + (M s3 s0 * (p s0 * p s0) + M s3 s1 * (p s1 * p s1)
         + M s3 s2 * (p s2 * p s2) + M s3 s3 * (p s3 * p s3))
      == (M s0 s0 + M s1 s0 + M s2 s0 + M s3 s0) * (p s0 * p s0)
       + (M s0 s1 + M s1 s1 + M s2 s1 + M s3 s1) * (p s1 * p s1)
       + (M s0 s2 + M s1 s2 + M s2 s2 + M s3 s2) * (p s2 * p s2)
       + (M s0 s3 + M s1 s3 + M s2 s3 + M s3 s3) * (p s3 * p s3)) by ring.
    rewrite E, K0, K1, K2, K3. ring. }
  unfold purity, sum4. lra.
Qed.

(** ** Each row deficit vanishes *)

Lemma each_row_deficit_zero :
  forall M p,
    (forall a b, 0 <= M a b) ->
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity (evolve M p) == purity p ->
    forall i, row_deficit_expr M p i == 0.
Proof.
  intros M p Hnn Hcol Hrow Heq i.
  assert (T := total_deficit M p Hcol Hrow).
  assert (N0 := row_deficit_nonneg M p s0 Hnn).
  assert (N1 := row_deficit_nonneg M p s1 Hnn).
  assert (N2 := row_deficit_nonneg M p s2 Hnn).
  assert (N3 := row_deficit_nonneg M p s3 Hnn).
  destruct i; lra.
Qed.

(** ** A distinguishing distribution *)

Definition p_test : St -> Q :=
  fun i => match i with
           | s0 => 1 # 10 | s1 => 2 # 10 | s2 => 3 # 10 | s3 => 4 # 10
           end.

Lemma p_test_is_a_distribution :
  p_test s0 + p_test s1 + p_test s2 + p_test s3 == 1.
Proof. compute. reflexivity. Qed.

Lemma p_test_sq_pos :
  forall j k, j <> k -> 0 < (p_test j - p_test k) * (p_test j - p_test k).
Proof.
  intros j k H. destruct j; destruct k; try contradiction; compute; reflexivity.
Qed.

(** ** No spreading *)

Lemma pair_products_vanish :
  forall M i,
    (forall a b, 0 <= M a b) ->
    row_deficit_expr M p_test i == 0 ->
    forall j k, j <> k -> M i j * M i k == 0.
Proof.
  intros M i Hnn Hzero j k Hjk.
  assert (R : forall u v, 0 <= M i u * M i v * ((p_test u - p_test v) * (p_test u - p_test v)))
    by (intros; apply mul_nonneg; [apply mul_nonneg; apply Hnn | apply sq_nonneg]).
  assert (R01 := R s0 s1). assert (R02 := R s0 s2). assert (R03 := R s0 s3).
  assert (R12 := R s1 s2). assert (R13 := R s1 s3). assert (R23 := R s2 s3).
  unfold row_deficit_expr in Hzero.
  (* each of the six terms is zero *)
  assert (Z01 : M i s0 * M i s1 * ((p_test s0 - p_test s1) * (p_test s0 - p_test s1)) == 0) by lra.
  assert (Z02 : M i s0 * M i s2 * ((p_test s0 - p_test s2) * (p_test s0 - p_test s2)) == 0) by lra.
  assert (Z03 : M i s0 * M i s3 * ((p_test s0 - p_test s3) * (p_test s0 - p_test s3)) == 0) by lra.
  assert (Z12 : M i s1 * M i s2 * ((p_test s1 - p_test s2) * (p_test s1 - p_test s2)) == 0) by lra.
  assert (Z13 : M i s1 * M i s3 * ((p_test s1 - p_test s3) * (p_test s1 - p_test s3)) == 0) by lra.
  assert (Z23 : M i s2 * M i s3 * ((p_test s2 - p_test s3) * (p_test s2 - p_test s3)) == 0) by lra.
  (* divide each by its strictly positive squared difference *)
  assert (P01 := cancel_pos_r _ _ (p_test_sq_pos s0 s1 ltac:(discriminate)) Z01).
  assert (P02 := cancel_pos_r _ _ (p_test_sq_pos s0 s2 ltac:(discriminate)) Z02).
  assert (P03 := cancel_pos_r _ _ (p_test_sq_pos s0 s3 ltac:(discriminate)) Z03).
  assert (P12 := cancel_pos_r _ _ (p_test_sq_pos s1 s2 ltac:(discriminate)) Z12).
  assert (P13 := cancel_pos_r _ _ (p_test_sq_pos s1 s3 ltac:(discriminate)) Z13).
  assert (P23 := cancel_pos_r _ _ (p_test_sq_pos s2 s3 ltac:(discriminate)) Z23).
  destruct j; destruct k; try contradiction;
    solve [ exact P01 | exact P02 | exact P03 | exact P12 | exact P13 | exact P23
          | rewrite Qmult_comm; assumption ].
Qed.

(** ** A row that cannot spread is a point mass *)

Lemma row_is_point_mass :
  forall M i,
    (forall a b, 0 <= M a b) ->
    row_sum M i == 1 ->
    (forall j k, j <> k -> M i j * M i k == 0) ->
    exists m, M i m == 1 /\ (forall k, k <> m -> M i k == 0).
Proof.
  intros M i Hnn Hrow Hpair.
  unfold row_sum, sum4 in Hrow.
  assert (A0 := Hnn i s0). assert (A1 := Hnn i s1).
  assert (A2 := Hnn i s2). assert (A3 := Hnn i s3).
  destruct (Qlt_le_dec 0 (M i s0)) as [H0 | H0].
  { exists s0. assert (E1 : M i s1 == 0)
      by (apply (cancel_pos_l _ _ H0); apply Hpair; discriminate).
    assert (E2 : M i s2 == 0)
      by (apply (cancel_pos_l _ _ H0); apply Hpair; discriminate).
    assert (E3 : M i s3 == 0)
      by (apply (cancel_pos_l _ _ H0); apply Hpair; discriminate).
    split; [lra | intros k Hk; destruct k; [contradiction | exact E1 | exact E2 | exact E3]]. }
  assert (E0 : M i s0 == 0) by lra.
  destruct (Qlt_le_dec 0 (M i s1)) as [H1 | H1].
  { exists s1. assert (E2 : M i s2 == 0)
      by (apply (cancel_pos_l _ _ H1); apply Hpair; discriminate).
    assert (E3 : M i s3 == 0)
      by (apply (cancel_pos_l _ _ H1); apply Hpair; discriminate).
    split; [lra | intros k Hk; destruct k; [exact E0 | contradiction | exact E2 | exact E3]]. }
  assert (E1 : M i s1 == 0) by lra.
  destruct (Qlt_le_dec 0 (M i s2)) as [H2 | H2].
  { exists s2. assert (E3 : M i s3 == 0)
      by (apply (cancel_pos_l _ _ H2); apply Hpair; discriminate).
    split; [lra | intros k Hk; destruct k; [exact E0 | exact E1 | contradiction | exact E3]]. }
  assert (E2 : M i s2 == 0) by lra.
  exists s3.
  split; [lra | intros k Hk; destruct k; [exact E0 | exact E1 | exact E2 | contradiction]].
Qed.

(** ** Reconstructing the permutation *)

(** The row carrying the one in column [j]. *)
Definition col_arg (M : Mat) (j : St) : St :=
  if Qeq_dec (M s0 j) 1 then s0
  else if Qeq_dec (M s1 j) 1 then s1
  else if Qeq_dec (M s2 j) 1 then s2 else s3.

(** ** THE CONVERSE *)

Theorem purity_preserved_forces_reversible :
  forall M,
    (forall a b, 0 <= M a b) ->
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity (evolve M p_test) == purity p_test ->
    reversible M.
Proof.
  intros M Hnn Hcol Hrow Heq.
  (* no row spreads *)
  assert (Hpair : forall i j k, j <> k -> M i j * M i k == 0).
  { intros i j k Hjk.
    apply (pair_products_vanish M i Hnn
             (each_row_deficit_zero M p_test Hnn Hcol Hrow Heq i) j k Hjk). }
  (* every entry is zero or one *)
  assert (Hzo : forall i j, M i j == 0 \/ M i j == 1).
  { intros i j.
    destruct (row_is_point_mass M i Hnn (Hrow i) (fun a b h => Hpair i a b h))
      as [m [Hm Hoth]].
    destruct (st_eq_dec j m) as [E | N].
    - right. rewrite E. exact Hm.
    - left. apply Hoth. exact N. }
  (* every column carries exactly one one, so col_arg finds it *)
  assert (Hcolone : forall j, M (col_arg M j) j == 1 /\
                              forall i, i <> col_arg M j -> M i j == 0).
  { intros j.
    assert (K := Hcol j). unfold col_sum, sum4 in K.
    unfold col_arg.
    destruct (Qeq_dec (M s0 j) 1) as [Q0 | Q0].
    { split; [exact Q0 |].
      destruct (Hzo s1 j) as [z1 | o1]; destruct (Hzo s2 j) as [z2 | o2];
      destruct (Hzo s3 j) as [z3 | o3];
        try (exfalso; lra);
        intros i Hi; destruct i; solve [ contradiction | assumption ]. }
    destruct (Hzo s0 j) as [z0 | o0]; [| contradiction].
    destruct (Qeq_dec (M s1 j) 1) as [Q1 | Q1].
    { split; [exact Q1 |].
      destruct (Hzo s2 j) as [z2 | o2]; destruct (Hzo s3 j) as [z3 | o3];
        try (exfalso; lra);
        intros i Hi; destruct i; solve [ contradiction | assumption ]. }
    destruct (Hzo s1 j) as [z1 | o1]; [| contradiction].
    destruct (Qeq_dec (M s2 j) 1) as [Q2 | Q2].
    { split; [exact Q2 |].
      destruct (Hzo s3 j) as [z3 | o3];
        try (exfalso; lra);
        intros i Hi; destruct i; solve [ contradiction | assumption ]. }
    destruct (Hzo s2 j) as [z2 | o2]; [| contradiction].
    destruct (Hzo s3 j) as [z3 | o3]; [exfalso; lra |].
    split; [exact o3 |].
    intros i Hi; destruct i; solve [ contradiction | assumption ]. }
  (* the reconstructed map is the graph of M, and it is injective *)
  exists (col_arg M). split.
  - intros i j. unfold dmat.
    destruct (Hcolone j) as [Hone Hzero].
    destruct (st_eq_dec i (col_arg M j)) as [E | N].
    + rewrite (delta_eq i (col_arg M j) E), E. exact Hone.
    + rewrite (delta_ne i (col_arg M j) N). apply Hzero. exact N.
  - intros x y Hxy.
    destruct (st_eq_dec x y) as [E | N]; [exact E | exfalso].
    destruct (Hcolone x) as [Hx _]. destruct (Hcolone y) as [Hy _].
    rewrite <- Hxy in Hy.
    assert (Z := Hpair (col_arg M x) x y N).
    rewrite Hx, Hy in Z. compute in Z. discriminate Z.
Qed.

(** THE BICONDITIONAL.  Reversible evolution produces no entropy, and nothing
    else does.  The loop between this stream's two laws is closed. *)
Theorem no_entropy_production_iff_reversible :
  forall M,
    (forall a b, 0 <= M a b) ->
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    (reversible M <-> purity (evolve M p_test) == purity p_test).
Proof.
  intros M Hnn Hcol Hrow. split.
  - intros Hr. apply reversible_preserves_purity. exact Hr.
  - intros Heq. apply purity_preserved_forces_reversible; assumption.
Qed.

(** ** The honest ledger *)

Print Assumptions cancel_pos_r.
Print Assumptions cancel_pos_l.
Print Assumptions row_deficit_nonneg.
Print Assumptions total_deficit.
Print Assumptions each_row_deficit_zero.
Print Assumptions p_test_sq_pos.
Print Assumptions pair_products_vanish.
Print Assumptions row_is_point_mass.
Print Assumptions purity_preserved_forces_reversible.
Print Assumptions no_entropy_production_iff_reversible.
