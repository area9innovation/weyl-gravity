(** * The whole four-level chain on T^4, proved rather than computed.

    [ReversePhysicsTorus.v] proved the topological step: at every mode with a
    nonzero frequency, closed = exact, so the symplectic-to-Hamiltonian gap is
    carried entirely by the zero mode.  The other two levels of the chain --

      Hamiltonian  <=  symplectic  <=  marginal  <=  volume-preserving

    -- were still only computed, by the Forge gate, at truncations N <= 3.  This
    file proves them, for every mode, and proves both remaining inclusions STRICT
    by explicit witnesses (an inclusion chain that silently collapsed would make
    the whole separation vacuous).

    THE STRUCTURAL PAYOFF.  [symplectic_implies_marginal] turns out to consume
    only TWO of the six closedness equations: the INTRA-degree-of-freedom pairs
    (i0,i1) and (i2,i3).  The other four -- the inter-DOF pairs -- are exactly
    what the marginal condition cannot see, and [marginal_not_symplectic] shows
    they are not implied.  That is the torus counterpart of the linear-carrier
    finding in the G0 certificate, where the residual obstruction sat precisely
    in the inter-DOF block J A_12 = -(A_21)^T J.  Two different carriers, the
    same localisation.

    BOUNDARY.  The per-mode rank computations and the arithmetic that sums
    per-mode dimensions into the totals tabulated in the G1 report are still NOT
    formalised; those remain the Forge gate's exact-rational computation.  What
    is proved here is the inclusion structure and its strictness, at every mode. *)

Require Import QArith.
Require Import ReversePhysicsTorus.

Open Scope Q_scope.

(** ** Vector fields, and the 1-form they induce *)

(** A vector field at mode [k] has components [X^j = a_j cos_k + b_j sin_k]. *)

(** [alpha = iota_X omega] with [omega = dq1^dp1 + dq2^dp2]:
    [alpha_0 = -X^1], [alpha_1 = X^0], [alpha_2 = -X^3], [alpha_3 = X^2].
    The same signed permutation sends the cos part of X to the cos part of alpha
    and the sin part to the sin part, so one function serves for both. *)
Definition alpha_of (a : Form) : Form :=
  fun j => match j with
           | i0 => - a i1
           | i1 => a i0
           | i2 => - a i3
           | i3 => a i2
           end.

(** X preserves omega. *)
Definition symplectic (k : Mode) (a b : Form) : Prop :=
  closed k (alpha_of a) (alpha_of b).

(** X is globally Hamiltonian. *)
Definition hamiltonian (k : Mode) (a b : Form) : Prop :=
  exact_form k (alpha_of a) (alpha_of b).

(** Each degree of freedom independently preserves its own phase-space area:
    the partial divergence in each conjugate pair vanishes. *)
Definition marginal (k : Mode) (a b : Form) : Prop :=
  (k i0 * a i0 + k i1 * a i1 == 0) /\ (k i0 * b i0 + k i1 * b i1 == 0) /\
  (k i2 * a i2 + k i3 * a i3 == 0) /\ (k i2 * b i2 + k i3 * b i3 == 0).

(** The total phase-space volume is preserved: the full divergence vanishes. *)
Definition volume (k : Mode) (a b : Form) : Prop :=
  (k i0 * a i0 + k i1 * a i1 + k i2 * a i2 + k i3 * a i3 == 0) /\
  (k i0 * b i0 + k i1 * b i1 + k i2 * b i2 + k i3 * b i3 == 0).

(** ** The chain: each level implies the next *)

(** Hamiltonian implies symplectic -- inherited from [exact_implies_closed]. *)
Theorem hamiltonian_implies_symplectic :
  forall k a b, hamiltonian k a b -> symplectic k a b.
Proof.
  intros k a b H. apply exact_implies_closed. exact H.
Qed.

(** Only the two INTRA-degree-of-freedom closedness equations, isolated. *)
Definition intra_dof_closed (k : Mode) (A B : Form) : Prop :=
  (k i0 * A i1 == k i1 * A i0) /\ (k i0 * B i1 == k i1 * B i0) /\
  (k i2 * A i3 == k i3 * A i2) /\ (k i2 * B i3 == k i3 * B i2).

Lemma closed_implies_intra_dof_closed :
  forall k A B, closed k A B -> intra_dof_closed k A B.
Proof.
  intros k A B H.
  destruct (H i0 i1) as [HA01 HB01].
  destruct (H i2 i3) as [HA23 HB23].
  repeat split; assumption.
Qed.

(** The marginal condition follows from the intra-DOF equations ALONE.  This is
    the sharp form of the next theorem, and it is what localises the gap. *)
Lemma intra_dof_closed_implies_marginal :
  forall k a b, intra_dof_closed k (alpha_of a) (alpha_of b) -> marginal k a b.
Proof.
  intros k a b [HA01 [HB01 [HA23 HB23]]].
  simpl in HA01, HB01, HA23, HB23.
  unfold marginal. repeat split.
  - rewrite HA01. ring.
  - rewrite HB01. ring.
  - rewrite HA23. ring.
  - rewrite HB23. ring.
Qed.

