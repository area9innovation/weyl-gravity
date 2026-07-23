#!/usr/bin/env python3
"""Independent verifier for the axial repeated-factor shortcut audit."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


class AuditError(AssertionError):
    """Raised when the repeated-factor evidence or boundary drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(expression: str) -> str:
    omega = sp.Symbol("omega")
    parsed = sp.sympify(expression, locals={"omega": omega, "I": sp.I})
    return sp.sstr(sp.expand(parsed)).replace(" ", "")


def _multiset(expressions: list[str]) -> Counter[str]:
    return Counter(_canonical(expression) for expression in expressions)


def verify_derivative_identities() -> None:
    """Separate scalar spectral derivatives from time-translation Jordan vectors."""

    x, lam, a, potential = sp.symbols("x lambda a V")
    u = sp.Function("u")(x, lam)

    def operator(field: sp.Expr) -> sp.Expr:
        return (
            sp.diff(field, x, 2)
            + a * sp.diff(field, x)
            + (lam - potential) * field
        )

    # d_lambda(P_lambda u) = P_lambda(d_lambda u) + u exactly.
    _require(
        sp.expand(
            sp.diff(operator(u), lam)
            - operator(sp.diff(u, lam))
            - u
        )
        == 0,
        "scalar spectral-derivative identity failed",
    )

    v, omega = sp.symbols("v omega", real=True)
    radial = sp.Function("radial")(omega)
    phase = sp.exp(sp.I * omega * v)
    full_derivative = sp.diff(phase * radial, omega)
    radial_sensitivity = phase * sp.diff(radial, omega)
    time_shift = lambda field: sp.diff(field, v) - sp.I * omega * field
    _require(
        sp.simplify(time_shift(full_derivative) - sp.I * phase * radial) == 0,
        "full frequency derivative is not the expected time Jordan vector",
    )
    _require(
        sp.simplify(time_shift(radial_sensitivity)) == 0,
        "fixed-frequency radial sensitivity was incorrectly made time-generalized",
    )


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-repeated-factor-audit-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency boundary drift",
    )

    imported: dict[str, dict[str, Any]] = {}
    for name, reference in data["imports"].items():
        path = Path(reference["path"])
        _require(
            not path.is_absolute() and ".." not in path.parts,
            f"unsafe import path: {name}",
        )
        full = ROOT / path
        _require(full.is_file(), f"missing import: {name}")
        _require(_sha256(full) == reference["sha256"], f"hash drift: {name}")
        _require(
            len(reference["commit"]) == 40
            and all(c in "0123456789abcdef" for c in reference["commit"]),
            f"invalid commit: {name}",
        )
        imported[name] = json.loads(full.read_text())

    operator = imported["axial_operator"]
    split = operator["branch_split"]
    _require(
        split["constants"] == {"p": "1/2", "q": "1"},
        "branch-split constants drift",
    )
    _require(
        "exactly the composition" in split["extra_branch"],
        "typed composition is absent",
    )

    complete = imported["complete_reconstruction"]
    dimensions = complete["dimension_and_rank"]
    expected_dimensions = {
        "Einstein_kernel_dimension": 2,
        "carrier_dimension": 4,
        "complete_metric_dimension": 6,
    }
    for key, value in expected_dimensions.items():
        _require(dimensions[key] == value, f"dimension drift: {key}")
    stated = data["dimension_obstruction"]
    _require(
        stated["Einstein_kernel_dimension"] == 2
        and stated["Ricci_carrier_solution_dimension"] == 4
        and stated["complete_Bach_solution_dimension"] == 6
        and stated["scalar_RW_order"] == 2
        and stated["scalar_RW_square_solution_dimension"] == 4,
        "dimension obstruction drift",
    )
    _require(6 != 4, "dimension mutation erased the scalar-square obstruction")

    horizon = imported["horizon_reach"]
    _require(
        "scalar solution exponents {0, -4*I*m*omega}"
        in horizon["rw_benchmark"]["statement"],
        "RW horizon exponent import drift",
    )
    carrier_horizon = [
        branch["exponent"]
        for branch in imported["endpoint_obstruction"][
            "carrier_endpoint_basis"
        ]["horizon"]["branches"]
    ]
    expected_carrier = ["0", "0", "-4*I*omega", "-2-4*I*omega"]
    _require(
        _multiset(carrier_horizon) == _multiset(expected_carrier),
        "imported carrier horizon exponents drift",
    )
    _require(
        _multiset(data["endpoint_obstruction"]["Ricci_carrier_horizon_exponents"])
        == _multiset(expected_carrier),
        "reported carrier horizon exponents drift",
    )
    scalar_square = ["0", "0", "-4*I*omega", "-4*I*omega"]
    _require(
        _multiset(carrier_horizon) != _multiset(scalar_square),
        "carrier was falsely identified with a scalar RW square",
    )

    full_horizon = [
        lift["carrier_exponent"]
        for lift in complete["endpoint_bases"]["horizon"][
            "additional_lifts"
        ].values()
    ] + [
        mode["H1_exponent"]
        for mode in complete["endpoint_bases"]["horizon"][
            "Einstein_kernel"
        ].values()
        if isinstance(mode, dict)
    ]
    expected_full = [
        "0", "0", "0", "-4*I*omega", "-1-4*I*omega", "-2-4*I*omega"
    ]
    _require(
        _multiset(full_horizon) == _multiset(expected_full),
        "complete horizon exponent multiset drift",
    )
    _require(
        _multiset(data["endpoint_obstruction"]["complete_Bach_horizon_exponents"])
        == _multiset(expected_full),
        "reported complete horizon exponent multiset drift",
    )

    infinity_lifts = complete["endpoint_bases"]["infinity"]["additional_lifts"]
    rates = Counter(_canonical(lift["carrier_rate"]) for lift in infinity_lifts)
    powers_by_rate: dict[str, list[str]] = {}
    for lift in infinity_lifts:
        powers_by_rate.setdefault(
            _canonical(lift["carrier_rate"]), []
        ).append(lift["carrier_power"])
    _require(
        rates == Counter({"0": 2, "-2*I*omega": 2}),
        "carrier infinity rate multiplicities drift",
    )
    _require(
        _multiset(powers_by_rate["0"]) == _multiset(["0", "-1"])
        and _multiset(powers_by_rate["-2*I*omega"])
        == _multiset(["-4*I*omega", "-4*I*omega-1"]),
        "carrier infinity power columns drift",
    )

    legacy = imported["legacy_metric_all_orders"]
    obstruction = imported["endpoint_obstruction"]["metric_reconstruction_gate"]
    _require(
        legacy["polynomial_mode"]["degree"] == 1
        and legacy["polynomial_mode"]["logarithm"] is False,
        "legacy radial polynomial import drift",
    )
    _require(
        obstruction["exact_omitted_row_residual"]
        == "3*I*(omega - 2*I)/r**2"
        and obstruction["pilot_interval_disjoint_from_zero_set"] is True,
        "legacy polynomial exclusion drift",
    )
    _require(
        data["legacy_radial_column"]["complete_status"]
        == "excluded from the complete six-dimensional module",
        "spurious radial column was promoted",
    )

    flags = data["claim_flags"]
    required_true = {
        "exact_typed_operator_composition_certified",
        "complete_module_scalar_RW_square_conjugacy_obstructed",
        "naive_doubled_RW_endpoint_identification_obstructed",
    }
    required_false = {
        "identical_matrix_factor_square_certified",
        "canonical_scalar_spectral_derivative_submodule_certified",
        "frequency_transport_sensitivities_are_physical_modes",
        "time_translation_Jordan_chain_certified",
        "legacy_polynomial_column_in_complete_module",
    }
    _require(
        all(flags.get(key) is True for key in required_true),
        "proved claim was demoted",
    )
    _require(
        all(flags.get(key) is False for key in required_false),
        "unproved repeated-factor or Jordan claim was promoted",
    )
    limits = set(data["does_not_establish"])
    _require(
        "nonexistence of every singular, nonlocal or frequency-dependent matrix equivalence"
        in limits
        and "nonexistence of every local three-component matrix repeated-factor representation"
        in limits
        and "a canonical scalar spectral-derivative submodule inside the complete Bach module"
        in limits,
        "claim boundary drift",
    )
    verify_derivative_identities()


def verify(path: Path = CERTIFICATE) -> None:
    verify_certificate(json.loads(path.read_text()))


def main() -> int:
    verify()
    print("PASS axial repeated-factor shortcut audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
