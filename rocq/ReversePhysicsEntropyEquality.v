(** * No entropy production: the forward half, exactly.

    [ReversePhysicsSecondLaw.v] proved that a doubly stochastic evolution never
    increases purity, and left the EQUALITY case open, recording specifically
    that "reversible evolution PRESERVES purity exactly is not proved".

    This file proves it, and supplies the mechanism of the converse.

      [reversible_preserves_purity]   reversible ==> purity is preserved exactly
      [row_deficit]                   the purity lost in a row is exactly a sum
                                      of weighted squared differences
      [spreading_produces_entropy]    a row putting positive weight on two states
                                      with different probability has STRICTLY
                                      positive deficit

    ** Why a relabelling is entropy-neutral

    [sparse_square] is the whole reason: with the underlying map injective, at
    most one term of each row survives, so squaring the sum is the same as
    summing the squares.  Nothing is lost because nothing is mixed.

    ** What is NOT here: the converse

    The biconditional "no entropy production iff reversible" is NOT established.
    The forward direction is proved; the converse would need, from purity being
    preserved on a distribution with distinct entries:

      (a) extracting from the vanishing TOTAL deficit that each of the
          twenty-four nonnegative terms vanishes, hence that every row has at
          most one nonzero entry; then
      (b) reconstructing the permutation from row sparsity plus unit column
          sums.

    Step (a) was attempted and abandoned: the case analysis over (row, pair,
    pair) with the test distribution's values expanded exhausted memory.  A
    cheaper route exists -- keep the twenty-four terms opaque and split the sum
    once rather than per case -- but it is not done here.
    [spreading_produces_entropy] is the mathematical content of (a) stated
    positively and proved; the extraction and (b) are the remaining work.

    ** Boundary

    Four states, one step, Renyi-2 purity.  The same restrictions as the
    companion file; nothing here reaches Shannon entropy or the continuous
    carriers. *)

Require Import QArith.
Require Import Lqa.
Require Import ReversePhysicsStochastic.
Require Import ReversePhysicsSecondLaw.

Open Scope Q_scope.

(** ** Congruence bookkeeping *)

Lemma evolve_congr :
  forall M N p i, (forall a b, M a b == N a b) -> evolve M p i == evolve N p i.
Proof.
  intros M N p i H. unfold evolve, sum4.
  rewrite (H i s0), (H i s1), (H i s2), (H i s3). reflexivity.
Qed.

Lemma purity_congr :
  forall p q, (forall i, p i == q i) -> purity p == purity q.
Proof.
  intros p q H. unfold purity, sum4.
  rewrite (H s0), (H s1), (H s2), (H s3). reflexivity.
Qed.

(** ** A relabelling squares termwise *)

(** With the underlying map injective, at most one term of the row survives, so
    squaring the sum is the same as summing the squares.  This is the entire
    reason a permutation is entropy-neutral. *)
Lemma sparse_square :
  forall (f : St -> St) (p : St -> Q) (i : St),
    (forall x y, f x = f y -> x = y) ->
    (delta i (f s0) * p s0 + delta i (f s1) * p s1
     + delta i (f s2) * p s2 + delta i (f s3) * p s3)
    * (delta i (f s0) * p s0 + delta i (f s1) * p s1
       + delta i (f s2) * p s2 + delta i (f s3) * p s3)
    == delta i (f s0) * (p s0 * p s0) + delta i (f s1) * (p s1 * p s1)
     + delta i (f s2) * (p s2 * p s2) + delta i (f s3) * (p s3 * p s3).
Proof.
  intros f p i Hinj.
  destruct (st_eq_dec i (f s0)) as [E0 | N0];
  destruct (st_eq_dec i (f s1)) as [E1 | N1];
  destruct (st_eq_dec i (f s2)) as [E2 | N2];
  destruct (st_eq_dec i (f s3)) as [E3 | N3];
  repeat first
    [ rewrite (delta_eq i (f s0) E0) | rewrite (delta_ne i (f s0) N0)
    | rewrite (delta_eq i (f s1) E1) | rewrite (delta_ne i (f s1) N1)
    | rewrite (delta_eq i (f s2) E2) | rewrite (delta_ne i (f s2) N2)
    | rewrite (delta_eq i (f s3) E3) | rewrite (delta_ne i (f s3) N3) ];
  try ring;
  exfalso;
  repeat match goal with
  | [ A : i = f ?u, B : i = f ?v |- _ ] =>
      let H := fresh in
      assert (H : u = v) by (apply Hinj; rewrite <- A, <- B; reflexivity);
      discriminate H
  end.
