(** * The coprime obstruction carries a positive conserved charge — so it is not
      an instability channel.

    This module AUDITS an interpretation, not a theorem.  [CoprimeHierarchyOrderLaw.v]
    proved where the coprime-ratio obstruction can appear.  The report attached to
    it then read that obstruction as the ghost's escape route:

      "an obstruction at a p:q resonance means there is a genuine on-shell
       q <-> p quanta conversion between the modes; that conversion is the
       channel through which the ghost sector talks to the healthy one — the
       perturbative mechanism of the instability."

    That reading is WRONG, and this file proves why in the general case.  (The
    Forge gate [tools/physics-moyal/ghost_channel_gate.forge] certifies the same
    statements as exact polynomial identities on nine specific loci and on the
    actually computed obstruction polynomials; here it is proved for all p, q.)

    ** The mechanism

    In mode variables [a1, a1b, a2, a2b] the Poisson bracket acts on a monomial
    [M = a1^{n1} a1b^{m1} a2^{n2} a2b^{m2}] by

      { p n1hat + q n2hat , M }  =  i [ (n1-m1) p + (n2-m2) q ] M

    where [n_jhat = a_j a_jb] is the occupation of mode j.  The bracket eigenvalue
    is EXACTLY the resonance frequency that [ker_split] uses to define the kernel.
    So the commutant of

      J = p n1hat + q n2hat

    is precisely the resonant sector.  The obstruction lives in that sector by
    construction — it is the kernel projection — hence it conserves J, and so does
    every other possible obstruction at the critical degree.  Nothing about the
    conversion kernel is special: resonance IS J-conservation.

    ** Why that settles the interpretation

    J is a POSITIVE combination of two NONNEGATIVE occupations, so conserving it
    bounds both of them: [n1 <= J/p] and [n2 <= J/q], for all time, at any coupling.
    The bound is kinematic — the derivation never refers to the sign of either
    frequency in the Hamiltonian, so it survives unchanged if mode 2 is made a
    ghost.  A channel that conserves a positive-definite charge cannot be the
    mechanism of a runaway.

    The structure that DOES run away is pair creation [a1^q a2^p], charge
    [(+q, +p)].  It is proved here to break J, and the charge it does conserve
    ([p n1hat - q n2hat]) is proved to have unbounded level sets.  That is the
    difference between a conversion channel and an instability, made exact.

    ** Boundary — what this does NOT establish

    - It does not touch the order law or the kernel-parity rule.  Only the
      physical gloss put on them changes.
    - The bracket action on monomials is stated here as the DEFINITION [freq]
      and separately certified as a polynomial identity in Forge; it is not
      re-derived from the mpoly implementation inside Rocq.
    - The boundedness statement is about the level set of J.  Conservation of J
      by the full (non-normalised) Hamiltonian is a separate question: the raw
      cubic vertex has non-resonant terms, which are exactly the ones J does not
      commute with.
    - Nothing here concerns Weyl gravity, the BV-BFV complex, or the residual
      classes. *)

Require Import ZArith.
Require Import Znumtheory.
Require Import QArith.
Require Import Lqa.
Require Import Lia.
Require Import CoprimeHierarchyOrderLaw.

(** ** The bracket eigenvalue *)

Open Scope Z_scope.

(** [{ J, M } = i * freq p q m * M].  This is the same expression as [resonant]
    in the order law, which is the entire point. *)
Definition freq (p q : Z) (m : Mono) : Z :=
  (e_a1 m - e_a1b m) * p + (e_a2 m - e_a2b m) * q.

Definition conserves_charge (p q : Z) (m : Mono) : Prop := freq p q m = 0.

(** The commutant of [J = p n1hat + q n2hat] is EXACTLY the resonant sector. *)
Theorem conserves_charge_iff_resonant :
  forall p q m, conserves_charge p q m <-> resonant p q m.
Proof. intros p q m. unfold conserves_charge, freq, resonant. reflexivity. Qed.

(** ** Every possible obstruction conserves the charge *)

Theorem kernel_conserves_charge :
  forall p q, conserves_charge p q (kernel p q).
Proof. intros p q. unfold conserves_charge, freq, kernel. simpl. ring. Qed.

Theorem kernel_conj_conserves_charge :
  forall p q, conserves_charge p q (kernel_conj p q).
Proof. intros p q. unfold conserves_charge, freq, kernel_conj. simpl. ring. Qed.

Theorem diagonal_conserves_charge :
  forall p q m, diagonal m -> conserves_charge p q m.
Proof.
  intros p q m [H1 H2]. unfold conserves_charge, freq.
  rewrite H1, H2. ring.
Qed.

(** The order law's classification says a nonnegative resonant monomial at the
    critical degree is diagonal, the kernel, or its conjugate.  All three
    conserve J.  So EVERY possible obstruction at the critical degree does —
    there is no J-breaking candidate for the obstruction to have been. *)
Theorem every_critical_obstruction_conserves_charge :
  forall p q m,
    0 < p -> 0 < q ->
    rel_prime p q ->
    nonneg_mono m ->
    total_degree m = p + q ->
    resonant p q m ->
    conserves_charge p q m.
