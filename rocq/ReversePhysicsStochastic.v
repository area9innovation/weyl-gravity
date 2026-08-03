(** * Testing the two assumptions the whole stream had been consuming.

    Every certificate in this stream lists [RP-DETERMINISTIC] and
    [RP-REVERSIBLE] under "consumed" and NONE has ever listed them under
    "under_test".  The reason is structural: on the Hamiltonian carriers every
    evolution is [exp(tA)], which is deterministic and invertible by
    construction, so those two assumptions could not fail there and therefore
    could not be tested.  This file supplies a carrier where they can fail.

    ** The carrier

    A finite state space with four states, and evolution by a column-stochastic
    matrix over Q acting on probability distributions.  This is the ensemble
    picture rather than the point picture -- closer to how Carcassi and Aidala
    set things up -- and it is exactly the setting in which non-determinism and
    irreversibility are expressible:

      - a NON-deterministic evolution spreads a point mass over several states;
      - an IRREVERSIBLE evolution merges distinct states.

    ** The assumptions, in this carrier

      [deterministic]           a point mass evolves to a point mass, i.e. the
                                matrix is the graph of a function f
      [conserves_information]   the uniform (maximum-entropy) ensemble is
                                stationary -- the discrete Liouville condition
      [reversible]              distinct states stay distinct, i.e. f is
                                injective

    ** The result

      [reversibility_is_not_independent]
          reversible  <->  deterministic /\ conserves_information

    So on this carrier REVERSIBILITY IS NOT AN INDEPENDENT POSTULATE.  It is
    forced by determinism together with information conservation, and conversely
    it implies both.  That is a reverse-physics statement about the assumption
    vocabulary this stream has been using -- and it retroactively explains why
    the Hamiltonian carriers could bake reversibility in without loss.

    Both conjuncts are independent: [collapse_is_deterministic_not_conserving]
    and [mixer_conserves_but_is_not_deterministic].

    ** Boundary

    Four states, rational entries, one time step.  Nothing here is about
    continuous state spaces, about entropy beyond the stationarity of the
    uniform ensemble, or about the Hamiltonian carriers of the other
    developments -- this file imports none of them. *)

Require Import QArith.
Require Import Lqa.

Open Scope Q_scope.

(** ** The carrier *)

Inductive St : Set := s0 | s1 | s2 | s3.

Definition st_eq_dec (x y : St) : {x = y} + {x <> y}.
Proof. decide equality. Defined.

Definition delta (i j : St) : Q := if st_eq_dec i j then 1 else 0.

Lemma delta_eq : forall i j, i = j -> delta i j == 1.
Proof. intros i j H. unfold delta. destruct (st_eq_dec i j); [reflexivity | contradiction]. Qed.

Lemma delta_ne : forall i j, i <> j -> delta i j == 0.
Proof. intros i j H. unfold delta. destruct (st_eq_dec i j); [contradiction | reflexivity]. Qed.

Lemma delta_nonneg : forall i j, 0 <= delta i j.
Proof. intros i j. unfold delta. destruct (st_eq_dec i j); lra. Qed.

Definition Mat := St -> St -> Q.

Definition sum4 (g : St -> Q) : Q := g s0 + g s1 + g s2 + g s3.
Definition col_sum (M : Mat) (j : St) : Q := sum4 (fun i => M i j).
Definition row_sum (M : Mat) (i : St) : Q := sum4 (fun j => M i j).

(** The graph of a function, as a matrix. *)
Definition dmat (f : St -> St) : Mat := fun i j => delta i (f j).

(** ** The assumptions *)

(** A point mass evolves to a point mass. *)
Definition det_map (M : Mat) (f : St -> St) : Prop := forall i j, M i j == dmat f i j.
Definition deterministic (M : Mat) : Prop := exists f, det_map M f.

(** The uniform (maximum-entropy) ensemble is stationary.  Applying M to the
    uniform distribution gives the vector of row sums divided by four, so this
    is exactly "every row sum is one" -- the discrete Liouville condition. *)
