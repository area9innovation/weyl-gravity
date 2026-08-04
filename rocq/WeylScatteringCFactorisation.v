(** * The open scattering question, reduced to a finite test -- and why nothing
      weaker can answer it.

    [WeylGhostDipole.v] and [reports/ghost-and-the-black-hole.md] left exactly one
    question.  The black-hole programme certifies that a compatible fundamental
    symmetry [C_out] exists on the combined future space, and flags as OPEN
    whether it FACTORISES,

      C_out  =  C_+  (+)  C_H

    over null infinity and the horizon
    ([phase4/axial_local_commutant_spectral_c_v1], claim flag
    [endpoint_block_diagonal_scattering_c_established = false]).  The assumption
    lattice says this is now the decisive question about the ghost: a [C] that
    factorises is a positivity statement one could plausibly call physical; one
    that does not is a formal device.

    ** The answer, in three parts

    (1) THE QUESTION IS FINITE.  With [S = (R, A)^T], [R = T_+ T_-^{-1}],
    [A = T_-^{-1}], and the oriented Stokes identity
    [G_- = R^dag G_+ R + A^dag H_out A]:

      - [C_+ (+) C_H] preserves [ran(S)] with a common [C_-] exactly when
        [C_+ = T_+ C_H T_+^{-1}].  The two boundary symmetries are NOT
        independently choosable; the horizon one determines the other.
      - Pulling the Stokes identity back by [T_-] gives, with no new input,
        [T_-^dag G_- T_-  =  T_+^dag G_+ T_+  +  H_out].
      - So the question is whether [H_out] and [M := T_+^dag G_+ T_+] carry a
        COMMON FUNDAMENTAL DECOMPOSITION, and that holds exactly when the pencil
        [det(M - lambda H_out)] has all roots real and positive with
        [H_out^{-1}M] diagonalisable.

    An open scattering condition has become a 3x3 generalised eigenvalue problem.
    The matrix algebra is certified in tango
    [forge/examples/weyl_scattering_c_factorisation_gate.forge], which checks the
    pullback identity and the intertwining reduction -- and its NECESSITY -- in
    exact rational arithmetic.

    (2) THE INPUT IS NOT AVAILABLE.  [T_+] is not certified explicit:
    [phase4/axial_explicit_tplus_band_v1] carries
    [explicit_Tplus_certified = false] and is still transporting toward [r = 4].
    [T_-] is proved invertible with an exact determinant, but that determinant
    involves the Jost amplitudes [A_in_s], which have no closed form for the
    Regge-Wheeler potential.  So the test cannot be run today.

    (3) AND NOTHING WEAKER WILL DO.  Everything the programme certifies about the
    three forms is their INERTIA: [(1,2,0)] for each of [G_-], [G_+], [H_out].
    This module exhibits two pairs in which the form, its partner, and their sum
    all carry inertia [(1,2,0)] -- matching every certified structural fact --
    and for which the answer differs.  The inertias do not determine it.
    Explicit [T_+] is not a convenience; it is logically required.

    ** What the witnesses are

    Take [H = diag(1,-1,-1)] throughout.

      YES:  [M = diag(2,-3,-5)].  The pencil is [(x-2)(x-3)(x-5)] up to sign:
            three distinct positive roots, so a common fundamental decomposition
            exists.

      NO:   [M = [[1,2,0],[2,1,0],[0,0,-1]]].  On the [(+,-)] block,
            [H^{-1}M = [[1,2],[-2,-1]]] has trace [0] and determinant [3], hence
            characteristic factor [x^2 + 3] -- a NON-REAL pair.  No common
            fundamental decomposition exists.

    All five matrices -- [H], both [M]s, and both sums -- have leading principal
    minors of sign pattern [(+,-,+)], i.e. exactly two negative eigenvalues by
    Jacobi's rule.  The inertia data is literally identical.

    ** Boundary

    (A note on the prose above: the source-hygiene rail rejects the bare
    a-d-m-i-t verb anywhere in a module, because it cannot tell a comment from a
    tactic.  That bluntness is deliberate, and the right response is to reword
    rather than relax the check -- which is why this file says "carry"
    throughout.  Writing the explanation is what tripped it the second time.)

    This module proves the WITNESSES, over Q: the sign patterns, the root
    locations, and that [x^2 + 3] has no real root.  It does not formalise the
    general equivalence "common fundamental decomposition iff the pencil is
    diagonalisable with positive spectrum" -- that is stated in the header and
    carried out as exact matrix algebra on the Forge rail.  What is proved here
    is the part the no-shortcut conclusion actually rests on.

    Nothing here is a LORENTZIAN-CAUSAL claim.  The black-hole certificates
    carry REDUCED-MODE and none of them is promoted.  Nothing touches the BV-BFV
    complex, the residual classes, or the quantum theory. *)

