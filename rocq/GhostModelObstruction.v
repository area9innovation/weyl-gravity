(** * The ghost model: the same obstruction, and no charge to bound it.

    [CoprimeHierarchyChargeBound.v] audited a physics gloss and refuted it: the
    coprime obstruction conserves [J = p n1hat + q n2hat], a POSITIVE combination
    of nonnegative occupations, so it bounds them rather than destabilising
    anything.  It also recorded the limit of that argument — the model it was
    proved in has no ghost.  Its free Hamiltonian is [w1 n1hat + w2 n2hat] with
    both frequencies positive, and its closing section declared the successor:

      GHOST_MODEL_OBSTRUCTION — redo the deformation with a genuinely indefinite
      free Hamiltonian h0 = w1 n1hat - w2 n2hat and ask whether the obstruction
      structure changes.  Under a2 <-> a2b the conversion kernel becomes pair
      creation, so the two models plausibly see MIRROR-IMAGE OBSTRUCTION LOCI.
      If that is right, the coprime hierarchy is a statement about which channel
      is resonant — not about stability at all, in either model.

    This module settles it.  The conclusion is confirmed; the phrasing was not
    quite right, in a way worth stating.

    ** What is proved

    Resonance in the ghost model is [(n1-m1) p - (n2-m2) q = 0].  The relabelling
    [conj2] that exchanges [a2] with [a2b] is an involution preserving total
    degree, nonnegativity and diagonality, and it carries the ghost-resonant
    sector BIJECTIVELY onto the healthy resonant sector.  It sends the conversion
    kernel [a1^q a2b^p] to pair creation [a1^q a2^p].

    THE LOCI DO NOT MIRROR — THEY COINCIDE.  [conj2] acts on monomials, not on
    [(p, q)], so the set of ratios admitting an obstruction is literally the same
    in both models, and the whole coprime hierarchy transports unchanged.  What
    mirrors is the CHANNEL: at each such ratio the obstructing monomial is
    conversion in the healthy model and pair creation in the ghost model.

    THE CHARGE IS WHERE THE MODELS PART.  A quadratic charge [al n1hat + be n2hat]
    conserved on the ghost model's critical sector must satisfy [al q + be p = 0],
    which for positive [p, q] forces [al] and [be] to have STRICTLY OPPOSITE
    SIGNS: the only surviving charge is proportional to [p n1hat - q n2hat], and
    its level sets are unbounded.  In the healthy model the same argument gives
    [(p, q)], both positive, which bounds.

    ** What that means, and it is the point of the exercise

    The bound proved in the predecessor is a consequence of the DEFINITENESS of
    the free Hamiltonian, not of the obstruction.  The obstruction is identical in
    the two models — same ratios, same degree, same classification, exchanged by a
    relabelling — and it bounds in one and not the other.  So the coprime
    hierarchy is indeed a statement about which channel is resonant, exactly as
    the successor question guessed, and stability is carried entirely by the sign
    of h0.

    That separation is the useful part: the obstruction is MATHEMATICS about a
    degree and a coprimality condition, and the boundedness is PHYSICS about a
    positive-definite free Hamiltonian.  Conflating them is what produced the
    original wrong gloss.

    ** Boundary — what this does NOT establish

    - It does not show the ghost model is unstable.  It shows the specific
      charge argument that bounds the healthy model has no counterpart here.  An
      unbounded level set permits growth; it does not produce it.
    - It says nothing about whether the ghost model's cubic vertex actually
      contains the pair-creation monomial with nonzero coefficient.  That is a
      computation in the deformation, not a statement about the resonant sector.
    - The quadratic charges considered are the diagonal ones [al n1hat +
      be n2hat].  A conserved quantity of higher degree is not excluded, and
      would have to be ruled out separately to call the ghost model unbounded.
    - The bracket action on monomials is the DEFINITION [ghost_freq] here, as it
      is in the predecessor; it is certified as a polynomial identity in Forge,
      not re-derived from the implementation inside Rocq.
    - Nothing here concerns Weyl gravity, the BV-BFV complex, or the residual
      classes.  The Weyl ghost is a genuinely indefinite system, which is why the
      successor question was asked, but this is a two-mode toy. *)

Require Import ZArith.
Require Import Znumtheory.
Require Import QArith.
Require Import Lqa.
Require Import Lia.
Require Import CoprimeHierarchyOrderLaw.
Require Import CoprimeHierarchyChargeBound.

Open Scope Z_scope.

(** ** The ghost model's resonance condition

    [h0 = w1 n1hat - w2 n2hat] at ratio [w1 : w2 = p : q].  The bracket eigenvalue
    is [freq_minus], which the predecessor already introduced to name the charge
    that pair creation conserves — the same expression, now as the model's own
    resonance condition rather than as a contrast. *)
Definition ghost_resonant (p q : Z) (m : Mono) : Prop := freq_minus p q m = 0.