Definition conserves_information (M : Mat) : Prop := forall i, row_sum M i == 1.

(** Distinct states stay distinct. *)
Definition reversible (M : Mat) : Prop :=
  exists f, det_map M f /\ (forall x y, f x = f y -> x = y).

(** ** Bookkeeping *)

Lemma row_sum_congr :
  forall M N i, (forall a b, M a b == N a b) -> row_sum M i == row_sum N i.
Proof.
  intros M N i H. unfold row_sum, sum4.
  rewrite (H i s0), (H i s1), (H i s2), (H i s3). reflexivity.
Qed.

(** Every deterministic matrix is column-stochastic: probability is conserved
    forwards whether or not anything else is. *)
Lemma dmat_col_sum : forall f j, col_sum (dmat f) j == 1.
Proof.
  intros f j. unfold col_sum, sum4, dmat.
  destruct (f j); compute; reflexivity.
Qed.

(** The total mass of a deterministic matrix is four, however the rows fall. *)
Lemma dmat_total :
  forall f, row_sum (dmat f) s0 + row_sum (dmat f) s1
          + row_sum (dmat f) s2 + row_sum (dmat f) s3 == 4.
Proof.
  intros f.
  assert (H := dmat_col_sum f).
  unfold row_sum, col_sum, sum4 in *.
  pose proof (H s0) as C0. pose proof (H s1) as C1.
  pose proof (H s2) as C2. pose proof (H s3) as C3.
  lra.
Qed.

(** ** Information conservation forces injectivity *)

Theorem determinism_and_information_force_reversibility :
  forall M, deterministic M -> conserves_information M -> reversible M.
Proof.
  intros M [f Hf] Hu.
  exists f. split; [exact Hf |].
  intros x y Hxy.
  destruct (st_eq_dec x y) as [E | N]; [exact E |].
  (* x <> y but f x = f y: the fibre over f x has at least two elements, so its
     row sum is at least two, contradicting the row sum being one. *)
  exfalso.
  assert (R : row_sum (dmat f) (f x) == 1).
  { rewrite <- (row_sum_congr M (dmat f) (f x) Hf). apply Hu. }
  unfold row_sum, sum4, dmat in R.
  assert (Hx : delta (f x) (f x) == 1) by (apply delta_eq; reflexivity).
  assert (Hy : delta (f x) (f y) == 1) by (apply delta_eq; exact Hxy).
  assert (N0 := delta_nonneg (f x) (f s0)).
  assert (N1 := delta_nonneg (f x) (f s1)).
  assert (N2 := delta_nonneg (f x) (f s2)).
  assert (N3 := delta_nonneg (f x) (f s3)).
  destruct x; destruct y; try contradiction; simpl in *; lra.
Qed.

(** ** Injectivity forces information conservation *)

(** With f injective no state has two preimages, so no row sum exceeds one. *)
Lemma injective_row_sum_le_one :
  forall f, (forall x y, f x = f y -> x = y) ->
    forall i, row_sum (dmat f) i <= 1.
Proof.
  intros f Hinj i.
  unfold row_sum, sum4, dmat.
  destruct (st_eq_dec i (f s0)) as [E0 | N0];
  destruct (st_eq_dec i (f s1)) as [E1 | N1];
  destruct (st_eq_dec i (f s2)) as [E2 | N2];
  destruct (st_eq_dec i (f s3)) as [E3 | N3];
  repeat first
    [ rewrite (delta_eq i (f s0) E0)
    | rewrite (delta_ne i (f s0) N0)
    | rewrite (delta_eq i (f s1) E1)
    | rewrite (delta_ne i (f s1) N1)
    | rewrite (delta_eq i (f s2) E2)
    | rewrite (delta_ne i (f s2) N2)
    | rewrite (delta_eq i (f s3) E3)
    | rewrite (delta_ne i (f s3) N3) ];
  try lra;
  exfalso;
  repeat match goal with
  | [ A : i = f ?u, B : i = f ?v |- _ ] =>
      let H := fresh in
      assert (H : u = v) by (apply Hinj; rewrite <- A, <- B; reflexivity);
      discriminate H
  end.
