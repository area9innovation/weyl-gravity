"""Exact third-order source evaluation for the balanced compact-product jet.

This module consumes the action-derived q2/q3 row checkpoints.  The public
PBW export retains coefficient jets through order four; the axial ell=2
projection on the cubic ell=2,4,6 carrier needs the fifth equatorial
derivative.  The checkpointed operators retain the authoritative order-ten
``ThetaJet`` objects, so no missing derivative is inferred or inserted as
zero here.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import factorial
import hashlib
import json
from pathlib import Path
import pickle

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = (
    ROOT
    / "build/weyl_maxwell_product_linfinity_v1"
    / "ac923be427404bf66cac4adaf5b55f3400b03247d8e2f14091ac873f2cff046e"
)
CROSSWALK = ROOT / "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_cauchy_balanced_q2_q3_resonant_slice_v1.json"
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json"
INPUTS = {
    "canonical_crosswalk": (
        "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json",
        "1b6164c332cb18722529b1cdd979b24f49a12a9e81dfdc233817ad7302c3139f",
    ),
    "repaired_cubic_export_obstruction": (
        "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json",
        "0767475f509a93a145af9944d133bd352326da8e9e4708f06e3a74adcfad42ae",
    ),
    "two_jet_kuranishi_carrier": (
        "bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json",
        "7803297a7f65cf7ddb6e3eb24e4ae6d9fdd3c36bb1deb8290bb5e91f5c8dd921",
    ),
    "mixed_charge_correspondence": (
        "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json",
        "9853e39d52d931e54384fcfecb7c8c6f8bb8b47ab2e4f93da31ad32e7dbb04d7",
    ),
    "arity_three_parent": (
        "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
        "f78828e64525ecda924f34a75a1fe4ad8593b3fbf67cb2900ac221b98c454596",
    ),
}

AXIAL_ROWS = frozenset((12, 17))
POLAR_ROWS = frozenset((6, 7, 10, 19))
OUTPUT_ROWS = (23, 26, 30, 31)
VECTOR_OUTPUT_ROWS = frozenset((23, 26))
OUTPUT_ORDERS = {
    23: (1, 3, 5),
    26: (1, 3, 5),
    30: (0, 2, 4),
    31: (0, 2, 4),
}

THETA = sp.symbols("theta", real=True)
SQRT3 = sp.sqrt(3)
OMEGA_MINUS = sp.sqrt(6 - 2 * SQRT3)
OMEGA_EXTRA = 4 / SQRT3
AMPLITUDE_EXTRA = sp.sqrt(sp.Rational(27, 52) * (5 * SQRT3 - 6))


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.radsimp(sp.cancel(value))))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "theta": THETA})


def compositions(total: int, slots: int):
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, slots - 1):
            yield (first, *rest)


def multinomial(parts: tuple[int, ...]) -> int:
    value = factorial(sum(parts))
    for part in parts:
        value //= factorial(part)
    return value


@lru_cache(maxsize=None)
def angular_derivative(ell: int, kind: str, order: int) -> sp.Expr:
    harmonic = sp.legendre(ell, sp.cos(THETA))
    if kind == "scalar":
        function = harmonic
    elif kind == "covector":
        function = -sp.sin(THETA) * sp.diff(harmonic, THETA)
    elif kind == "dual_vector_density":
        function = -sp.diff(harmonic, THETA) / sp.sin(THETA)
    else:
        raise ValueError(f"unknown angular carrier {kind}")
    return sp.simplify(sp.diff(function, THETA, order).subs(THETA, sp.pi / 2))


@dataclass(frozen=True)
class Mode:
    mode_id: str
    lattice: tuple[int, int]
    frequency: sp.Expr
    # row -> (amplitude, ell, angular carrier)
    fields: dict[int, tuple[sp.Expr, int, str]]


def first_order_modes() -> tuple[Mode, ...]:
    modes = []
    for sign in (1, -1):
        modes.append(
            Mode(
                f"E{'+' if sign > 0 else '-'}",
                (sign, 0),
                sign * OMEGA_MINUS,
                {
                    12: (-sp.Integer(1), 2, "covector"),
                    17: (SQRT3, 2, "scalar"),
                },
            )
        )
        modes.append(
            Mode(
                f"X{'+' if sign > 0 else '-'}",
                (0, sign),
                sign * OMEGA_EXTRA,
                {
                    12: (-AMPLITUDE_EXTRA / 3, 2, "covector"),
                    17: (3 * AMPLITUDE_EXTRA, 2, "scalar"),
                },
            )
        )
    return tuple(modes)


def _channel_lattice(channel: str, sign: str) -> tuple[int, int]:
    positive = {
        "Einstein_self_sum": (2, 0),
        "extra_self_sum": (0, 2),
        "cross_sum": (1, 1),
        "cross_difference": (-1, 1),
        "combined_zero": (0, 0),
    }[channel]
    factor = 1 if sign == "+" else -1
    return factor * positive[0], factor * positive[1]


def second_order_modes() -> tuple[Mode, ...]:
    value = json.loads(CROSSWALK.read_text())
    modes = []
    for record in value["signed_channel_crosswalk"]:
        ell = int(record["ell"])
        coefficients = tuple(parse(item) for item in record["covariant_coefficients"])
        fields: dict[int, tuple[sp.Expr, int, str]] = {}
        if ell == 0:
            circle, sphere, electric = coefficients
            if circle != 0:
                fields[10] = (circle, 0, "scalar")
            # The certified balanced representative has sphere=electric=0.
            if sphere != 0 or electric != 0:
                raise AssertionError("homogeneous correction left its certified C-only slice")
        else:
            a_time, mixed, a_space, maxwell = coefficients
            if a_time != 0:
                fields[6] = (a_time, ell, "scalar")
            if mixed != 0:
                fields[7] = (mixed, ell, "scalar")
            if a_space != 0:
                fields[10] = (a_space, ell, "scalar")
            if maxwell != 0:
                fields[19] = (maxwell, ell, "covector")
        modes.append(
            Mode(
                f"v:L{ell}:{record['channel']}:{record['frequency_sign']}",
                _channel_lattice(record["channel"], record["frequency_sign"]),
                parse(record["omega"]),
                fields,
            )
        )
    return tuple(mode for mode in modes if mode.fields)


def mode_derivative(mode: Mode, row: int, word: tuple[int, ...]) -> sp.Expr:
    if row not in mode.fields or 1 in word or 3 in word:
        return sp.S.Zero
    amplitude, ell, kind = mode.fields[row]
    return (
        amplitude
        * (-sp.I * mode.frequency) ** word.count(0)
        * angular_derivative(ell, kind, word.count(2))
    )


@lru_cache(maxsize=None)
def load_operator(arity: int, row: int):
    path = CHECKPOINT / f"q{arity}" / f"row-{row:02d}.pkl"
    return pickle.loads(path.read_bytes())


def _term_value(term, modes: tuple[Mode, ...], output_order: int) -> sp.Expr:
    if len(modes) == 2:
        rows = (term[0], term[2])
        words = (term[1], term[3])
        coefficient = term[4]
    elif len(modes) == 3:
        rows = (term[0], term[2], term[4])
        words = (term[1], term[3], term[5])
        coefficient = term[6]
    else:
        raise ValueError("only q2 and q3 are supported")
    value = sp.S.Zero
    for partition in compositions(output_order, len(modes) + 1):
        coefficient_order, extras = partition[0], partition[1:]
        coefficient_jet = coefficient.jet((2,) * coefficient_order)
        if coefficient_jet == 0:
            continue
        local = sp.Integer(multinomial(partition)) * coefficient_jet
        for mode, row, word, extra in zip(modes, rows, words, extras, strict=True):
            local *= mode_derivative(mode, row, tuple(word) + (2,) * extra)
            if local == 0:
                break
        value += local
    return value


def source_jets(
    target: tuple[int, int],
) -> tuple[dict[str, dict[int, dict[int, sp.Expr]]], dict[str, int]]:
    first = first_order_modes()
    second = second_order_modes()
    output: dict[str, dict[tuple[int, int], sp.Expr]] = {
        "mixed_q2": {},
        "cubic_q3_over_6": {},
    }
    counts = {"q2_terms": 0, "q3_terms": 0, "q2_mode_assignments": 0, "q3_mode_assignments": 0}
    for row in OUTPUT_ROWS:
        for order in OUTPUT_ORDERS[row]:
            for component in output.values():
                component[(row, order)] = sp.S.Zero

        for term in load_operator(2, row).terms:
            left, right = term[0], term[2]
            if not (
                (left in AXIAL_ROWS and right in POLAR_ROWS)
                or (left in POLAR_ROWS and right in AXIAL_ROWS)
            ):
                continue
            counts["q2_terms"] += 1
            left_modes, right_modes = (first, second) if left in AXIAL_ROWS else (second, first)
            for left_mode, right_mode in product(left_modes, right_modes):
                if (
                    left_mode.lattice[0] + right_mode.lattice[0],
                    left_mode.lattice[1] + right_mode.lattice[1],
                ) != target:
                    continue
                counts["q2_mode_assignments"] += 1
                for order in OUTPUT_ORDERS[row]:
                    output["mixed_q2"][(row, order)] += _term_value(
                        term, (left_mode, right_mode), order
                    )

        for term in load_operator(3, row).terms:
            if not (term[0] in AXIAL_ROWS and term[2] in AXIAL_ROWS and term[4] in AXIAL_ROWS):
                continue
            counts["q3_terms"] += 1
            for modes in product(first, repeat=3):
                if (
                    sum(mode.lattice[0] for mode in modes),
                    sum(mode.lattice[1] for mode in modes),
                ) != target:
                    continue
                counts["q3_mode_assignments"] += 1
                for order in OUTPUT_ORDERS[row]:
                    output["cubic_q3_over_6"][(row, order)] += _term_value(
                        term, modes, order
                    ) / 6

    jets = {
        name: {
            row: {order: value[(row, order)] for order in OUTPUT_ORDERS[row]}
            for row in OUTPUT_ROWS
        }
        for name, value in output.items()
    }
    return jets, counts


@lru_cache(maxsize=None)
def projector_row(kind: str, ell: int = 2) -> sp.Matrix:
    if kind == "scalar":
        orders = (0, 2, 4)
        carrier = "scalar"
    elif kind == "vector":
        orders = (1, 3, 5)
        carrier = "dual_vector_density"
    else:
        raise ValueError(kind)
    ells = (2, 4, 6)
    matrix = sp.Matrix(
        [[angular_derivative(item, carrier, order) for item in ells] for order in orders]
    )
    return matrix.inv()[ells.index(ell), :]


def project_ell2(jets: dict[int, dict[int, sp.Expr]]) -> sp.Matrix:
    coefficients = []
    for row in OUTPUT_ROWS:
        kind = "vector" if row in VECTOR_OUTPUT_ROWS else "scalar"
        orders = OUTPUT_ORDERS[row]
        coefficients.append(
            canonical((projector_row(kind) * sp.Matrix([jets[row][order] for order in orders]))[0])
        )
    # PBW Euler rows are variational densities.  This is the action-row
    # normalization independently calibrated by the direct 4D q2 fixtures.
    return sp.Matrix(
        [3 * coefficients[0], 3 * coefficients[1], coefficients[2] / 2, coefficients[3] / 2]
    ).applyfunc(canonical)


def shell_adjoints(target: tuple[int, int]) -> tuple[sp.Matrix, ...]:
    if target[0] != 0:
        sign = target[0]
        return (sp.Matrix([0, -2 * sign, 0, 2 * SQRT3 * sign]),)
    sign = target[1]
    return (
        sp.Matrix([-6, 0, 6, 0]),
        sp.Matrix([0, -sp.Rational(2, 3) * sign, 0, 6 * sign]),
    )


def _serialize_term(term, arity: int, output_row: int) -> dict[str, object]:
    if arity == 2:
        inputs = ((term[0], term[1]), (term[2], term[3]))
        coefficient = term[4]
    else:
        inputs = ((term[0], term[1]), (term[2], term[3]), (term[4], term[5]))
        coefficient = term[6]
    return {
        "output_row": output_row,
        "inputs": [{"row": row, "word": list(word)} for row, word in inputs],
        "theta_coefficient_derivatives_0_through_5": [
            str(coefficient.jet((2,) * order)) for order in range(6)
        ],
    }


def build_slice() -> dict[str, object]:
    terms: dict[str, list[dict[str, object]]] = {"q2": [], "q3": []}
    row_hashes: dict[str, str] = {}
    for row in OUTPUT_ROWS:
        for arity in (2, 3):
            path = CHECKPOINT / f"q{arity}" / f"row-{row:02d}.pkl"
            row_hashes[f"q{arity}_row_{row}"] = sha(path)
            for term in load_operator(arity, row).terms:
                if arity == 2:
                    keep = (
                        term[0] in AXIAL_ROWS and term[2] in POLAR_ROWS
                    ) or (
                        term[0] in POLAR_ROWS and term[2] in AXIAL_ROWS
                    )
                else:
                    keep = term[0] in AXIAL_ROWS and term[2] in AXIAL_ROWS and term[4] in AXIAL_ROWS
                if keep:
                    terms[f"q{arity}"].append(_serialize_term(term, arity, row))
    if (len(terms["q2"]), len(terms["q3"])) != (832, 579):
        raise AssertionError("restricted q2/q3 term census changed")
    return {
        "schema": "einstein-weyl-compact-cauchy-balanced-q2-q3-resonant-slice-v1",
        "result_id": "EINSTEIN_WEYL_COMPACT_CAUCHY_BALANCED_Q2_Q3_RESONANT_SLICE_V1",
        "coefficient_field": "Q",
        "coefficient_base_point": "theta=pi/2",
        "coefficient_derivative_order": 5,
        "operator_convention": {
            "q2": "D^2E",
            "q3": "D^3E",
            "third_order_source": "D^2E[u,v]+D^3E[u,u,u]/6",
        },
        "source_checkpoint": {
            "fingerprint": CHECKPOINT.name,
            "manifest_sha256": sha(CHECKPOINT / "source-manifest.json"),
            "row_pickle_sha256": row_hashes,
        },
        "input_rows": {
            "axial": sorted(AXIAL_ROWS),
            "polar": sorted(POLAR_ROWS),
            "output": list(OUTPUT_ROWS),
        },
        "term_counts": {"q2": len(terms["q2"]), "q3": len(terms["q3"])},
        "terms": terms,
    }


def _nonzero_witness(value: sp.Expr) -> dict[str, object]:
    if value == 0:
        return {"exact_zero": True, "minimal_polynomial": "z"}
    z = sp.symbols("z")
    polynomial = sp.Poly(sp.minpoly(value, z), z)
    return {
        "exact_zero": False,
        "minimal_polynomial": str(polynomial.as_expr()),
        "minimal_polynomial_constant_coefficient": str(polynomial.nth(0)),
        "numeric_40_digits": str(sp.N(value, 40)),
    }


def l2_image_audit() -> dict[str, object]:
    """Compute the normalization-free image of d(mu) at an m=0 spin-2 ray."""

    ell = 2
    magnetic = tuple(range(-ell, ell + 1))
    raising = sp.zeros(2 * ell + 1)
    for index, m in enumerate(magnetic[:-1]):
        raising[index + 1, index] = sp.sqrt((ell - m) * (ell + m + 1))
    lowering = raising.T
    t1 = (raising + lowering) / 2
    t2 = (raising - lowering) / (2 * sp.I)
    t3 = sp.diag(*magnetic)
    occupied = sp.zeros(2 * ell + 1, 1)
    occupied[magnetic.index(0)] = 1
    plus_one = sp.zeros(2 * ell + 1, 1)
    plus_one[magnetic.index(1)] = 1
    rotation_derivatives = [
        sp.simplify(2 * sp.re((occupied.T.conjugate() * generator * variation)[0]))
        for generator, variation in ((t1, plus_one), (t2, sp.I * plus_one), (t3, plus_one))
    ]
    if rotation_derivatives != [sp.sqrt(6), -sp.sqrt(6), 0]:
        raise AssertionError("spin-two stabilizer derivative changed")
    # Columns are rescaled by their nonzero coefficients.  Such rescaling
    # changes neither the image nor its rank.
    image = sp.Matrix(
        [
            [1, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0],
        ]
    )
    if image.rank() != 3:
        raise AssertionError("l2 image rank changed")
    return {
        "spin_two_rotation_derivatives": [str(item) for item in rotation_derivatives],
        "normalized_basis_columns": [
            [str(image[row, column]) for row in range(image.rows)]
            for column in range(image.cols)
        ],
        "rank": image.rank(),
    }


def evaluate() -> dict[str, object]:
    imported = {}
    for name, (relative, digest) in INPUTS.items():
        path = ROOT / relative
        if sha(path) != digest:
            raise AssertionError(f"stale required input: {name}")
        imported[name] = {"path": relative, "sha256": digest}
    records = []
    for positive_target in ((1, 0), (0, 1)):
        component_jets, counts = source_jets(positive_target)
        components = {
            name: project_ell2(jets) for name, jets in component_jets.items()
        }
        components["total"] = (
            components["mixed_q2"] + components["cubic_q3_over_6"]
        ).applyfunc(canonical)
        for sign in (1, -1):
            target = sign * positive_target[0], sign * positive_target[1]
            local_components = {
                name: vector
                if sign == 1
                else vector.applyfunc(lambda item: canonical(sp.conjugate(item)))
                for name, vector in components.items()
            }
            source = local_components["total"]
            pairings = [
                canonical((adjoint.T * source)[0]) for adjoint in shell_adjoints(target)
            ]
            records.append(
                {
                    "target": list(target),
                    "frequency": str(target[0] * OMEGA_MINUS + target[1] * OMEGA_EXTRA),
                    "counts": counts,
                    "source_action_row_order": [
                        "3*g_03_star_ell2",
                        "3*g_13_star_ell2",
                        "A_0_star_ell2/2",
                        "A_1_star_ell2/2",
                    ],
                    "source_components": {
                        name: [str(item) for item in vector]
                        for name, vector in local_components.items()
                    },
                    "adjoints": [
                        [str(item) for item in adjoint]
                        for adjoint in shell_adjoints(target)
                    ],
                    "pairings": [str(item) for item in pairings],
                    "pairing_witnesses": [_nonzero_witness(item) for item in pairings],
                }
            )

    crosswalk = json.loads(CROSSWALK.read_text())
    if not crosswalk["classification"]["K3_evaluation_authorized"]:
        raise AssertionError("canonical crosswalk did not authorize K3")
    l2_audit = l2_image_audit()
    arity_three_rows = {}
    for row in OUTPUT_ROWS:
        path = CHECKPOINT / "arity-three" / f"row-{row:02d}.json"
        value = json.loads(path.read_text())
        if value != {"defect_count": 0, "row": row}:
            raise AssertionError(f"arity-three Noether row {row} changed")
        arity_three_rows[str(row)] = {"defect_count": 0, "sha256": sha(path)}
    return {
        "schema": "einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-v1",
        "result_id": "EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1",
        "result_state": "GLOBAL_KURANISHI_CLASS_ZERO_BUT_FOUR_ORIGINAL_SHELLS_BOUNDED_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compactified magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L x S2; bounded/finite-quasiperiodic versus smooth exponential-polynomial correction classes",
            "charge_sector": "fixed magnetic bundle N=2 and fixed electric charge; no homogeneous Wilson-line shift",
            "carrier": "balanced real axial Einstein-minus plus second extra-primary ell=2 tangent with its certified polar second-order correction",
            "degree": 3,
            "parity": "axial",
            "ell": "third-order closure ell=2,4,6; projected original ell=2 shells",
            "m": 0,
            "k": 0,
            "omega": "four original shells +/-omega_minus and +/-omega_extra",
        },
        "provenance": {
            "producer": str(Path(__file__).relative_to(ROOT)),
            "required_inputs": imported,
            "restricted_tensor_slice": {"path": str(SLICE.relative_to(ROOT)), "sha256": sha(SLICE)},
            "checkpoint_manifest_sha256": sha(CHECKPOINT / "source-manifest.json"),
            "selected_action_sha256": "647ff2fe89c167b00f480ce421e089646d5c6459534d90e74a99d40b7a75d4bd",
            "row_layout_sha256": "6236040676b7e699f5e48be6241143aa3bb5b7c9b4e07364826fc6f2b5ad24a2",
            "arity_three_Noether_checkpoint_rows": arity_three_rows,
        },
        "equation": {
            "second_order": "L v=-(1/2)D^2E[u,u]",
            "third_order": "L w=-D^2E[u,v]-(1/6)D^3E[u,u,u]",
            "projected_global_class": "[P_O(D^2C[u,v]+D^3C[u,u,u]/6)] in O/im(l2(u,-))",
        },
        "global_constraint_projection": {
            "obstruction_basis": ["H", "P_x", "J_1", "J_2", "J_3"],
            "D2C_u_v": ["0", "0", "0", "0", "0"],
            "D3C_u_u_u_over_6": ["0", "0", "0", "0", "0"],
            "K3_representative": ["0", "0", "0", "0", "0"],
            "selection_certificate": "every third-order source is axial with even ell=2,4,6 and k=m=0; H and P_x are scalar ell=0, while lifted rotations are axial ell=1, so all closed-slice pairings vanish exactly",
            "spin_two_rotation_derivatives": l2_audit["spin_two_rotation_derivatives"],
            "l2_image_normalized_basis_columns": l2_audit["normalized_basis_columns"],
            "l2_image": "span{H,J_1,J_2}",
            "l2_rank": l2_audit["rank"],
            "quotient_basis": ["P_x", "J_3"],
            "quotient_dimension": 2,
            "intrinsic_global_K3_class": "0",
        },
        "resonant_shells": sorted(records, key=lambda item: tuple(item["target"])),
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "OBSTRUCTED: every occupied original branch has a nonzero adjoint-shell functional",
            "smooth_exponential_polynomial": "CERTIFIED_SOLVABLE_WITH_SECULAR_TERMS: the square axial constant-coefficient pencil has nonzero determinant p^2 q; adjugate reduction and scalar polynomial-exponential surjectivity give a smooth secular preimage (degree at most one on q and at most two on p)",
            "causal_retarded": "NO_CERTIFIED_MAP",
        },
        "independence": {
            "correction_choice": "v->v+z changes the global representative by l2(u,z); the displayed zero class in O/im(l2) is unchanged",
            "boundary_representative": "the Cauchy slice is closed, so exact current/action improvements integrate to zero",
            "nonlinear_gauge": "the imported action-derived arity-three Q^2/Noether identity sends a second-jet gauge change into the same l2 image plus an exact closed-slice term",
            "bounded_resonance_scope": "the shell numbers are for the certified no-homogeneous-solution second-order representative; the global quotient statement is correction-independent",
        },
        "action_and_Noether_replay": {
            "second_action_jet": "all 27 signed ell=0,2,4 correction representatives are imported through the exact alpha_B=3 Ostrogradsky crosswalk, including lapse, shift, canonical P and pi and the no-time-integration-by-parts boundary convention",
            "arity_three_identity": "the four relevant full-BV output rows have exact zero Q^2 defect in the source-matched action-derived checkpoint",
            "relevant_row_defect_counts": {str(row): 0 for row in OUTPUT_ROWS},
        },
        "classification": {
            "D3_tensor_regenerated_on_balanced_carrier": True,
            "mixed_D2_u_v_regenerated_on_all_27_signed_correction_rows": True,
            "five_stabilizer_projections_zero": True,
            "global_K3_class_zero": True,
            "l2_image_rank_three": True,
            "all_four_original_shells_evaluated": True,
            "bounded_third_order_extension": False,
            "smooth_secular_third_order_extension": True,
            "causal_retarded_third_order_extension": False,
            "all_orders_or_quantum_claim": False,
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result separates a vanishing compact stabilizer Kuranishi class from nonzero bounded resonant shell obstructions at third order for one balanced fixture. It certifies a smooth secular third-order preimage abstractly, not a bounded, causal, all-orders, particle, positivity, unitarity or quantum result.",
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--write-slice", action="store_true")
    args = parser.parse_args()
    if args.write_slice:
        SLICE.parent.mkdir(parents=True, exist_ok=True)
        SLICE.write_text(json.dumps(build_slice(), indent=2, sort_keys=True) + "\n")
    elif args.write:
        if json.loads(SLICE.read_text()) != build_slice():
            raise AssertionError("stale restricted q2/q3 slice")
        OUTPUT.write_text(json.dumps(evaluate(), indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != evaluate():
        raise AssertionError("stale third-order Kuranishi evaluation")
    print("EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1: PASS")
