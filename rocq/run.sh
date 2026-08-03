#!/usr/bin/env bash
# run.sh — the reverse-physics torus GATE.
#
# Closes the REVERSE_PHYSICS_TORUS_ALL_TRUNCATIONS gate: the Forge gate
# (tango forge/examples/reverse_physics_torus_gate.forge) computes the
# symplectic-minus-Hamiltonian gap on T^4 at truncations N = 0..3; this proves the
# per-mode statement for EVERY mode, which subsumes every truncation.
#
# Zero axioms, zero parameters: Print Assumptions must say "Closed under the
# global context" for every theorem, and coqchk must list NO axioms.
#
# Gates: [1] coqc  [2] source hygiene (no Axiom/Parameter/Admitted/admit)
#        [3] Print Assumptions all closed  [4] coqchk + empty axiom section
#        [5] fail-closed negative control (a FALSE claim must be REJECTED)
#
#   cd weyl-gravity/rocq && ./run.sh
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

SRC=ReversePhysicsTorus.v
MOD=ReversePhysicsTorus
pass=0
fail=0

echo "=== reverse-physics torus gate (Rocq) ==="
command -v coqc >/dev/null || { echo "coqc not found"; exit 1; }
coqc --version | head -1

echo; echo "[1] coqc $SRC"
if coqc "$SRC" >/tmp/rp_coqc.log 2>&1; then
  echo "  coqc OK"; pass=$((pass+1))
else
  echo "  coqc FAILED:"; sed -n '1,40p' /tmp/rp_coqc.log; fail=$((fail+1))
fi

echo; echo "[2] source hygiene"
if command grep -nE '^[[:space:]]*(Axiom|Parameter|Hypothesis|Conjecture|Admitted)\b|\badmit\b' "$SRC"; then
  echo "  declared assumption or admit present — REJECT"; fail=$((fail+1))
else
  echo "  no Axiom/Parameter/Hypothesis/Conjecture/Admitted/admit"; pass=$((pass+1))
fi

echo; echo "[3] Print Assumptions all closed"
want_n=$(command grep -c "^Print Assumptions" "$SRC")
closed_n=$(command grep -c "^Closed under the global context" /tmp/rp_coqc.log)
if [ "$want_n" -gt 0 ] && [ "$closed_n" -eq "$want_n" ]; then
  echo "  $closed_n/$want_n closed under the global context"; pass=$((pass+1))
else
  echo "  NOT all closed ($closed_n/$want_n) — REJECT"; fail=$((fail+1))
fi

echo; echo "[4] coqchk (standalone kernel) + empty axiom section"
if coqchk -silent -o "$MOD" >/tmp/rp_chk.log 2>&1; then
  echo "  coqchk OK"; pass=$((pass+1))
else
  echo "  coqchk FAILED:"; cat /tmp/rp_chk.log; fail=$((fail+1))
fi
if command grep -q '^\* Axioms: <none>' /tmp/rp_chk.log; then
  echo "  coqchk axiom section: <none> (fully closed development)"; pass=$((pass+1))
else
  echo "  coqchk REPORTS AXIOMS — REJECT:"; sed -n '/Axioms/,/^$/p' /tmp/rp_chk.log; fail=$((fail+1))
fi

echo; echo "[5] fail-closed negative control"
# The zero mode DOES carry classes, so 'closed implies exact' is FALSE there.
# If this compiled, the development would be inconsistent or the theorems vacuous.
cat > _neg_control.v <<'NEG'
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
if coqc _neg_control.v >/tmp/rp_neg.log 2>&1; then
  echo "  FALSE claim was ACCEPTED — REJECT"; fail=$((fail+1))
else
  echo "  false claim -> coqc REJECTS (fail-closed)"; pass=$((pass+1))
fi
rm -f _neg_control.v _neg_control.vo _neg_control.vok _neg_control.vos _neg_control.glob ._neg_control.aux

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
