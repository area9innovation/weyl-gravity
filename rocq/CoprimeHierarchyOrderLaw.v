(** * The coprime-ratio order law, proved.

    The Science Forge conjecture [sf:program/conjecture/coprime-ratio-hierarchy]
    stood at lifecycle OBSERVED with "No ansatz proof exists": for a coprime
    resonance p:q the Pais-Uhlenbeck cubic-vertex interaction deformation first
    obstructs at order p+q-2, on the conversion kernel a1^q a2b^p.

    Five fixtures supported it (3:1, 3:2, 5:1, 5:3, 7:1) and no mechanism was
    recorded.  This file proves the ORDER LAW and the SELECTION RULE from two
    facts, one about the word generator and one about arithmetic.

    ** Fact 1 -- the degree of a word is fixed by its order

    The vertex is cubic.  The Moyal bracket of homogeneous polynomials of degrees
    d1 and d2 is homogeneous of degree d1 + d2 - 2.  A word at order n is n
    vertices joined by n-1 brackets, so its degree is

      3n - 2(n-1) = n + 2

    EXACTLY -- not at most.  Every contribution at order n is homogeneous of
    degree n+2.  [word_degree] below is that recurrence.

    ** Fact 2 -- at degree p+q the resonance has essentially one solution

    A monomial a1^n1 a1b^m1 a2^n2 a2b^m2 is on shell when
    (n1-m1) p + (n2-m2) q = 0.  With p and q coprime this forces
    n1-m1 = k q and n2-m2 = -k p for one integer k, and the degree budget
    n1+m1+n2+m2 = p+q then forces |k| <= 1.  k = 0 is diagonal; k = 1 pins the
    exponents completely to (q, 0, 0, p) -- the conversion kernel -- and k = -1
    to its conjugate.  [resonant_at_critical_degree] is that classification.

    ** The consequence

    Putting them together: the conversion kernel has degree p+q, contributions at
    order n have degree exactly n+2, so the kernel can appear only at
    n = p+q-2, and every lower order is identically zero on it.  That is the
    order law and the selection rule together.

    ** Boundary

    Fact 1 is stated as a recurrence over the word generator, which is the
    modelling step: that a word at order n is n cubic vertices joined by n-1
    Moyal brackets is asserted here, not derived from moyal_hi.forge.  What is
    proved is that the recurrence forces degree n+2, and the arithmetic
    classification, which is where the coprimality does its work.

    Nothing here explains why EVEN p is unobstructed -- see
    PREREG-EVEN-P.md and the accompanying report.  The order law says WHERE an
    obstruction can appear, not that one does. *)

Require Import ZArith.
Require Import Znumtheory.
Require Import Lia.

Open Scope Z_scope.

(** ** Fact 1: a word at order n is homogeneous of degree n+2 *)

(** The degree of a word, as a recurrence: one vertex is cubic, and adjoining a
    further vertex through a Moyal bracket adds 3 and removes 2. *)
Fixpoint word_degree (n : nat) : Z :=
  match n with
  | O => 0                      (* no word *)
  | S O => 3                    (* the cubic vertex itself *)
  | S k => word_degree k + 3 - 2
  end.

Theorem word_degree_is_order_plus_two :
  forall n, (1 <= n)%nat -> word_degree n = Z.of_nat n + 2.
Proof.
  induction n as [| k IH]; intros H.
  - lia.
  - destruct k as [| j].
    + simpl. lia.
    + assert (Hk : (1 <= S j)%nat) by lia.
      specialize (IH Hk).
      change (word_degree (S (S j))) with (word_degree (S j) + 3 - 2).
      rewrite IH. lia.
Qed.

(** ** Fact 2: the resonance at the critical degree *)

