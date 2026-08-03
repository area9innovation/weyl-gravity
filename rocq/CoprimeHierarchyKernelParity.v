(** * Which kernel appears, and why: an involution fixes it.

    [CoprimeHierarchyOrderLaw.v] proved WHERE the coprime-ratio obstruction can
    appear: order p+q-2, on the conversion kernel.  It does not say WHICH
    combination of the kernel and its conjugate appears.  The corpus data:

      locus   q   kernel          coefficient
      3:1     1   antisymmetric   real
      5:1     1   antisymmetric   real
      7:1     1   antisymmetric   real
      9:1     1   antisymmetric   real       (computed 2026-08-03)
      5:3     3   antisymmetric   real
      7:3     3   antisymmetric   real       (computed 2026-08-03)
      3:2     2   SYMMETRIC       imaginary
      5:2     2   SYMMETRIC       imaginary  (computed 2026-08-03)
      7:2     2   SYMMETRIC       imaginary  (computed 2026-08-03)

    The split tracks the parity of q, not of the order.  (Those two agree on
    every fixture with p odd, so the corpus could not distinguish them; 3:2 is
    the locus that rules out an order-parity reading, since it has ODD order and
    a symmetric kernel while 5:1 has EVEN order and an antisymmetric one.)

    ** The involution

    The vertex is v = -i (c y + i s p)^3, a cube of a single linear combination.
    In mode variables that combination is

      u = A (a2 + a2b) + B (a1 - a1b),     A, B real,

    symmetric in mode 2 and antisymmetric in mode 1.  Consider

      K :   a1 <-> a1b,    a2 -> -a2b,    a2b -> -a2.

    Then u -> -u, so the cubic vertex is ODD under K, while the free Hamiltonian
    h0 ~ w1 a1 a1b + w2 a2 a2b is EVEN.  A contribution built from n vertices
    therefore has K-eigenvalue (-1)^n.

    On the kernel monomials K acts by

      K(a1^q a2b^p)  = (-1)^p a1b^q a2^p,
      K(a1b^q a2^p)  = (-1)^p a1^q a2b^p,

    so the symmetric combination has eigenvalue (-1)^p and the antisymmetric one
    (-1)^(p+1).  Matching against (-1)^n with n = p+q-2 gives the rule.

    ** Boundary

    That u is odd under K, that h0 is even, and that an order-n contribution
    carries n vertices are MODELLING INPUTS, stated as hypotheses.  What is
    proved is that those inputs force the observed q-parity split -- and in
    particular that they forbid the other combination, which is what makes the
    rule content rather than a restatement. *)

Require Import Bool.
Require Import Arith.
Require Import Lia.

(** ** Parities

    [true] means K-eigenvalue +1. *)

(** A contribution at order [n] carries [n] vertices, each odd under K. *)
Definition contribution_parity (n : nat) : bool := Nat.even n.

(** The symmetric kernel has eigenvalue (-1)^p, the antisymmetric one
    (-1)^(p+1). *)
Definition symmetric_kernel_parity (p : nat) : bool := Nat.even p.
Definition antisymmetric_kernel_parity (p : nat) : bool := negb (Nat.even p).

(** A kernel can carry the obstruction only if its K-eigenvalue matches the
    contribution's. *)
Definition survives (kernel_parity contribution : bool) : Prop :=
  kernel_parity = contribution.

(** ** The critical order *)

(** At the critical order n = p+q-2 the contribution parity is that of p+q. *)
Lemma contribution_parity_at_critical_order :
  forall p q, (2 <= p + q)%nat ->
    contribution_parity (p + q - 2) = Nat.even (p + q).
Proof.
  intros p q H. unfold contribution_parity.
  (* Nat.even recurses two steps at a time, so this is definitional once the
     critical order is generalised away from the subtraction. *)
  remember (p + q - 2)%nat as m eqn:Hm.
  assert (Hpq : (p + q)%nat = S (S m)) by lia.
  rewrite Hpq. reflexivity.
Qed.

(** ** THE RULE *)

(** The symmetric kernel survives exactly when q is even. *)
Theorem symmetric_kernel_iff_q_even :
  forall p q, (2 <= p + q)%nat ->
    survives (symmetric_kernel_parity p) (contribution_parity (p + q - 2))
    <-> Nat.even q = true.
Proof.
  intros p q H. unfold survives, symmetric_kernel_parity.
  rewrite (contribution_parity_at_critical_order p q H).
  rewrite Nat.even_add.
  destruct (Nat.even p); destruct (Nat.even q); simpl; split; intro; congruence.
Qed.

(** The antisymmetric kernel survives exactly when q is odd. *)
Theorem antisymmetric_kernel_iff_q_odd :
  forall p q, (2 <= p + q)%nat ->
    survives (antisymmetric_kernel_parity p) (contribution_parity (p + q - 2))
    <-> Nat.even q = false.
Proof.
  intros p q H. unfold survives, antisymmetric_kernel_parity.
  rewrite (contribution_parity_at_critical_order p q H).
  rewrite Nat.even_add.
  destruct (Nat.even p); destruct (Nat.even q); simpl; split; intro; congruence.
Qed.

(** And the two are exclusive: exactly one combination can carry the
    obstruction.  This is what makes the rule a constraint rather than a
    description -- the other combination is FORBIDDEN, not merely unobserved. *)
Theorem exactly_one_kernel_survives :
  forall p q, (2 <= p + q)%nat ->
    (survives (symmetric_kernel_parity p) (contribution_parity (p + q - 2))
     /\ ~ survives (antisymmetric_kernel_parity p) (contribution_parity (p + q - 2)))
    \/
    (survives (antisymmetric_kernel_parity p) (contribution_parity (p + q - 2))
     /\ ~ survives (symmetric_kernel_parity p) (contribution_parity (p + q - 2))).
Proof.
  intros p q H. unfold survives, symmetric_kernel_parity, antisymmetric_kernel_parity.
  rewrite (contribution_parity_at_critical_order p q H).
  rewrite Nat.even_add.
  destruct (Nat.even p); destruct (Nat.even q); simpl;
    [ left | right | left | right ]; split; congruence.
Qed.

(** ** Agreement with every computed locus *)

(** The nine loci for which the obstruction has been computed, as a check that
    the rule is not vacuous: [true] in the second column means the symmetric
    kernel was observed. *)
Definition locus_check (p q : nat) (symmetric_observed : bool) : Prop :=
  symmetric_observed = Nat.even q.

Theorem all_nine_computed_loci_agree :
  locus_check 3 1 false /\ locus_check 5 1 false /\ locus_check 7 1 false
  /\ locus_check 9 1 false /\ locus_check 5 3 false /\ locus_check 7 3 false
  /\ locus_check 3 2 true  /\ locus_check 5 2 true  /\ locus_check 7 2 true.
Proof. repeat split; reflexivity. Qed.

(** ** The honest ledger *)

Print Assumptions contribution_parity_at_critical_order.
Print Assumptions symmetric_kernel_iff_q_even.
Print Assumptions antisymmetric_kernel_iff_q_odd.
Print Assumptions exactly_one_kernel_survives.
Print Assumptions all_nine_computed_loci_agree.
