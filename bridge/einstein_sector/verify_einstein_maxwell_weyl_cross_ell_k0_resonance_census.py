"""Independent exact verifier for the bounded cross-ell resonance census."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_resonance_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_resonance_census.schema.json"
BRANCHES = (-1, 0, 1)


def squarefree(value: int) -> tuple[int, int]:
    outside = 1
    inside = value
    divisor = 2
    while divisor * divisor <= inside:
        square = divisor * divisor
        while inside % square == 0:
            outside *= divisor
            inside //= square
        divisor += 1
    return outside, inside


def plus(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    answer = dict(left)
    for root, coefficient in right.items():
        answer[root] = answer.get(root, Fraction()) + coefficient
        if not answer[root]:
            del answer[root]
    return answer


def product(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    answer: dict[int, Fraction] = {}
    for root_left, coefficient_left in left.items():
        for root_right, coefficient_right in right.items():
            common = gcd(root_left, root_right)
            root = root_left * root_right // common**2
            answer[root] = answer.get(root, Fraction()) + coefficient_left * coefficient_right * common
            if not answer[root]:
                del answer[root]
    return answer


def shell(ell: int, branch: int) -> dict[int, Fraction]:
    lam = ell * (ell + 1)
    if branch == 0:
        return {1: Fraction(3 * lam - 2, 3)}
    outside, inside = squarefree(2 * lam)
    return plus({1: Fraction(lam)}, {inside: Fraction(branch * outside)})


def defect(first: dict[int, Fraction], second: dict[int, Fraction], target: dict[int, Fraction]) -> dict[int, Fraction]:
    delta = plus(plus(target, {root: -coefficient for root, coefficient in first.items()}), {root: -coefficient for root, coefficient in second.items()})
    four_product = {root: -4 * coefficient for root, coefficient in product(first, second).items()}
    return plus(product(delta, delta), four_product)


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    assert payload["provenance"]["generator_sha256"] == hashlib.sha256(
        (ROOT / payload["provenance"]["generator_path"]).read_bytes()
    ).hexdigest()

    # These polynomial inequalities prove the candidate reduction without
    # importing the producer's floating-point localization.
    for ell in range(2, 97):
        assert 32 * ell**2 - 48 * ell + 1 > 0  # omega_minus > ell-1/2
        assert 32 * ell**2 + 112 * ell + 81 > 0  # omega_plus < ell+3/2
    for output_ell in range(1, 193):
        assert (7 * output_ell - 1) * (output_ell - 1) >= 0
        assert 7 * output_ell**2 + 22 * output_ell + 16 > 0

    collisions = 0
    resonance_checks = 0
    for ell_first in range(2, 97):
        for ell_second in range(ell_first + 1, 97):
            total = ell_first + ell_second
            difference = ell_second - ell_first
            outputs = tuple(range(total - 2, total + 1)) + tuple(range(difference, difference + 3))
            for branch_first in BRANCHES:
                first = shell(ell_first, branch_first)
                for branch_second in BRANCHES:
                    second = shell(ell_second, branch_second)
                    collisions += 1
                    assert plus(first, {root: -coefficient for root, coefficient in second.items()})
                    for output_ell in outputs:
                        for target_branch in BRANCHES:
                            resonance_checks += 1
                            assert defect(first, second, shell(output_ell, target_branch))

    assert collisions == payload["census"]["frequency_collision_checks"] == 40185
    assert resonance_checks == payload["census"]["squared_resonance_checks"] == 723330

    nearest = payload["census"]["nearest_nonresonant_channel"]
    assert nearest["labels"] == [5, 34, "extra", "Einstein_plus", "difference", 30, "Einstein_minus"]
    expected = defect(shell(5, 0), shell(34, 1), shell(30, -1))
    serialized = [
        {"radicand": root, "coefficient": str(coefficient)}
        for root, coefficient in sorted(expected.items())
    ]
    assert serialized == nearest["exact_squared_resonance_polynomial"]
    assert payload["classification"]["unbounded_cross_ell_theorem_proved"] is False
    assert payload["classification"]["cross_ell_quadratic_source_solved"] is False


if __name__ == "__main__":
    main()