(** Symplectic implies marginal, at every mode. *)
Theorem symplectic_implies_marginal :
  forall k a b, symplectic k a b -> marginal k a b.
Proof.
  intros k a b Hs.
  apply intra_dof_closed_implies_marginal.
  apply closed_implies_intra_dof_closed.
  exact Hs.
Qed.

(** Marginal implies volume preserving, at every mode: add the two per-DOF
    equations. *)
Theorem marginal_implies_volume :
  forall k a b, marginal k a b -> volume k a b.
Proof.
  intros k a b [Ha01 [Hb01 [Ha23 Hb23]]].
  unfold volume. split.
  - transitivity ((k i0 * a i0 + k i1 * a i1) + (k i2 * a i2 + k i3 * a i3)).
    + ring.
    + rewrite Ha01, Ha23. ring.
  - transitivity ((k i0 * b i0 + k i1 * b i1) + (k i2 * b i2 + k i3 * b i3)).
    + ring.
    + rewrite Hb01, Hb23. ring.
Qed.

(** The whole chain in one statement. *)
Theorem the_chain :
  forall k a b,
    (hamiltonian k a b -> symplectic k a b) /\
    (symplectic k a b -> marginal k a b) /\
    (marginal k a b -> volume k a b).
Proof.
  intros k a b. split; [| split].
  - apply hamiltonian_implies_symplectic.
  - apply symplectic_implies_marginal.
  - apply marginal_implies_volume.
Qed.

(** ** Both remaining inclusions are STRICT *)

Definition mkmode (x0 x1 x2 x3 : Q) : Mode :=
  fun j => match j with i0 => x0 | i1 => x1 | i2 => x2 | i3 => x3 end.

Definition mkform (x0 x1 x2 x3 : Q) : Form :=
  fun j => match j with i0 => x0 | i1 => x1 | i2 => x2 | i3 => x3 end.

Definition b_zero : Form := mkform 0 0 0 0.

(** [X = cos(2 pi q2) d/dq1] : mode [e_{q2}], cos part [a = (1,0,0,0)]. *)
Definition k_shear : Mode := mkmode 0 0 1 0.
Definition a_shear : Form := mkform 1 0 0 0.

(** Every degree of freedom independently conserves its information, and the
    total volume is conserved -- yet X does not even preserve omega. *)
Theorem marginal_not_symplectic :
  marginal k_shear a_shear b_zero /\
  volume k_shear a_shear b_zero /\
  ~ symplectic k_shear a_shear b_zero.
Proof.
  split; [| split].
  - repeat split; compute; reflexivity.
  - split; compute; reflexivity.
  - intros Hs.
    destruct (Hs i1 i2) as [HA _].
    compute in HA. discriminate HA.
Qed.

(** [X = cos(2 pi (q1 + q2)) (d/dq1 - d/dq2)] : mode [(1,0,1,0)], cos part
    [a = (1,0,-1,0)].  The total divergence cancels between the two degrees of
    freedom, but neither preserves its own area: the first gains exactly what the
    second loses.  This is the torus form of the G0 witness [diag(I, -I)]. *)
Definition k_split : Mode := mkmode 1 0 1 0.
Definition a_split : Form := mkform 1 0 (-1) 0.

Theorem volume_not_marginal :
  volume k_split a_split b_zero /\ ~ marginal k_split a_split b_zero.
Proof.
  split.
  - split; compute; reflexivity.
  - intros [Ha01 _].
    compute in Ha01. discriminate Ha01.
Qed.

(** ** What the marginal condition cannot see *)

(** Putting the two together: the marginal condition is exactly the intra-DOF
    content of symplecticity, and the inter-DOF equations it drops are not
    recoverable -- [marginal_not_symplectic] is a field that satisfies every
    intra-DOF equation and violates an inter-DOF one.

    So on the torus, as on the linear carrier of the G0 certificate, the residual
    obstruction is inter-degree-of-freedom coupling, which no condition stated
    per degree of freedom can express. *)
Theorem marginal_is_exactly_the_intra_dof_content :
  (forall k a b, symplectic k a b -> intra_dof_closed k (alpha_of a) (alpha_of b)) /\
  (forall k a b, intra_dof_closed k (alpha_of a) (alpha_of b) -> marginal k a b) /\
  (intra_dof_closed k_shear (alpha_of a_shear) (alpha_of b_zero) /\
   ~ symplectic k_shear a_shear b_zero).
Proof.
  split; [| split].
  - intros k a b Hs. apply closed_implies_intra_dof_closed. exact Hs.
  - intros k a b H. apply intra_dof_closed_implies_marginal. exact H.
  - split.
    + repeat split; compute; reflexivity.
    + intros Hs. destruct (Hs i1 i2) as [HA _].
      compute in HA. discriminate HA.
Qed.

(** ** The honest ledger *)

Print Assumptions hamiltonian_implies_symplectic.
Print Assumptions closed_implies_intra_dof_closed.
Print Assumptions intra_dof_closed_implies_marginal.
Print Assumptions symplectic_implies_marginal.
Print Assumptions marginal_implies_volume.
Print Assumptions the_chain.
Print Assumptions marginal_not_symplectic.
Print Assumptions volume_not_marginal.
Print Assumptions marginal_is_exactly_the_intra_dof_content.
