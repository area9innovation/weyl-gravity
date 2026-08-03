#!/usr/bin/env bash
# run.sh — the reverse-physics torus GATE.
#
# Three developments, all zero-axiom, in dependency order:
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

MODULES=(ReversePhysicsTorus ReversePhysicsTorusChain ReversePhysicsTorusReversal)
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

neg_ok=0
for n in _neg_a _neg_b _neg_c; do
  if coqc "$n.v" >/tmp/rp_neg.log 2>&1; then
    echo "  $n: FALSE claim was ACCEPTED — REJECT"; neg_ok=1
  else
    echo "  $n: false claim -> coqc REJECTS (fail-closed)"
  fi
done
if [ "$neg_ok" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi
rm -f _neg_[abc].v _neg_[abc].vo _neg_[abc].vok _neg_[abc].vos _neg_[abc].glob ._neg_[abc].aux

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
