#!/usr/bin/env bash
# run.sh — the reverse-physics torus GATE.
#
# Eleven developments, all zero-axiom, in dependency order.  The first four are the
# torus chain, the next four an INDEPENDENT stochastic carrier, and the last two
# engage Carcassi-Aidala directly: a BRIDGE restating the torus results in their
# notation, and a PARITY OBSTRUCTION on their degree-of-freedom counting.
#
#   ReversePhysicsTorus.v          the TOPOLOGICAL step: at every mode with a
#                                  nonzero frequency closed = exact, so the
#                                  symplectic-to-Hamiltonian gap is carried
#                                  entirely by the zero mode -- for every
#                                  truncation, with no induction.
#   ReversePhysicsTorusChain.v     the REST of the chain: Hamiltonian <=
#                                  symplectic <= marginal <= volume-preserving at
#                                  every mode, both remaining inclusions proved
#                                  STRICT, and the marginal condition localised
#                                  as exactly the intra-DOF content.
#   ReversePhysicsTorusReversal.v  the REVERSAL: the law is EQUIVALENT to three
#                                  independent assumptions, each derived FROM the
#                                  law, with an independence witness per
#                                  assumption.
#   ReversePhysicsTorusSplit.v     WHY the third assumption is not physical: the
#                                  split-dependence of the first cancels against
#                                  it exactly, so the decomposition into a
#                                  "physical" and a "geometric" part is NOT
#                                  canonical.  Also corrects the earlier
#                                  split-dependence theorem, which had used an
#                                  ISOTROPIC pairing.
#   ReversePhysicsStochastic.v     a DIFFERENT carrier -- finite-state stochastic
#                                  evolution -- where determinism and
#                                  reversibility can actually FAIL, so the two
#                                  assumptions the stream had only ever consumed
#                                  can finally be tested.  Result: reversibility
#                                  is NOT independent; it is exactly determinism
#                                  plus information conservation.
#   ReversePhysicsSecondLaw.v      a SECOND LAW on that carrier: information
#                                  conservation entails that disorder never
#                                  decreases.  Exactly rational -- purity
#                                  (Renyi-2) rather than Shannon entropy, so no
#                                  logarithms.
#   ReversePhysicsEntropyEquality.v  the EQUALITY case, forward half: reversible
#                                  evolution preserves purity EXACTLY, and
#                                  spreading over states of differing probability
#                                  strictly produces entropy.
#   ReversePhysicsEntropyConverse.v  the CONVERSE, and so the BICONDITIONAL:
#                                  preserving purity on one distribution with
#                                  distinct entries forces reversibility.  The
#                                  loop between the stream's two laws is closed.
#   ReversePhysicsAOPBridge.v      the BRIDGE: our omega is proved to be their
#                                  J (x) I_n, their two tensor factors are shown
#                                  to be bookkeeping rather than physics, and
#                                  their open GR conjecture is shown to need a
#                                  topological term the finite-dimensional
#                                  theorem does not have.
#   ReversePhysicsConformalCount.v  the FOURTH DESIDERATUM: adding conformal
#                                  invariance to their DOF-counting trilemma
#                                  excludes the density branch in ODD dimension
#                                  by parity.  A Cauchy surface is
#                                  three-dimensional.
#   ReversePhysicsNoConformalCount.v  the LAST BRANCH: on flat space a dilation
#                                  is conformal, so every ball has the count of
#                                  the unit ball.  Additivity is never used, so
#                                  the non-additive resolution does not escape
#                                  either.  All three branches are closed.
#
# Print Assumptions must say "Closed under the global context" for every
# theorem, and coqchk must list NO axioms.
#
# Gates: [1] coqc  [2] source hygiene (no Axiom/Parameter/Admitted/admit)
#        [3] Print Assumptions all closed  [4] coqchk + empty axiom section
#        [5] fail-closed negative controls (FALSE claims must be REJECTED)
#
#   cd weyl-gravity/rocq && ./run.sh
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

MODULES=(ReversePhysicsTorus ReversePhysicsTorusChain ReversePhysicsTorusReversal ReversePhysicsTorusSplit ReversePhysicsStochastic ReversePhysicsSecondLaw ReversePhysicsEntropyEquality ReversePhysicsEntropyConverse ReversePhysicsAOPBridge ReversePhysicsConformalCount ReversePhysicsNoConformalCount)
pass=0
fail=0

echo "=== reverse-physics torus gate (Rocq) ==="
command -v coqc >/dev/null || { echo "coqc not found"; exit 1; }
coqc --version | head -1

echo; echo "[1] coqc (in dependency order)"
: > /tmp/rp_coqc.log
for m in "${MODULES[@]}"; do
  if coqc "$m.v" >>/tmp/rp_coqc.log 2>&1; then
    echo "  coqc $m.v OK"; pass=$((pass+1))
  else
    echo "  coqc $m.v FAILED:"; sed -n '1,40p' /tmp/rp_coqc.log; fail=$((fail+1))
  fi
done

