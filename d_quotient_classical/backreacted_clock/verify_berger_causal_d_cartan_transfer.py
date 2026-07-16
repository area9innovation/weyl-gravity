#!/usr/bin/env python3
"""Independent frozen-record audit of the conditional causal Cartan transfer."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reduce(terms: dict[tuple[str, ...], Fraction]) -> dict[tuple[str, ...], Fraction]:
    """Independent reducer for QL=1-LQ, QD=DQ and QA=AR."""
    pending = {word: value for word, value in terms.items() if value}
    while True:
        output: dict[tuple[str, ...], Fraction] = {}
        changed = False
        for word, coefficient in pending.items():
            products: tuple[tuple[tuple[str, ...], Fraction], ...] | None = None
            for index in range(len(word) - 1):
                pair = word[index : index + 2]
                before, after = word[:index], word[index + 2 :]
                if pair == ("Q", "L"):
                    products = (
                        (before + after, coefficient),
                        (before + ("L", "Q") + after, -coefficient),
                    )
                    break
                if pair == ("Q", "D"):
                    products = ((before + ("D", "Q") + after, coefficient),)
                    break
                if pair == ("Q", "A"):
                    products = ((before + ("A", "R") + after, coefficient),)
                    break
            if products is None:
                output[word] = output.get(word, Fraction(0)) + coefficient
            else:
                changed = True
                for new_word, value in products:
                    output[new_word] = output.get(new_word, Fraction(0)) + value
        pending = {word: value for word, value in output.items() if value}
        if not changed:
            return pending


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    assert payload["result_id"] == "BERGER_CAUSAL_D_CARTAN_TRANSFER"
    for dependency in payload["dependency_refs"].values():
        matches = list(ROOT.glob(f"**/{dependency['result_id']}.json"))
        assert len(matches) == 1, dependency["result_id"]
        assert _sha256(matches[0]) == dependency["sha256"]

    assumptions = payload["endpoint_assumptions"]
    unary = payload["unary_transfer"]
    binary = payload["arity_two_transfer"]
    assert assumptions["chain_homotopy"] == "q Lambda_s+Lambda_s q=1 for s in {+,-}"
    assert assumptions["D_chain_map"] == "q D-D q=0"
    assert unary["definition"] == "iota_D,s^(1)=Lambda_s D"
    assert unary["derivation"] == "q Lambda_s D+Lambda_s D q=(q Lambda_s+Lambda_s q)D=D"
    assert binary["closure"] == "delta A_D,s^(2)=-[q2,D]=[D,q2]=0"
    assert binary["raw_primitive"] == "iota_D,s,raw^(2)=-Lambda_s A_D,s^(2)"
    assert binary["raw_derivation"] == "for delta A=0, delta(Lambda_s A)=(q Lambda_s+Lambda_s q)A=A"
    unary_defect = {
        ("Q", "L", "D"): Fraction(1),
        ("L", "D", "Q"): Fraction(1),
        ("D",): Fraction(-1),
    }
    binary_defect = {
        ("Q", "L", "A"): Fraction(-1),
        ("L", "A", "R"): Fraction(-1),
        ("A",): Fraction(1),
    }
    assert not _reduce(unary_defect)
    assert not _reduce(binary_defect)
    assert payload["exact_checks"]["unary_noncommutative_rewrite_zero"] is True
    assert payload["exact_checks"]["arity_two_noncommutative_rewrite_zero"] is True

    flags = payload["flags"]
    assert flags["BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM"] is True
    assert flags["BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"] is False
    assert flags["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is False
    assert flags["BERGER_CAUSAL_D_CARTAN_EXTENSION"] is False
    assert payload["next_gate"] == "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"
    print("independent conditional causal D-Cartan transfer audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