(** ** The relabelling that turns a positive-frequency mode into a ghost *)

Definition conj2 (m : Mono) : Mono :=
  mkMono (e_a1 m) (e_a1b m) (e_a2b m) (e_a2 m).

Theorem conj2_involutive : forall m, conj2 (conj2 m) = m.
Proof. intros [a b c d]. reflexivity. Qed.

Theorem conj2_preserves_total_degree :
  forall m, total_degree (conj2 m) = total_degree m.
Proof. intros [a b c d]. unfold total_degree, conj2. simpl. ring. Qed.

Theorem conj2_preserves_nonneg :
  forall m, nonneg_mono m -> nonneg_mono (conj2 m).
Proof.
  intros [a b c d] [H1 [H2 [H3 H4]]]. unfold nonneg_mono, conj2. simpl.
  repeat split; assumption.
Qed.

Theorem conj2_preserves_diagonal :
  forall m, diagonal m -> diagonal (conj2 m).
Proof.
  intros [a b c d] [H1 H2]. unfold diagonal, conj2. simpl. split; [ exact H1 | ].
  symmetry. exact H2.
Qed.

(** ** The mirror: the two resonant sectors are exchanged *)

Theorem ghost_resonant_iff_resonant_of_conj2 :
  forall p q m, ghost_resonant p q m <-> resonant p q (conj2 m).
Proof.
  intros p q [a b c d]. unfold ghost_resonant, freq_minus, resonant, conj2. simpl.
  split; intro H; lia.
Qed.

(** The conversion kernel of the healthy model IS pair creation in the ghost
    model — the single fact the successor question was built on. *)
Theorem conj2_kernel_is_pair_creation :
  forall p q, conj2 (kernel p q) = pair_creation p q.
Proof. intros p q. reflexivity. Qed.

Theorem pair_creation_is_ghost_resonant :
  forall p q, ghost_resonant p q (pair_creation p q).
Proof. intros p q. unfold ghost_resonant. apply pair_creation_conserves_the_indefinite_charge. Qed.

(** ...and the healthy model's obstruction is NOT resonant in the ghost model,
    which is the same statement read the other way. *)
Theorem kernel_is_not_ghost_resonant :
  forall p q, 0 < p -> 0 < q -> ~ ghost_resonant p q (kernel p q).
Proof.
  intros p q Hp Hq H. unfold ghost_resonant in H.
  exact (kernel_breaks_the_indefinite_charge p q Hp Hq H).
Qed.

(** ** The classification transports — same ratios, mirrored channel *)

(** Pair annihilation [a1b^q a2b^p], the image of the healthy model's
    [kernel_conj] under the relabelling. *)
Definition pair_annihilation (p q : Z) : Mono := mkMono 0 q 0 p.

Theorem conj2_kernel_conj_is_pair_annihilation :
  forall p q, conj2 (kernel_conj p q) = pair_annihilation p q.
Proof. intros p q. reflexivity. Qed.

(** The ghost model's critical sector, classified.  Note what did NOT change:
    the hypotheses are identical — same positivity, same coprimality, same
    critical degree [p + q].  Only the two named monomials differ, and they are
    the images of the healthy ones under [conj2]. *)
Theorem ghost_resonant_at_critical_degree :
  forall p q m,
    0 < p -> 0 < q ->
    rel_prime p q ->
    nonneg_mono m ->
    total_degree m = p + q ->
    ghost_resonant p q m ->
    diagonal m \/ m = pair_creation p q \/ m = pair_annihilation p q.
Proof.
  intros p q m Hp Hq Hcop Hnn Hdeg Hres.
  assert (Hd : total_degree (conj2 m) = p + q)
    by (rewrite conj2_preserves_total_degree; exact Hdeg).
  destruct (resonant_at_critical_degree p q (conj2 m) Hp Hq Hcop
              (conj2_preserves_nonneg m Hnn) Hd
              (proj1 (ghost_resonant_iff_resonant_of_conj2 p q m) Hres))
    as [Hdiag | [Hk | Hkc]].
  - left. rewrite <- (conj2_involutive m). apply conj2_preserves_diagonal. exact Hdiag.
  - right. left.
    rewrite <- (conj2_involutive m), Hk. apply conj2_kernel_is_pair_creation.
  - right. right.
    rewrite <- (conj2_involutive m), Hkc. apply conj2_kernel_conj_is_pair_annihilation.
Qed.

(** THE LOCI COINCIDE.  An obstruction exists at a ratio in one model exactly when
    it does in the other, because [conj2] is a degree- and nonnegativity-preserving
    bijection between the two critical sectors and does not touch [(p, q)].  The
    successor question's "mirror-image obstruction loci" is therefore not quite
    right: the loci are the SAME, and it is the channel that mirrors. *)