echo; echo "[2] source hygiene"
hyg=0
for m in "${MODULES[@]}"; do
  if command grep -nE '^[[:space:]]*(Axiom|Parameter|Hypothesis|Conjecture|Admitted)\b|\badmit\b' "$m.v"; then
    echo "  $m.v declares an assumption or admits — REJECT"; hyg=1
  fi
done
if [ "$hyg" -eq 0 ]; then
  echo "  no Axiom/Parameter/Hypothesis/Conjecture/Admitted/admit in any module"; pass=$((pass+1))
else
  fail=$((fail+1))
fi

echo; echo "[3] Print Assumptions all closed"
want_n=0
for m in "${MODULES[@]}"; do
  want_n=$((want_n + $(command grep -c "^Print Assumptions" "$m.v")))
done
closed_n=$(command grep -c "^Closed under the global context" /tmp/rp_coqc.log)
if [ "$want_n" -gt 0 ] && [ "$closed_n" -eq "$want_n" ]; then
  echo "  $closed_n/$want_n closed under the global context"; pass=$((pass+1))
else
  echo "  NOT all closed ($closed_n/$want_n) — REJECT"; fail=$((fail+1))
fi

echo; echo "[4] coqchk (standalone kernel) + empty axiom section"
if coqchk -silent -o "${MODULES[@]}" >/tmp/rp_chk.log 2>&1; then
  echo "  coqchk OK (${MODULES[*]})"; pass=$((pass+1))
else
  echo "  coqchk FAILED:"; cat /tmp/rp_chk.log; fail=$((fail+1))
fi
if command grep -q '^\* Axioms: <none>' /tmp/rp_chk.log; then
  echo "  coqchk axiom section: <none> (fully closed development)"; pass=$((pass+1))
else
  echo "  coqchk REPORTS AXIOMS — REJECT:"; sed -n '/Axioms/,/^$/p' /tmp/rp_chk.log; fail=$((fail+1))
fi

echo; echo "[5] fail-closed negative controls"

# (a) The zero mode DOES carry classes, so 'closed implies exact' is FALSE there.
cat > _neg_a.v <<'NEG'
Require Import ReversePhysicsTorus.
(* FALSE on purpose: uniform translation is closed but NOT exact at the zero
   mode. A gate that accepts this proves nothing. *)
Theorem bogus_translation_is_exact :
  forall k, zero_mode k -> exact_form k (unit_form i0) zero_form.
Proof.
  intros k Hz.
  apply (proj2 (exact_at_zero_mode_iff_vanishing k (unit_form i0) zero_form Hz)).
  intros j. destruct j; split; reflexivity.
Qed.
NEG

# (b) The chain must not collapse: marginal does NOT imply symplectic.
cat > _neg_b.v <<'NEG'
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
(* FALSE on purpose: the shear witness is marginal and not symplectic, so a
   proof that marginal implies symplectic would collapse the chain. *)
Theorem bogus_marginal_implies_symplectic :
  forall k a b, marginal k a b -> symplectic k a b.
Proof.
  intros k a b Hm. exact Hm.
Qed.
NEG


# (c) The law is strictly stronger than A1 alone: a proof that marginal
#     information conservation suffices would contradict A2/A3 independence.
cat > _neg_c.v <<'NEG'
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
Require Import ReversePhysicsTorusReversal.
(* FALSE on purpose: dropping A2 and A3 must not still give the law. *)
Theorem bogus_marginal_suffices :
  forall k a b, marginal k a b -> hamiltonian k a b.
Proof.
  intros k a b Hm. exact Hm.
Qed.
NEG


# (d) marginal is NOT invariant across admissible symplectic splits.
cat > _neg_d.v <<'NEG'
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
Require Import ReversePhysicsTorusReversal.
Require Import ReversePhysicsTorusSplit.
(* FALSE on purpose: if marginal were split-invariant the whole point of
   ReversePhysicsTorusSplit.v would collapse. *)
Theorem bogus_marginal_is_split_invariant :
  forall k a b, marginal k a b -> marginal_rot k a b.
Proof.
  intros k a b H. exact H.
Qed.
NEG


# (e) Determinism alone must NOT give reversibility: the collapse map is
#     deterministic and destroys information.
cat > _neg_e.v <<'NEG'
Require Import ReversePhysicsStochastic.
(* FALSE on purpose: if determinism sufficed, the collapse witness would be
   contradictory and the stochastic result vacuous. *)
Theorem bogus_determinism_suffices :
  forall M, deterministic M -> reversible M.
Proof.
  intros M H. exact H.
Qed.
NEG


# (f) Disorder is not merely conserved -- the mixer strictly increases it.
cat > _neg_f.v <<'NEG'
Require Import QArith.
Require Import ReversePhysicsStochastic.
Require Import ReversePhysicsSecondLaw.
Open Scope Q_scope.
(* FALSE on purpose: a doubly stochastic evolution can strictly DECREASE purity,
   so claiming conservation would make the second law vacuous. *)
Theorem bogus_purity_is_conserved :
  forall M p, nonneg M -> (forall j, col_sum M j == 1) -> conserves_information M ->
    purity (evolve M p) == purity p.