Proof.
  intros p q m Hp Hq Hcop Hnn Hdeg Hres.
  destruct (resonant_at_critical_degree p q m Hp Hq Hcop Hnn Hdeg Hres)
    as [Hd | [Hk | Hkc]].
  - apply diagonal_conserves_charge. exact Hd.
  - rewrite Hk. apply kernel_conserves_charge.
  - rewrite Hkc. apply kernel_conj_conserves_charge.
Qed.

(** ** The contrast: pair creation *)

(** [a1^q a2^p] — both modes RAISED, charge [(+q, +p)]. *)
Definition pair_creation (p q : Z) : Mono := mkMono q 0 p 0.

Theorem pair_creation_breaks_charge :
  forall p q, 0 < p -> 0 < q -> ~ conserves_charge p q (pair_creation p q).
Proof.
  intros p q Hp Hq H. unfold conserves_charge, freq, pair_creation in H.
  simpl in H. nia.
Qed.

(** It conserves the OTHER combination instead — the indefinite one. *)
Definition freq_minus (p q : Z) (m : Mono) : Z :=
  (e_a1 m - e_a1b m) * p - (e_a2 m - e_a2b m) * q.

Theorem pair_creation_conserves_the_indefinite_charge :
  forall p q, freq_minus p q (pair_creation p q) = 0.
Proof. intros p q. unfold freq_minus, pair_creation. simpl. ring. Qed.

(** And the conversion kernel breaks THAT one — the two are exchanged. *)
Theorem kernel_breaks_the_indefinite_charge :
  forall p q, 0 < p -> 0 < q -> freq_minus p q (kernel p q) <> 0.
Proof. intros p q Hp Hq. unfold freq_minus, kernel. simpl. nia. Qed.

Close Scope Z_scope.

(** ** Why a positive charge bounds and an indefinite one does not

    Occupations are nonnegative rationals; [Q] keeps the development
    axiom-free, where [R] would not. *)

Open Scope Q_scope.

(** Conserving [J = p n1 + q n2] with [p, q > 0] bounds BOTH occupations. *)
Theorem positive_charge_bounds_both_occupations :
  forall p q n1 n2 J : Q,
    0 < p -> 0 < q -> 0 <= n1 -> 0 <= n2 ->
    p * n1 + q * n2 == J ->
    p * n1 <= J /\ q * n2 <= J.
Proof.
  intros p q n1 n2 J Hp Hq H1 H2 Heq.
  assert (0 <= p * n1) by (apply Qmult_le_0_compat; lra).
  assert (0 <= q * n2) by (apply Qmult_le_0_compat; lra).
  split; lra.
Qed.

(** In the form actually used: [n1 <= J/p]. *)
Corollary positive_charge_bounds_n1 :
  forall p q n1 n2 J : Q,
    0 < p -> 0 < q -> 0 <= n1 -> 0 <= n2 ->
    p * n1 + q * n2 == J ->
    n1 <= J / p.
Proof.
  intros p q n1 n2 J Hp Hq H1 H2 Heq.
  destruct (positive_charge_bounds_both_occupations p q n1 n2 J Hp Hq H1 H2 Heq)
    as [Hb _].
  apply Qle_shift_div_l; [ exact Hp | ].
  rewrite Qmult_comm. exact Hb.
Qed.

(** The indefinite charge bounds nothing: its level set through the origin is an
    unbounded ray of physical (nonnegative) states.  Given any bound [B] there is
    a state on that level set exceeding it. *)
Theorem indefinite_charge_level_set_is_unbounded :
  forall p q B : Q,
    0 < p -> 0 < q -> 0 <= B ->
    exists n1 n2 : Q,
      0 <= n1 /\ 0 <= n2 /\ p * n1 - q * n2 == 0 /\ B < n1.
Proof.
  intros p q B Hp Hq HB.
  exists (B + 1), (p * (B + 1) / q).
  assert (Hqn : ~ q == 0) by (intro Hc; rewrite Hc in Hq; apply (Qlt_irrefl 0); exact Hq).
  assert (Hnum : 0 <= p * (B + 1)) by (apply Qmult_le_0_compat; lra).
  repeat split.
  - lra.
  - apply Qle_shift_div_l; [ exact Hq | lra ].
  - assert (Hd : q * (p * (B + 1) / q) == p * (B + 1)) by (field; exact Hqn).
    rewrite Hd. ring.
  - lra.
Qed.

Close Scope Q_scope.

(** ** The honest ledger *)

Print Assumptions conserves_charge_iff_resonant.
Print Assumptions kernel_conserves_charge.
Print Assumptions kernel_conj_conserves_charge.
Print Assumptions diagonal_conserves_charge.
Print Assumptions every_critical_obstruction_conserves_charge.
Print Assumptions pair_creation_breaks_charge.
Print Assumptions pair_creation_conserves_the_indefinite_charge.
Print Assumptions kernel_breaks_the_indefinite_charge.
Print Assumptions positive_charge_bounds_both_occupations.
Print Assumptions positive_charge_bounds_n1.
Print Assumptions indefinite_charge_level_set_is_unbounded.