Theorem obstruction_ratios_are_unchanged :
  forall p q m,
    0 < p -> 0 < q -> rel_prime p q ->
    nonneg_mono m -> total_degree m = p + q ->
    (ghost_resonant p q m <-> resonant p q (conj2 m)).
Proof.
  intros p q m _ _ _ _ _. apply ghost_resonant_iff_resonant_of_conj2.
Qed.

(** ** Where the models part: the surviving charge

    A diagonal quadratic charge [al n1hat + be n2hat] acts on a monomial with
    eigenvalue [al (n1-m1) + be (n2-m2)].  Conserving it on the ghost model's
    critical sector requires, in particular, conserving it on pair creation. *)
Definition charge_eigenvalue (al be : Z) (m : Mono) : Z :=
  (e_a1 m - e_a1b m) * al + (e_a2 m - e_a2b m) * be.

Theorem conserved_on_pair_creation_forces_the_relation :
  forall al be p q,
    charge_eigenvalue al be (pair_creation p q) = 0 -> q * al + p * be = 0.
Proof.
  intros al be p q H. unfold charge_eigenvalue, pair_creation in H. simpl in H. lia.
Qed.

(** ...and that relation forces the two coefficients to have STRICTLY OPPOSITE
    signs, unless the charge is trivial.  This is the whole difference between the
    two models, in one line. *)
Theorem surviving_ghost_charge_is_indefinite :
  forall al be p q,
    0 < p -> 0 < q ->
    q * al + p * be = 0 ->
    (al = 0 /\ be = 0) \/ al * be < 0.
Proof.
  intros al be p q Hp Hq H.
  destruct (Z.lt_trichotomy al 0) as [Hlt | [Hz | Hgt]].
  - right. nia.
  - left. subst al. split; [ reflexivity | nia ].
  - right. nia.
Qed.

(** The healthy model's charge fails the same test, which is the contrast made
    exact: [(p, q)] is not conserved on pair creation. *)
Theorem healthy_charge_is_not_conserved_on_pair_creation :
  forall p q, 0 < p -> 0 < q -> charge_eigenvalue p q (pair_creation p q) <> 0.
Proof.
  intros p q Hp Hq H. unfold charge_eigenvalue, pair_creation in H. simpl in H. nia.
Qed.

(** ...while the indefinite one IS, and it is the one [conj2] carries the healthy
    model's charge to. *)
Theorem indefinite_charge_is_conserved_on_pair_creation :
  forall p q, charge_eigenvalue p (- q) (pair_creation p q) = 0.
Proof. intros p q. unfold charge_eigenvalue, pair_creation. simpl. ring. Qed.

Close Scope Z_scope.

(** ** And an indefinite charge bounds nothing

    The predecessor proved this for the level set of [p n1 - q n2]; it is exactly
    the charge that survives here, so the conclusion transports directly.  Stated
    again in the ghost model's own terms so the chain is readable without it. *)

Open Scope Q_scope.

Theorem ghost_model_charge_does_not_bound_occupations :
  forall p q B : Q,
    0 < p -> 0 < q -> 0 <= B ->
    exists n1 n2 : Q,
      0 <= n1 /\ 0 <= n2 /\ p * n1 - q * n2 == 0 /\ B < n1.
Proof. exact indefinite_charge_level_set_is_unbounded. Qed.

(** The contrast, restated: in the HEALTHY model the same conservation law bounds
    both occupations.  Same p, same q, same nonnegativity — only the sign in the
    charge differs, and that is the sign of the free Hamiltonian. *)
Theorem healthy_model_charge_does_bound_occupations :
  forall p q n1 n2 J : Q,
    0 < p -> 0 < q -> 0 <= n1 -> 0 <= n2 ->
    p * n1 + q * n2 == J ->
    p * n1 <= J /\ q * n2 <= J.
Proof. exact positive_charge_bounds_both_occupations. Qed.

Close Scope Q_scope.

(** ** The honest ledger *)

Print Assumptions conj2_involutive.
Print Assumptions conj2_preserves_total_degree.
Print Assumptions conj2_preserves_nonneg.
Print Assumptions conj2_preserves_diagonal.
Print Assumptions ghost_resonant_iff_resonant_of_conj2.
Print Assumptions conj2_kernel_is_pair_creation.
Print Assumptions pair_creation_is_ghost_resonant.
Print Assumptions kernel_is_not_ghost_resonant.
Print Assumptions conj2_kernel_conj_is_pair_annihilation.
Print Assumptions ghost_resonant_at_critical_degree.
Print Assumptions obstruction_ratios_are_unchanged.
Print Assumptions conserved_on_pair_creation_forces_the_relation.
Print Assumptions surviving_ghost_charge_is_indefinite.
Print Assumptions healthy_charge_is_not_conserved_on_pair_creation.
Print Assumptions indefinite_charge_is_conserved_on_pair_creation.
Print Assumptions ghost_model_charge_does_not_bound_occupations.
Print Assumptions healthy_model_charge_does_bound_occupations.
