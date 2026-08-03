(** * A second law, on the carrier the first one left behind.

    Reverse physics pays off as a LATTICE of law/assumption pairs.  Everything in
    this stream so far concerns one law -- Hamiltonian privilege -- plus a
    side-result about the assumption vocabulary.  This file adds a second law on
    the finite-state stochastic carrier of [ReversePhysicsStochastic.v]:

      information conservation  ==>  disorder never decreases

    ** Why this is exactly rational

    The obvious statement of the second law needs Shannon entropy, whose
    logarithms are not rational and would break the exactness this whole stream
    depends on.  Two ways round it; this file takes the second.

      MAJORIZATION.  p is majorized by q exactly when p = Dq for a doubly
      stochastic D (Hardy--Littlewood--Polya).  Order-theoretic, no logarithms --
      but stating it needs sorting, which is heavy.

      PURITY.  sum_i p_i^2, the collision probability.  It is the exact rational
      content of the Renyi-2 entropy -log(sum p^2): since -log is monotone,
      "entropy does not decrease" IS "purity does not increase", with no
      logarithm anywhere.  Purity is Schur-convex, so this is the majorization
      statement evaluated on one Schur-convex functional.

    ** The result

      [purity_never_increases]  a doubly stochastic evolution never increases
                                purity, i.e. never decreases disorder
      [mixing_strictly_increases_disorder]  and the bound is attained strictly,
                                so the theorem is not vacuous

    ** The reverse-physics reading

    The two hypotheses are already in the vocabulary and are not new postulates:
    column sums one is conservation of probability (the evolution maps
    distributions to distributions), and row sums one is
    [conserves_information] -- stationarity of the uniform ensemble, the same
    condition that made reversibility redundant in the companion file.

    So on this carrier the second law is not an extra assumption.  It is a
    CONSEQUENCE of information conservation, and the two laws in this stream --
    Hamiltonian structure and the arrow of disorder -- turn out to consume the
    same assumption.

    ** Boundary

    Four states, one step, rational entries.  Renyi-2 only: nothing here is about
    Shannon entropy, about continuous state spaces, about many steps or
    equilibration, and nothing transfers to the Hamiltonian carriers. *)

Require Import QArith.
Require Import Lqa.
Require Import ReversePhysicsStochastic.

Open Scope Q_scope.

(** ** Evolving a distribution, and its purity *)

(** Transition probabilities are nonnegative.  (The companion file needed only
    the combinatorial structure and so never declared this; it is stated here
    because the second law is an inequality and genuinely uses it.) *)
Definition nonneg (M : Mat) : Prop := forall i j, 0 <= M i j.

Definition evolve (M : Mat) (p : St -> Q) : St -> Q :=
  fun i => sum4 (fun j => M i j * p j).

(** The collision probability.  Maximal (= 1) on a point mass, minimal on the
    uniform distribution: a direct, logarithm-free measure of order. *)
Definition purity (p : St -> Q) : Q := sum4 (fun i => p i * p i).

(** ** Jensen for four terms, as a polynomial identity *)

Lemma mul_nonneg : forall a b : Q, 0 <= a -> 0 <= b -> 0 <= a * b.
Proof. intros. nra. Qed.

Lemma sq_nonneg : forall x : Q, 0 <= x * x.
Proof. intros. nra. Qed.

(** The whole analytic content, with no analysis: the deficit between the mean
    of the squares and the square of the mean is a sum of weighted squared
    differences.  Stated with an unconstrained weight sum so that [ring] alone
    decides it. *)
Lemma jensen4_identity :
  forall w0 w1 w2 w3 x0 x1 x2 x3 : Q,
    (w0 + w1 + w2 + w3) * (w0*(x0*x0) + w1*(x1*x1) + w2*(x2*x2) + w3*(x3*x3))
      - (w0*x0 + w1*x1 + w2*x2 + w3*x3) * (w0*x0 + w1*x1 + w2*x2 + w3*x3)
    == w0*w1*((x0-x1)*(x0-x1)) + w0*w2*((x0-x2)*(x0-x2)) + w0*w3*((x0-x3)*(x0-x3))
     + w1*w2*((x1-x2)*(x1-x2)) + w1*w3*((x1-x3)*(x1-x3)) + w2*w3*((x2-x3)*(x2-x3)).
Proof. intros. ring. Qed.

Lemma jensen4_le :
  forall w0 w1 w2 w3 x0 x1 x2 x3 : Q,
    0 <= w0 -> 0 <= w1 -> 0 <= w2 -> 0 <= w3 ->
    w0 + w1 + w2 + w3 == 1 ->
    (w0*x0 + w1*x1 + w2*x2 + w3*x3) * (w0*x0 + w1*x1 + w2*x2 + w3*x3)
      <= w0*(x0*x0) + w1*(x1*x1) + w2*(x2*x2) + w3*(x3*x3).