Proof.
  intros. reflexivity.
Qed.
NEG


# (g) Preserving purity must NOT be automatic for doubly stochastic maps.
cat > _neg_g.v <<'NEG'
Require Import QArith.
Require Import ReversePhysicsStochastic.
Require Import ReversePhysicsSecondLaw.
Require Import ReversePhysicsEntropyEquality.
Open Scope Q_scope.
(* FALSE on purpose: the mixer is doubly stochastic and strictly loses purity,
   so preservation cannot follow from double stochasticity alone. *)
Theorem bogus_all_doubly_stochastic_preserve_purity :
  forall M p, conserves_information M -> purity (evolve M p) == purity p.
Proof.
  intros M p H. reflexivity.
Qed.
NEG


# (h) The test distribution must have DISTINCT entries.  Every doubly stochastic
#     map preserves the uniform distribution, so a uniform test detects nothing.
cat > _neg_h.v <<'NEG'
Require Import QArith.
Require Import ReversePhysicsStochastic.
Require Import ReversePhysicsSecondLaw.
Require Import ReversePhysicsEntropyEquality.
Require Import ReversePhysicsEntropyConverse.
Open Scope Q_scope.
Definition p_unif : St -> Q := fun _ => 1 # 4.
(* FALSE on purpose: the mixer preserves the uniform distribution exactly and is
   not reversible, so a uniform test distribution proves nothing.  This is why
   p_test has pairwise distinct entries. *)
Theorem bogus_uniform_test_suffices :
  forall M, (forall a b, 0 <= M a b) -> (forall j, col_sum M j == 1) ->
    conserves_information M ->
    purity (evolve M p_unif) == purity p_unif -> reversible M.
Proof.
  intros M Hnn Hcol Hrow Heq. exact Heq.
Qed.
NEG


# (i) Preserving omega must NOT give a global Hamiltonian on a state space with
#     b_1 =/= 0 -- this is exactly the term the AoP GR conjecture would need.
cat > _neg_i.v <<'NEG'
Require Import ReversePhysicsTorus.
Require Import ReversePhysicsTorusChain.
Require Import ReversePhysicsAOPBridge.
(* FALSE on purpose: uniform translation on T^4 preserves omega and admits no
   global Hamiltonian.  If this compiled, finding 3 of the bridge would be
   vacuous. *)
Theorem bogus_omega_preservation_suffices :
  forall k a b, symplectic k a b -> hamiltonian k a b.
Proof.
  intros k a b H. exact H.
Qed.
NEG


# (j) There is no conformally invariant DOF density on a 3-manifold.
cat > _neg_j.v <<'NEG'
Require Import ZArith.
Require Import ReversePhysicsConformalCount.
(* FALSE on purpose: the parity obstruction says no curvature scalar balances
   the volume weight in odd dimension.  If this compiled, the fourth
   desideratum would be vacuous. *)
Theorem bogus_conformal_density_in_three :
  exists c, is_conformal_density 3 c.
Proof.
  exists weyl_squared_weights. reflexivity.
Qed.
NEG


# (k) A conformally invariant count cannot grow with the radius.
cat > _neg_k.v <<'NEG'
Require Import QArith.
Require Import ReversePhysicsNoConformalCount.
Open Scope Q_scope.
(* FALSE on purpose: no_informative_conformal_count says all balls tie.  If a
   count could grow with radius the refutation would be vacuous. *)
Theorem bogus_count_grows_with_radius :
  forall (Metric Region : Type)
         (mu : Metric -> Region -> Q)
         (scale : Q -> Metric -> Metric)
         (dil : Q -> Region -> Region)
         (flat : Metric)
         (ball : Q -> Region),
    (forall lam U, 0 < lam -> mu flat (dil lam U) == mu (scale lam flat) U) ->
    (forall lam m U, 0 < lam -> mu (scale lam m) U == mu m U) ->
    (forall r, 0 < r -> ball r = dil r (ball 1)) ->
    mu flat (ball 1) < mu flat (ball 2).
Proof.
  intros. reflexivity.
Qed.
NEG

neg_ok=0
for n in _neg_a _neg_b _neg_c _neg_d _neg_e _neg_f _neg_g _neg_h _neg_i _neg_j _neg_k; do
  if coqc "$n.v" >/tmp/rp_neg.log 2>&1; then
    echo "  $n: FALSE claim was ACCEPTED — REJECT"; neg_ok=1
  else
    echo "  $n: false claim -> coqc REJECTS (fail-closed)"
  fi
done
if [ "$neg_ok" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi
rm -f _neg_[a-k].v _neg_[a-k].vo _neg_[a-k].vok _neg_[a-k].vos _neg_[a-k].glob ._neg_[a-k].aux

echo
if [ "$fail" -eq 0 ]; then
  echo "RESULT: $pass green (0 red)"
  echo "GATE: PASS"
  exit 0
else
  echo "RESULT: $pass green ($fail red)"
  echo "GATE: FAIL"
  exit 1
fi