Qed.

(** ** Reversible evolution produces no entropy *)

Theorem reversible_preserves_purity :
  forall M p, reversible M -> purity (evolve M p) == purity p.
Proof.
  intros M p Hr.
  destruct Hr as [f [Hf Hinj]].
  assert (C : purity (evolve M p) == purity (evolve (dmat f) p)).
  { apply purity_congr. intros i. apply evolve_congr. intros a b. apply Hf. }
  rewrite C. clear C.
  unfold purity, evolve, sum4, dmat.
  rewrite (sparse_square f p s0 Hinj), (sparse_square f p s1 Hinj),
          (sparse_square f p s2 Hinj), (sparse_square f p s3 Hinj).
  assert (K0 := dmat_col_sum f s0). assert (K1 := dmat_col_sum f s1).
  assert (K2 := dmat_col_sum f s2). assert (K3 := dmat_col_sum f s3).
  unfold col_sum, sum4, dmat in K0, K1, K2, K3.
  assert (E :
    delta s0 (f s0) * (p s0 * p s0) + delta s0 (f s1) * (p s1 * p s1)
      + delta s0 (f s2) * (p s2 * p s2) + delta s0 (f s3) * (p s3 * p s3)
    + (delta s1 (f s0) * (p s0 * p s0) + delta s1 (f s1) * (p s1 * p s1)
      + delta s1 (f s2) * (p s2 * p s2) + delta s1 (f s3) * (p s3 * p s3))
    + (delta s2 (f s0) * (p s0 * p s0) + delta s2 (f s1) * (p s1 * p s1)
      + delta s2 (f s2) * (p s2 * p s2) + delta s2 (f s3) * (p s3 * p s3))
    + (delta s3 (f s0) * (p s0 * p s0) + delta s3 (f s1) * (p s1 * p s1)
      + delta s3 (f s2) * (p s2 * p s2) + delta s3 (f s3) * (p s3 * p s3))
    == (delta s0 (f s0) + delta s1 (f s0) + delta s2 (f s0) + delta s3 (f s0))
         * (p s0 * p s0)
     + (delta s0 (f s1) + delta s1 (f s1) + delta s2 (f s1) + delta s3 (f s1))
         * (p s1 * p s1)
     + (delta s0 (f s2) + delta s1 (f s2) + delta s2 (f s2) + delta s3 (f s2))
         * (p s2 * p s2)
     + (delta s0 (f s3) + delta s1 (f s3) + delta s2 (f s3) + delta s3 (f s3))
         * (p s3 * p s3)) by ring.
  rewrite E, K0, K1, K2, K3. ring.
Qed.

(** ** Where the entropy comes from *)

(** The row deficit, as a sum of weighted squared differences.  This is
    [jensen4_identity] with the row sum set to one, and it is where all the
    content of the equality case lives: purity is lost exactly when a row puts
    weight on two states carrying different probability. *)
Definition row_deficit_expr (M : Mat) (p : St -> Q) (i : St) : Q :=
  M i s0 * M i s1 * ((p s0 - p s1) * (p s0 - p s1))
  + M i s0 * M i s2 * ((p s0 - p s2) * (p s0 - p s2))
  + M i s0 * M i s3 * ((p s0 - p s3) * (p s0 - p s3))
  + M i s1 * M i s2 * ((p s1 - p s2) * (p s1 - p s2))
  + M i s1 * M i s3 * ((p s1 - p s3) * (p s1 - p s3))
  + M i s2 * M i s3 * ((p s2 - p s3) * (p s2 - p s3)).

