(** * The degenerate case: a dipole ghost admits no positive inner product.

    [WeylGhostForced.v] proved that two or more DISTINCT simple poles always
    include one with a negative residue, and flagged the honest gap:

      Weyl gravity's actual kinetic operator is Box^2 -- a DOUBLE pole at
      k^2 = 0, not two distinct simple poles.  That the dipole case is no
      better was cited (Riegert 1984), not proved, and it is the case that
      actually occurs.

    This module closes that gap.  It is the declared successor gate
    [WEYL_GHOST_DEGENERATE_LIMIT].

    ** Where the statement comes from

    Not from this stream.  The black-hole programme had already computed the
    physical instance, on the Schwarzschild exterior, in the odd-parity spin-two
    sector: [black_hole_programme/phase4/axial_local_nonlocal_positivity_v1]
    certifies that the dynamically compatible commutant of the spin-two flux
    structure is

      eta = a I + b N,     N^2 = 0

    -- a rank-two Jordan block -- and that the resulting flux metric

      G eta = [[0, g a], [g a, g b]],      det = - g^2 a^2

    is indefinite when a is nonzero and degenerate when it is not.  Never
    positive.  Its conclusion, in that package's words: "no rational local
    dynamically compatible metric operator makes the spin-two form positive
    definite."

    What this module does is abstract that computation away from the black-hole
    background and prove it as linear algebra over Q, so that it can discharge
    the [O3] citation in [WeylGhostForced.v].  The mathematics is theirs; the
    only thing added here is that it is now a machine-checked theorem in the
    reverse-physics chain rather than a reference.

    ** Why the two lines agree, and why that is the interesting part

    [WeylGhostForced.v] argues at the level of ACTIONS, kinematically, in every
    even dimension, with dependency tag LOCAL-ALGEBRAIC.  It concludes that the
    ghost is forced and that only RP-LOCAL and RP-METRIC can remove it.

    The black-hole package argues at the level of on-shell SCATTERING DATA on a
    fixed background, with tags LOCAL-ALGEBRAIC and REDUCED-MODE.  It concludes
    that no LOCAL positive metric exists -- and that a compatible fundamental
    symmetry does exist on the combined future space, i.e. a NONLOCAL one.

    Two independent computations, different objects, different tags, same
    verdict: LOCALITY is the load-bearing assumption.  The assumption lattice
    predicted which of the five had to give; the scattering analysis found
    exactly that one giving, in the sector that matters.

    The tags are NOT merged.  Neither result is promoted by the other, and
    nothing here is a LORENTZIAN-CAUSAL claim.  What is recorded is a
    convergence, which is evidence about where to look and not a theorem about
    the Lorentzian theory.

    ** Boundary

    This is 2x2 linear algebra over Q.  It does not derive the Jordan structure
    from Weyl gravity -- that a dipole ghost IS a rank-two Jordan block is the
    standing input, and the black-hole package is where it was computed for a
    real background.  Nothing here touches the BV-BFV complex, the residual
    classes, the physical spectrum, or the quantum theory. *)

Require Import QArith.
Require Import Lqa.

Open Scope Q_scope.

(** ** The commutant of a rank-two nilpotent

    [N = [[0,1],[0,0]]].  A redefinition of the inner product must commute with
    the dynamics, so the available freedom is exactly the commutant of [N] --
    and that is only two parameters, not four.  This is the whole reason the
    obstruction cannot be evaded. *)

Theorem commutant_of_the_jordan_block :
  forall p q r s : Q,
    (* eta N = N eta, written out on the four entries *)
    (0 == r) /\ (p == s) /\ (0 == 0) /\ (r == 0) ->
    r == 0 /\ p == s.
Proof. intros p q r s [H1 [H2 _]]. split; lra. Qed.

(** So [eta = a I + b N], i.e. [[a,b],[0,a]].  Paired against the off-diagonal
    null-basis Gram [G = [[0,g],[g,0]]] this gives the flux metric

      G eta  =  [[0, g a], [g a, g b]]

    which is symmetric, as it must be for a metric. *)

Definition flux_11 (g a b : Q) : Q := 0.
Definition flux_12 (g a b : Q) : Q := g * a.
Definition flux_22 (g a b : Q) : Q := g * b.

Definition flux_det (g a b : Q) : Q :=
  flux_11 g a b * flux_22 g a b - flux_12 g a b * flux_12 g a b.

(** A disequality is not a sign fact; [nra] needs the square made positive
    explicitly. *)
Lemma square_is_positive : forall x : Q, ~ x == 0 -> 0 < x * x.
Proof.
  intros x H.
  destruct (Qlt_le_dec 0 x) as [P | P]. nra.
  destruct (Qlt_le_dec x 0) as [N | N]. nra.
  exfalso. apply H. lra.
Qed.

Theorem flux_determinant :
  forall g a b, flux_det g a b == - (g * g * a * a).