Proof.
  intros w0 w1 w2 w3 x0 x1 x2 x3 H0 H1 H2 H3 Hs.
  assert (ID := jensen4_identity w0 w1 w2 w3 x0 x1 x2 x3).
  rewrite Hs in ID.
  assert (T01 : 0 <= w0*w1*((x0-x1)*(x0-x1)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  assert (T02 : 0 <= w0*w2*((x0-x2)*(x0-x2)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  assert (T03 : 0 <= w0*w3*((x0-x3)*(x0-x3)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  assert (T12 : 0 <= w1*w2*((x1-x2)*(x1-x2)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  assert (T13 : 0 <= w1*w3*((x1-x3)*(x1-x3)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  assert (T23 : 0 <= w2*w3*((x2-x3)*(x2-x3)))
    by (apply mul_nonneg; [apply mul_nonneg; assumption | apply sq_nonneg]).
  lra.
Qed.

(** ** THE SECOND LAW *)

(** A doubly stochastic evolution -- probability conserved forwards (column sums
    one) and information conserved (row sums one, the uniform ensemble
    stationary) -- never increases purity.  Disorder never decreases. *)
Theorem purity_never_increases :
  forall M p,
    nonneg M ->
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity (evolve M p) <= purity p.
Proof.
  intros M p Hnn Hcol Hrow.
  (* Row by row: each output entry is a convex combination of the input, so its
     square is at most the corresponding combination of squares. *)
  assert (row : forall i,
    evolve M p i * evolve M p i
      <= M i s0 * (p s0 * p s0) + M i s1 * (p s1 * p s1)
       + M i s2 * (p s2 * p s2) + M i s3 * (p s3 * p s3)).
  { intros i. unfold evolve, sum4.
    apply jensen4_le; try apply Hnn.
    specialize (Hrow i). unfold row_sum, sum4 in Hrow. exact Hrow. }
  assert (R0 := row s0). assert (R1 := row s1).
  assert (R2 := row s2). assert (R3 := row s3).
  (* Summing over rows and regrouping by column turns the bound into the column
     sums, each of which is one. *)
  assert (E : M s0 s0 * (p s0 * p s0) + M s0 s1 * (p s1 * p s1)
            + M s0 s2 * (p s2 * p s2) + M s0 s3 * (p s3 * p s3)
            + (M s1 s0 * (p s0 * p s0) + M s1 s1 * (p s1 * p s1)
             + M s1 s2 * (p s2 * p s2) + M s1 s3 * (p s3 * p s3))
            + (M s2 s0 * (p s0 * p s0) + M s2 s1 * (p s1 * p s1)
             + M s2 s2 * (p s2 * p s2) + M s2 s3 * (p s3 * p s3))
            + (M s3 s0 * (p s0 * p s0) + M s3 s1 * (p s1 * p s1)
             + M s3 s2 * (p s2 * p s2) + M s3 s3 * (p s3 * p s3))
            == col_sum M s0 * (p s0 * p s0) + col_sum M s1 * (p s1 * p s1)
             + col_sum M s2 * (p s2 * p s2) + col_sum M s3 * (p s3 * p s3))
    by (unfold col_sum, sum4; ring).
  rewrite (Hcol s0), (Hcol s1), (Hcol s2), (Hcol s3) in E.
  unfold purity, sum4.
  lra.
Qed.

(** ** The bound is attained strictly *)

(** A point mass on the first state: purity one, the most ordered distribution. *)
Definition point_mass : St -> Q := fun i => delta i s0.

Theorem mixing_strictly_increases_disorder :
  purity point_mass == 1 /\
  purity (evolve mixer point_mass) == 1 # 4 /\
  purity (evolve mixer point_mass) < purity point_mass.
Proof.
  split; [| split]; compute; reflexivity.
Qed.

(** The mixer really is an admissible evolution, so the strictness above is not
    obtained by cheating outside the hypotheses of the theorem. *)
Theorem mixer_is_admissible :
  nonneg mixer /\ (forall j, col_sum mixer j == 1) /\ conserves_information mixer.
Proof.
  split; [| split].
  - intros i j. compute. discriminate.
  - intros j. destruct j; compute; reflexivity.
  - apply mixer_conserves_but_is_not_deterministic.
Qed.

(** ** The two laws consume the same assumption *)

(** Reversible evolution is doubly stochastic, so it too can only increase
    disorder -- and being a relabelling it cannot strictly increase it either,
    though that equality is not proved here (see the boundary note). *)
Theorem reversible_never_increases_purity :
  forall M p, reversible M -> purity (evolve M p) <= purity p.
Proof.
  intros M p Hr.
  assert (Hinfo : conserves_information M)
    by (apply reversibility_forces_information_conservation; exact Hr).
  destruct Hr as [f [Hf Hinj]].
  apply purity_never_increases; [| | exact Hinfo].
  - intros i j. rewrite (Hf i j). unfold dmat. apply delta_nonneg.
  - intros j. unfold col_sum, sum4.
    rewrite (Hf s0 j), (Hf s1 j), (Hf s2 j), (Hf s3 j).
    assert (C := dmat_col_sum f j). unfold col_sum, sum4 in C. exact C.
Qed.

(** The reverse-physics point.  Both hypotheses of [purity_never_increases] are
    already in the vocabulary: column sums one is conservation of probability,
    and row sums one is [conserves_information].  So the second law is not an
    extra postulate on this carrier -- it is entailed by the same assumption that
    makes reversibility redundant. *)
Theorem the_second_law_is_entailed_by_information_conservation :
  forall M p,
    nonneg M ->
    (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity (evolve M p) <= purity p.
Proof. apply purity_never_increases. Qed.

(** ** The honest ledger *)

Print Assumptions jensen4_identity.
Print Assumptions jensen4_le.
Print Assumptions purity_never_increases.
Print Assumptions mixing_strictly_increases_disorder.
Print Assumptions mixer_is_admissible.
Print Assumptions reversible_never_increases_purity.
Print Assumptions the_second_law_is_entailed_by_information_conservation.