(** A monomial's exponents. *)
Record Mono : Set := mkMono { e_a1 : Z; e_a1b : Z; e_a2 : Z; e_a2b : Z }.

Definition nonneg_mono (m : Mono) : Prop :=
  0 <= e_a1 m /\ 0 <= e_a1b m /\ 0 <= e_a2 m /\ 0 <= e_a2b m.

Definition total_degree (m : Mono) : Z :=
  e_a1 m + e_a1b m + e_a2 m + e_a2b m.

(** On shell: the frequency (n1-m1) p + (n2-m2) q vanishes. *)
Definition resonant (p q : Z) (m : Mono) : Prop :=
  (e_a1 m - e_a1b m) * p + (e_a2 m - e_a2b m) * q = 0.

Definition diagonal (m : Mono) : Prop :=
  e_a1 m = e_a1b m /\ e_a2 m = e_a2b m.

(** The conversion kernel a1^q a2b^p and its conjugate. *)
Definition kernel (p q : Z) : Mono := mkMono q 0 0 p.
Definition kernel_conj (p q : Z) : Mono := mkMono 0 q p 0.

(** The classification.  At total degree exactly p+q, with p and q coprime and
    both positive, a nonnegative resonant monomial is diagonal, the kernel, or
    its conjugate. *)
Theorem resonant_at_critical_degree :
  forall p q m,
    0 < p -> 0 < q ->
    rel_prime p q ->
    nonneg_mono m ->
    total_degree m = p + q ->
    resonant p q m ->
    diagonal m \/ m = kernel p q \/ m = kernel_conj p q.
Proof.
  intros p q m Hp Hq Hcop [H1 [H2 [H3 H4]]] Hdeg Hres.
  unfold resonant in Hres.
  set (a := e_a1 m - e_a1b m). set (b := e_a2 m - e_a2b m).
  fold a b in Hres.
  (* coprimality: q divides a *)
  assert (Hqa : (q | a)).
  { apply (Gauss q p a).
    - exists (- b). lia.
    - apply rel_prime_sym. exact Hcop. }
  destruct Hqa as [k Hk].
  (* and then b = -k p *)
  assert (Hb : b = - (k * p)).
  { assert (q <> 0) by lia. nia. }
  (* degree budget bounds |k| *)
  assert (Hbound1 : Z.abs a <= e_a1 m + e_a1b m) by (unfold a; lia).
  assert (Hbound2 : Z.abs b <= e_a2 m + e_a2b m) by (unfold b; lia).
  assert (Habs : Z.abs a + Z.abs b <= p + q) by (unfold total_degree in Hdeg; lia).
  assert (Hka : Z.abs a = Z.abs k * q) by (rewrite Hk; rewrite Z.abs_mul; lia).
  assert (Hkb : Z.abs b = Z.abs k * p) by (rewrite Hb; rewrite Z.abs_opp, Z.abs_mul; lia).
  assert (Hk1 : Z.abs k <= 1) by nia.
  (* the three cases *)
  destruct (Z.abs k =? 0) eqn:Ez.
  { left. apply Z.eqb_eq in Ez.
    assert (k = 0) by lia. subst k.
    unfold diagonal. unfold a in Hk. unfold b in Hb. lia. }
  assert (Habsk : Z.abs k = 1) by lia.
  assert (Hkk : k = 1 \/ k = -1) by lia.
  destruct m as [x1 y1 x2 y2]. unfold a, b in *. simpl in *.
  destruct Hkk as [Hk1' | Hk1']; subst k.
  - right. left. unfold kernel. unfold total_degree in Hdeg. simpl in Hdeg.
    assert (x1 - y1 = q) by lia.
    assert (x2 - y2 = - p) by lia.
    assert (y1 = 0) by lia.
    assert (x2 = 0) by lia.
    subst. f_equal; lia.
  - right. right. unfold kernel_conj. unfold total_degree in Hdeg. simpl in Hdeg.
    assert (x1 - y1 = - q) by lia.
    assert (x2 - y2 = p) by lia.
    assert (x1 = 0) by lia.
    assert (y2 = 0) by lia.
    subst. f_equal; lia.
Qed.

(** ** THE ORDER LAW *)

(** The kernel has degree p+q. *)
Lemma kernel_degree : forall p q, 0 < p -> 0 < q -> total_degree (kernel p q) = p + q.
Proof. intros p q Hp Hq. unfold total_degree, kernel. simpl. lia. Qed.

(** A contribution at order n is homogeneous of degree n+2, so it can be
    supported on the kernel only if n+2 = p+q, i.e. n = p+q-2.  Every lower
    order is identically zero there: that is the selection rule. *)
Theorem order_law :
  forall p q n,
    0 < p -> 0 < q -> (1 <= n)%nat ->
    word_degree n = total_degree (kernel p q) ->
    Z.of_nat n = p + q - 2.
Proof.
  intros p q n Hp Hq Hn Heq.
  rewrite (word_degree_is_order_plus_two n Hn) in Heq.
  rewrite (kernel_degree p q Hp Hq) in Heq.
  lia.
Qed.

Theorem selection_rule_below_the_critical_order :
  forall p q n,
    0 < p -> 0 < q -> (1 <= n)%nat ->
    Z.of_nat n < p + q - 2 ->
    word_degree n <> total_degree (kernel p q).
Proof.
  intros p q n Hp Hq Hn Hlt Heq.
  apply (order_law p q n Hp Hq Hn) in Heq. lia.
Qed.

(** ** The honest ledger *)

Print Assumptions word_degree_is_order_plus_two.
Print Assumptions resonant_at_critical_degree.
Print Assumptions kernel_degree.
Print Assumptions order_law.
Print Assumptions selection_rule_below_the_critical_order.