Qed.

Theorem reversibility_forces_information_conservation :
  forall M, reversible M -> conserves_information M.
Proof.
  intros M [f [Hf Hinj]] i.
  rewrite (row_sum_congr M (dmat f) i Hf).
  assert (T := dmat_total f).
  assert (L0 := injective_row_sum_le_one f Hinj s0).
  assert (L1 := injective_row_sum_le_one f Hinj s1).
  assert (L2 := injective_row_sum_le_one f Hinj s2).
  assert (L3 := injective_row_sum_le_one f Hinj s3).
  destruct i; lra.
Qed.

(** ** THE RESULT *)

(** Reversibility is not an independent postulate on this carrier: it is exactly
    the conjunction of determinism and information conservation. *)
Theorem reversibility_is_not_independent :
  forall M, reversible M <-> (deterministic M /\ conserves_information M).
Proof.
  intros M. split.
  - intros Hr. split.
    + destruct Hr as [f [Hf _]]. exists f. exact Hf.
    + apply reversibility_forces_information_conservation. exact Hr.
  - intros [Hd Hu].
    apply determinism_and_information_force_reversibility; assumption.
Qed.

(** ** Both conjuncts are needed *)

(** Everything collapses to one state: deterministic, and information is
    destroyed.  Three states lose all their measure and one gains it. *)
Definition collapse : Mat := dmat (fun _ => s0).

Theorem collapse_is_deterministic_not_conserving :
  deterministic collapse /\ ~ conserves_information collapse /\ ~ reversible collapse.
Proof.
  split; [| split].
  - exists (fun _ => s0). intros i j. reflexivity.
  - intros H. specialize (H s1). compute in H. discriminate H.
  - intros H. apply reversibility_forces_information_conservation in H.
    specialize (H s1). compute in H. discriminate H.
Qed.

(** Uniform mixing: information is conserved -- the uniform ensemble is
    stationary -- but a point mass is smeared over every state, so evolution is
    not deterministic and the states are not kept apart. *)
Definition mixer : Mat := fun _ _ => 1 # 4.

Theorem mixer_conserves_but_is_not_deterministic :
  conserves_information mixer /\ ~ deterministic mixer /\ ~ reversible mixer.
Proof.
  split; [| split].
  - intros i. destruct i; compute; reflexivity.
  - intros [f Hf].
    (* the column over s0 would have to be a point mass, but every entry is 1/4 *)
    assert (H0 := Hf (f s0) s0).
    unfold mixer, dmat in H0.
    rewrite (delta_eq (f s0) (f s0) eq_refl) in H0.
    compute in H0. discriminate H0.
  - intros [f [Hf _]].
    assert (H0 := Hf (f s0) s0).
    unfold mixer, dmat in H0.
    rewrite (delta_eq (f s0) (f s0) eq_refl) in H0.
    compute in H0. discriminate H0.
Qed.

(** ** What this says about the stream's assumption vocabulary *)

(** [RP-REVERSIBLE] was carried as an independent postulate in every certificate
    of this stream.  On this carrier it is not one.  The honest reading is that
    the vocabulary was redundant: the pair (determinism, information
    conservation) already entails it, so listing reversibility separately
    overstated how many assumptions were in play. *)
Theorem reversibility_is_redundant_given_the_other_two :
  forall M, deterministic M -> conserves_information M -> reversible M.
Proof. apply determinism_and_information_force_reversibility. Qed.

(** ** The honest ledger *)

Print Assumptions dmat_col_sum.
Print Assumptions dmat_total.
Print Assumptions determinism_and_information_force_reversibility.
Print Assumptions injective_row_sum_le_one.
Print Assumptions reversibility_forces_information_conservation.
Print Assumptions reversibility_is_not_independent.
Print Assumptions collapse_is_deterministic_not_conserving.
Print Assumptions mixer_conserves_but_is_not_deterministic.
Print Assumptions reversibility_is_redundant_given_the_other_two.