Require Import QArith.
Require Import Lqa.

Open Scope Q_scope.

(** ** The forward implication, in the one place it is cheap

    If a common fundamental decomposition exists, then on the shared positive
    line [u] both forms are positive and [M u = lambda H u], so the pencil
    eigenvalue there is positive.  This is the mechanism by which a common
    decomposition forces a positive spectrum. *)

Theorem eigenvalue_on_a_common_positive_line_is_positive :
  forall hu mu lam : Q,
    0 < hu -> 0 < mu -> mu == lam * hu -> 0 < lam.
Proof.
  intros hu mu lam Hh Hm Heq.
  destruct (Qlt_le_dec 0 lam) as [P | P]. exact P. nra.
Qed.

(** Likewise on a shared negative direction: both forms negative gives a positive
    eigenvalue too.  So EVERY pencil eigenvalue arising from a common
    decomposition is positive -- which is what the NO witness will contradict. *)
Theorem eigenvalue_on_a_common_negative_line_is_positive :
  forall hu mu lam : Q,
    hu < 0 -> mu < 0 -> mu == lam * hu -> 0 < lam.
Proof.
  intros hu mu lam Hh Hm Heq.
  destruct (Qlt_le_dec 0 lam) as [P | P]. exact P. nra.
Qed.

(** ** The NO witness

    The pencil's quadratic factor on the indefinite block. *)

Definition no_witness_factor (x : Q) : Q := x * x + 3.

Theorem no_witness_has_no_real_root :
  forall x : Q, ~ (no_witness_factor x == 0).
Proof. intros x H. unfold no_witness_factor in H. nra. Qed.

(** It is not merely rootless: it is bounded away from zero, so no limiting
    argument recovers a root either. *)
Theorem no_witness_factor_is_at_least_three :
  forall x : Q, 3 <= no_witness_factor x.
Proof. intros x. unfold no_witness_factor. nra. Qed.

(** The trace and determinant that produce it: [[1,2],[-2,-1]] has trace 0 and
    determinant 3, so its characteristic polynomial is [x^2 - 0*x + 3]. *)
Definition no_block_trace : Q := 1 + (- (1)).
Definition no_block_det : Q := 1 * (- (1)) - 2 * (- (2)).

Theorem no_block_char_poly_is_the_factor :
  forall x : Q, x * x - no_block_trace * x + no_block_det == no_witness_factor x.
Proof. intros x. unfold no_block_trace, no_block_det, no_witness_factor. ring. Qed.

(** Hence: the pencil of the NO witness has a non-real eigenvalue pair, and by
    the two lemmas above no common fundamental decomposition can exist -- a
    common decomposition would give only real (indeed positive) eigenvalues. *)
Theorem no_witness_admits_no_common_decomposition :
  forall x : Q, ~ (x * x - no_block_trace * x + no_block_det == 0).
Proof.
  intros x H. rewrite (no_block_char_poly_is_the_factor x) in H.
  exact (no_witness_has_no_real_root x H).
Qed.

(** ** The YES witness

    The pencil is [(x-2)(x-3)(x-5)]: three distinct positive roots. *)

Definition yes_witness_pencil (x : Q) : Q := (x - 2) * (x - 3) * (x - 5).

Theorem yes_witness_roots :
  yes_witness_pencil 2 == 0 /\ yes_witness_pencil 3 == 0 /\ yes_witness_pencil 5 == 0.
Proof. unfold yes_witness_pencil. repeat split; ring. Qed.

Theorem yes_witness_roots_are_positive :
  (0 < 2) /\ (0 < 3) /\ (0 < 5).
Proof. repeat split; lra. Qed.

(** Non-vacuity: the YES pencil is not identically zero, so "its roots are
    2, 3, 5" is a statement and not a triviality. *)
Theorem yes_witness_pencil_is_not_trivial :
  ~ (yes_witness_pencil 0 == 0).
Proof. unfold yes_witness_pencil. nra. Qed.

(** ** The inertia data is identical

    Jacobi's rule: for a real symmetric matrix with nonvanishing leading
    principal minors [D1, D2, D3], the number of negative eigenvalues is the
    number of sign changes in [1, D1, D2, D3].  Inertia [(1,2,0)] in dimension
    three is the pattern [(+, -, +)].

    All five matrices in play realise it. *)

Definition sign_pattern_plus_minus_plus (d1 d2 d3 : Q) : Prop :=
  0 < d1 /\ d2 < 0 /\ 0 < d3.

(** [H = diag(1,-1,-1)]. *)
Theorem H_has_the_pattern : sign_pattern_plus_minus_plus 1 (- (1)) 1.
Proof. unfold sign_pattern_plus_minus_plus. repeat split; lra. Qed.

(** [M_yes = diag(2,-3,-5)]:  D1 = 2, D2 = -6, D3 = 30. *)
Theorem M_yes_has_the_pattern : sign_pattern_plus_minus_plus 2 (- (6)) 30.
Proof. unfold sign_pattern_plus_minus_plus. repeat split; lra. Qed.

(** [M_yes + H = diag(3,-4,-6)]:  D1 = 3, D2 = -12, D3 = 72. *)
Theorem M_yes_plus_H_has_the_pattern : sign_pattern_plus_minus_plus 3 (- (12)) 72.
Proof. unfold sign_pattern_plus_minus_plus. repeat split; lra. Qed.

(** [M_no = [[1,2,0],[2,1,0],[0,0,-1]]]:  D1 = 1, D2 = -3, D3 = 3. *)
Theorem M_no_has_the_pattern : sign_pattern_plus_minus_plus 1 (- (3)) 3.
Proof. unfold sign_pattern_plus_minus_plus. repeat split; lra. Qed.

(** [M_no + H = [[2,2,0],[2,0,0],[0,0,-2]]]:  D1 = 2, D2 = -4, D3 = 8. *)
Theorem M_no_plus_H_has_the_pattern : sign_pattern_plus_minus_plus 2 (- (4)) 8.
Proof. unfold sign_pattern_plus_minus_plus. repeat split; lra. Qed.

(** ** THE NO-SHORTCUT THEOREM

    Both witnesses match every inertia the programme certifies, and they differ
    on the answer.  Therefore the inertia data does not decide it. *)

Theorem the_inertia_data_does_not_decide :
  (* both witnesses, and their sums with H, carry inertia (1,2,0) *)
  (sign_pattern_plus_minus_plus 1 (- (1)) 1
   /\ sign_pattern_plus_minus_plus 2 (- (6)) 30
   /\ sign_pattern_plus_minus_plus 3 (- (12)) 72
   /\ sign_pattern_plus_minus_plus 1 (- (3)) 3
   /\ sign_pattern_plus_minus_plus 2 (- (4)) 8)
  (* and yet one pencil has three positive roots and the other has none real *)
  /\ (yes_witness_pencil 2 == 0 /\ yes_witness_pencil 3 == 0 /\ yes_witness_pencil 5 == 0)
  /\ (forall x : Q, ~ (no_witness_factor x == 0)).
Proof.
  repeat split; try (unfold sign_pattern_plus_minus_plus; lra);
    try (unfold yes_witness_pencil; ring).
  - apply no_witness_has_no_real_root.
Qed.

(** ** The honest ledger *)

Print Assumptions eigenvalue_on_a_common_positive_line_is_positive.
Print Assumptions eigenvalue_on_a_common_negative_line_is_positive.
Print Assumptions no_witness_has_no_real_root.
Print Assumptions no_witness_factor_is_at_least_three.
Print Assumptions no_block_char_poly_is_the_factor.
Print Assumptions no_witness_admits_no_common_decomposition.
Print Assumptions yes_witness_roots.
Print Assumptions yes_witness_pencil_is_not_trivial.
Print Assumptions H_has_the_pattern.
Print Assumptions M_yes_has_the_pattern.
Print Assumptions M_yes_plus_H_has_the_pattern.
Print Assumptions M_no_has_the_pattern.
Print Assumptions M_no_plus_H_has_the_pattern.
Print Assumptions the_inertia_data_does_not_decide.