Proof. intros g a b. unfold flux_det, flux_11, flux_12, flux_22. ring. Qed.

(** The determinant is never positive.  A 2x2 symmetric form with nonpositive
    determinant is never positive definite -- so no choice of [a] and [b] works.

    Note this is not "no choice we found": [a] and [b] EXHAUST the commutant, so
    it is no choice that exists. *)
Theorem flux_determinant_is_never_positive :
  forall g a b, ~ (0 < flux_det g a b).
Proof.
  intros g a b H. rewrite (flux_determinant g a b) in H. nra.
Qed.

(** ** The quadratic form, and explicit witnesses

    [Q(x,y) = 2 g a x y + g b y^2]. *)

Definition flux_form (g a b x y : Q) : Q := 2 * (g * a) * x * y + (g * b) * y * y.

(** The first basis vector is NULL for every admissible [eta].  That alone kills
    definiteness of either sign, without any case analysis. *)
Theorem first_basis_vector_is_null :
  forall g a b, flux_form g a b 1 0 == 0.
Proof. intros g a b. unfold flux_form. ring. Qed.

Theorem never_definite :
  forall g a b,
    ~ (forall x y : Q, ~ (x == 0 /\ y == 0) -> 0 < flux_form g a b x y).
Proof.
  intros g a b H.
  assert (Hne : ~ ((1 : Q) == 0 /\ (0 : Q) == 0)) by (intros [H1 _]; lra).
  pose proof (H 1 0 Hne) as Hpos.
  rewrite (first_basis_vector_is_null g a b) in Hpos. lra.
Qed.

(** ** The dichotomy

    [a <> 0]: the form is INDEFINITE, with explicit vectors of either sign. *)

Theorem indefinite_when_a_is_nonzero :
  forall g a b, ~ g == 0 -> ~ a == 0 ->
    flux_form g a b ((1 - g * b) / (2 * (g * a))) 1 == 1
    /\ flux_form g a b ((- (1) - g * b) / (2 * (g * a))) 1 == - (1).
Proof.
  intros g a b Hg Ha.
  unfold flux_form. split; field; split; assumption.
Qed.

(** [a == 0]: the form is DEGENERATE -- the first basis vector is in the radical,
    so the metric is not even nondegenerate, let alone positive. *)

Definition flux_bilinear (g a b x y x' y' : Q) : Q :=
  (g * a) * (x * y' + x' * y) + (g * b) * (y * y').

Theorem degenerate_when_a_is_zero :
  forall g b x' y', flux_bilinear g 0 b 1 0 x' y' == 0.
Proof. intros g b x' y'. unfold flux_bilinear. ring. Qed.

(** Non-vacuity: the bilinear form is NOT identically zero, so "degenerate" is a
    statement about a direction and not about a form that vanishes anyway. *)
Theorem the_bilinear_form_is_not_trivial :
  forall g, ~ g == 0 -> ~ (flux_bilinear g 1 0 1 0 0 1 == 0).
Proof. intros g Hg. unfold flux_bilinear. nra. Qed.

(** ** THE DIPOLE GHOST THEOREM

    Whatever the parameters, the flux metric available to a dipole is indefinite
    or degenerate.  There is no positive-definite invariant inner product, and
    therefore no rescue by redefining the norm.

    This is the statement [WeylGhostForced.v] had to cite. *)

Theorem a_dipole_admits_no_positive_inner_product :
  forall g a b,
    (~ (0 < flux_det g a b))
    /\ flux_form g a b 1 0 == 0.
Proof.
  intros g a b. split.
  - apply flux_determinant_is_never_positive.
  - apply first_basis_vector_is_null.
Qed.

(** And the sharp form of the dichotomy, in one statement. *)
Theorem indefinite_or_degenerate :
  forall g a b, ~ g == 0 ->
    (~ a == 0 -> flux_det g a b < 0) /\ (a == 0 -> flux_det g a b == 0).
Proof.
  intros g a b Hg. split; intro Ha; rewrite (flux_determinant g a b).
  - assert (Hg2 : 0 < g * g) by (apply square_is_positive; exact Hg).
    assert (Ha2 : 0 < a * a) by (apply square_is_positive; exact Ha).
    nra.
  - rewrite Ha. ring.
Qed.

(** ** The honest ledger *)

Print Assumptions commutant_of_the_jordan_block.
Print Assumptions square_is_positive.
Print Assumptions flux_determinant.
Print Assumptions flux_determinant_is_never_positive.
Print Assumptions first_basis_vector_is_null.
Print Assumptions never_definite.
Print Assumptions indefinite_when_a_is_nonzero.
Print Assumptions degenerate_when_a_is_zero.
Print Assumptions the_bilinear_form_is_not_trivial.
Print Assumptions a_dipole_admits_no_positive_inner_product.
Print Assumptions indefinite_or_degenerate.