Lemma row_deficit :
  forall M p i,
    row_sum M i == 1 ->
    M i s0 * (p s0 * p s0) + M i s1 * (p s1 * p s1)
      + M i s2 * (p s2 * p s2) + M i s3 * (p s3 * p s3)
      - evolve M p i * evolve M p i
    == row_deficit_expr M p i.
Proof.
  intros M p i Hrow.
  assert (ID := jensen4_identity (M i s0) (M i s1) (M i s2) (M i s3)
                                 (p s0) (p s1) (p s2) (p s3)).
  unfold row_sum, sum4 in Hrow. rewrite Hrow in ID.
  unfold evolve, sum4, row_deficit_expr. lra.
Qed.

Lemma mul_pos2 : forall a b : Q, 0 < a -> 0 < b -> 0 < a * b.
Proof. intros. nra. Qed.

Lemma mul_pos3 : forall a b c : Q, 0 < a -> 0 < b -> 0 < c -> 0 < a * b * c.
Proof. intros a b c Ha Hb Hc. apply mul_pos2; [apply mul_pos2 |]; assumption. Qed.

Lemma sq_pos : forall x y : Q, ~ (x == y) -> 0 < (x - y) * (x - y).
Proof.
  intros x y H.
  destruct (Q_dec x y) as [[Hlt | Hgt] | Heq].
  - nra.
  - nra.
  - contradiction.
Qed.

(** SPREADING PRODUCES ENTROPY.  If a row puts positive weight on two states
    whose probabilities differ, that row's deficit is strictly positive -- so
    purity strictly drops.  This is the mechanism behind the converse: an
    evolution that produces no entropy cannot spread. *)
Theorem spreading_produces_entropy :
  forall M p i j k,
    (forall a b, 0 <= M a b) ->
    j <> k -> 0 < M i j -> 0 < M i k -> ~ (p j == p k) ->
    0 < row_deficit_expr M p i.
Proof.
  intros M p i j k Hnn Hjk Hj Hk Hp.
  assert (Hp' : ~ (p k == p j)) by (intro C; apply Hp; symmetry; exact C).
  assert (S := sq_pos (p j) (p k) Hp).
  assert (S' := sq_pos (p k) (p j) Hp').
  assert (R : forall u v, 0 <= M i u * M i v * ((p u - p v) * (p u - p v)))
    by (intros; apply mul_nonneg; [apply mul_nonneg; apply Hnn | apply sq_nonneg]).
  assert (R01 := R s0 s1). assert (R02 := R s0 s2). assert (R03 := R s0 s3).
  assert (R12 := R s1 s2). assert (R13 := R s1 s3). assert (R23 := R s2 s3).
  unfold row_deficit_expr.
  destruct j; destruct k; try contradiction;
    first
      [ assert (0 < M i s0 * M i s1 * ((p s0 - p s1) * (p s0 - p s1)))
          by (apply mul_pos3; assumption)
      | assert (0 < M i s0 * M i s2 * ((p s0 - p s2) * (p s0 - p s2)))
          by (apply mul_pos3; assumption)
      | assert (0 < M i s0 * M i s3 * ((p s0 - p s3) * (p s0 - p s3)))
          by (apply mul_pos3; assumption)
      | assert (0 < M i s1 * M i s2 * ((p s1 - p s2) * (p s1 - p s2)))
          by (apply mul_pos3; assumption)
      | assert (0 < M i s1 * M i s3 * ((p s1 - p s3) * (p s1 - p s3)))
          by (apply mul_pos3; assumption)
      | assert (0 < M i s2 * M i s3 * ((p s2 - p s3) * (p s2 - p s3)))
          by (apply mul_pos3; assumption) ];
    lra.
Qed.

(** ** The honest ledger *)

Print Assumptions evolve_congr.
Print Assumptions purity_congr.
Print Assumptions sparse_square.
Print Assumptions reversible_preserves_purity.
Print Assumptions row_deficit.
Print Assumptions mul_pos2.
Print Assumptions mul_pos3.
Print Assumptions sq_pos.
Print Assumptions spreading_produces_entropy.
