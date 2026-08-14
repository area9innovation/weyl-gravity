#!/usr/bin/env python3
"""Independent verifier for the generic-L BT complete-g4 two-loop result."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-general-l-two-loop-v1.schema.json",
)

Form = tuple[int, int, int]
TERMS = [
    ("U41^2", Fraction(1), 0, ((4, 1), (4, 1)), False),
    ("2*U31*U51", Fraction(2), 0, ((3, 1), (5, 1)), False),
    ("-2*U31*U41*U30", Fraction(-2), 0, ((3, 1), (4, 1), (3, 0)), False),
    ("-2*v*U31*U41*U32", Fraction(-2), 1, ((3, 1), (4, 1), (3, 2)), False),
    ("Cov(U31^2,U30^2)", Fraction(1, 2), 0, ((3, 1), (3, 1), (3, 0), (3, 0)), True),
    ("Cov(U31^2,U30*U32)", Fraction(1), 1, ((3, 1), (3, 1), (3, 0), (3, 2)), True),
    ("Cov(U31^2,U32^2)", Fraction(3, 2), 2, ((3, 1), (3, 1), (3, 2), (3, 2)), True),
    ("Cov(U31^2,-U40)", Fraction(-1), 0, ((3, 1), (3, 1), (4, 0)), True),
    ("Cov(U31^2,-v*U42)", Fraction(-1), 1, ((3, 1), (3, 1), (4, 2)), True),
    ("Cov(U31^2,-3*v^2*U44)", Fraction(-3), 2, ((3, 1), (3, 1), (4, 4)), True),
    ("Cov(U31^2,v*U31^2/2)", Fraction(1, 2), 1, ((3, 1), (3, 1), (3, 1), (3, 1)), True),
    ("Cov(U31^2,3*v^2*U31*U33)", Fraction(3), 2, ((3, 1), (3, 1), (3, 1), (3, 3)), True),
    ("Cov(U31^2,15*v^3*U33^2/2)", Fraction(15, 2), 3, ((3, 1), (3, 1), (3, 3), (3, 3)), True),
]


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matchings(vertices: tuple[int, ...]):
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        for tail in matchings(vertices[1:index] + vertices[index + 1 :]):
            yield ((first, vertices[index]),) + tail


def signatures(atoms: tuple[tuple[int, int], ...]) -> Counter:
    slots = tuple(
        vertex
        for vertex, (degree, h_legs) in enumerate(atoms)
        for _ in range(degree - h_legs)
    )
    result = Counter()
    for matching in matchings(slots):
        result[
            tuple(sorted(Counter(tuple(sorted(edge)) for edge in matching).items()))
        ] += 1
    return result


def add(left: Form, right: Form) -> Form:
    return tuple(x + y for x, y in zip(left, right))


def neg(value: Form) -> Form:
    return tuple(-x for x in value)


def even_form(value: Form) -> Form:
    for part in value:
        if part:
            return value if part > 0 else neg(value)
    return value


def graph_structure(vertex_count: int, edges: list[tuple[int, int]]) -> dict:
    components = [{vertex} for vertex in range(vertex_count)]
    tree: list[int] = []
    chords: list[int] = []
    for index, (u, v) in enumerate(edges):
        left = next(component for component in components if u in component)
        right = next(component for component in components if v in component)
        if left is right:
            chords.append(index)
        else:
            left.update(right)
            components.remove(right)
            tree.append(index)
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(vertex_count)]
    for index in tree:
        u, v = edges[index]
        adjacency[u].append((v, index))
        adjacency[v].append((u, index))
    parent = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    component_index = [-1] * vertex_count
    order: list[int] = []
    for number, component in enumerate(components):
        root = min(component)
        parent[root] = root
        stack = [root]
        while stack:
            vertex = stack.pop()
            component_index[vertex] = number
            order.append(vertex)
            for neighbor, index in adjacency[vertex]:
                if parent[neighbor] == -1:
                    parent[neighbor] = vertex
                    parent_edge[neighbor] = index
                    stack.append(neighbor)
    return {
        "components": components,
        "component_index": component_index,
        "chords": chords,
        "parent": parent,
        "parent_edge": parent_edge,
        "order": order,
    }


def solve_flow(vertex_count: int, edges: list[tuple[int, int]], sources: list[int]):
    structure = graph_structure(vertex_count, edges)
    if len(structure["chords"]) != 2:
        return None, structure
    momenta: list[Form | None] = [None] * len(edges)
    for index, value in zip(structure["chords"], ((1, 0, 0), (0, 1, 0))):
        momenta[index] = value
    balances = [(0, 0, source) for source in sources]
    for index in structure["chords"]:
        u, v = edges[index]
        value = momenta[index]
        assert value is not None
        if u != v:
            balances[u] = add(balances[u], value)
            balances[v] = add(balances[v], neg(value))
    parent = structure["parent"]
    for vertex in reversed(structure["order"]):
        if parent[vertex] == vertex:
            if balances[vertex] != (0, 0, 0):
                return None, structure
            continue
        index = structure["parent_edge"][vertex]
        u, _ = edges[index]
        endpoint = neg(balances[vertex])
        value = endpoint if u == vertex else neg(endpoint)
        momenta[index] = value
        balances[parent[vertex]] = add(
            balances[parent[vertex]], balances[vertex]
        )
    assert all(value is not None for value in momenta)
    return [value for value in momenta if value is not None], structure


def rational_atom_factor(atoms: tuple[tuple[int, int], ...]) -> Fraction:
    result = Fraction(1)
    for degree, h_legs in atoms:
        result *= Fraction(math.comb(degree, h_legs), 2**h_legs)
    return result


def reconstruct() -> tuple[dict, dict]:
    groups = defaultdict(Counter)
    source_conserving = 0
    zero_flows = 0
    contributing = 0
    maximum_source = 0
    for name, term_coefficient, v_power, atoms, covariance in TERMS:
        if (3, 3) in atoms:
            continue
        if sum(2 - (degree - h) for degree, h in atoms) - 2 * v_power != -2:
            raise AssertionError("normalization")
        vertex_count = len(atoms)
        for signature, multiplicity in signatures(atoms).items():
            edges = [edge for edge, count in signature for _ in range(count)]
            if covariance and not any(
                (u < 2 <= v) or (v < 2 <= u) for u, v in edges
            ):
                continue
            for mask in range(1 << len(edges)):
                bulk = [
                    edge
                    for index, edge in enumerate(edges)
                    if not mask & (1 << index)
                ]
                structure = graph_structure(vertex_count, bulk)
                if len(structure["chords"]) != 2:
                    continue
                endpoints = [
                    vertex
                    for vertex, (_, h_legs) in enumerate(atoms)
                    for _ in range(h_legs)
                ]
                for index, edge in enumerate(edges):
                    if mask & (1 << index):
                        endpoints.extend(edge)
                for signs in itertools.product((-1, 1), repeat=len(endpoints)):
                    sources = [0] * vertex_count
                    vertex_arguments: list[list[Form]] = [
                        [] for _ in range(vertex_count)
                    ]
                    for vertex, sign in zip(endpoints, signs):
                        sources[vertex] += sign
                        vertex_arguments[vertex].append((0, 0, sign))
                    component_sources = [
                        sum(sources[vertex] for vertex in component)
                        for component in structure["components"]
                    ]
                    maximum_source = max(
                        maximum_source, *(abs(value) for value in component_sources)
                    )
                    flow, _ = solve_flow(vertex_count, bulk, sources)
                    if flow is None:
                        continue
                    source_conserving += 1
                    if any(value == (0, 0, 0) for value in flow):
                        zero_flows += 1
                        continue
                    for value, (u, v) in zip(flow, bulk):
                        vertex_arguments[u].append(value)
                        vertex_arguments[v].append(neg(value))
                    kernels = tuple(
                        sorted(
                            (atoms[vertex][0], tuple(sorted(vertex_arguments[vertex])))
                            for vertex in range(vertex_count)
                        )
                    )
                    propagators = tuple(sorted(even_form(value) for value in flow))
                    fixed = propagators.count((0, 0, 1))
                    propagators = tuple(
                        value for value in propagators if value != (0, 0, 1)
                    )
                    rank = mask.bit_count()
                    scale = v_power + rank + fixed
                    coefficient = (
                        term_coefficient
                        * multiplicity
                        * rational_atom_factor(atoms)
                        * 2**v_power
                        * Fraction((-1) ** rank, 2**rank)
                    )
                    groups[(scale, kernels, propagators)][(name, rank)] += coefficient
                    contributing += 1
    stats = {
        "source_conserving_oriented_flow_count": source_conserving,
        "identically_zero_oriented_flow_count": zero_flows,
        "raw_oriented_flow_count": contributing,
        "precombination_integrand_count": len(groups),
        "exactly_canceled_integrand_count": sum(
            sum(origins.values(), Fraction(0)) == 0 for origins in groups.values()
        ),
        "surviving_integrand_count": sum(
            sum(origins.values(), Fraction(0)) != 0 for origins in groups.values()
        ),
        "maximum_component_source_absolute_value": maximum_source,
        "surviving_by_omega_p_inverse_square_power": {
            str(power): count
            for power, count in sorted(
                Counter(
                    key[0]
                    for key, origins in groups.items()
                    if sum(origins.values(), Fraction(0))
                ).items()
            )
        },
    }
    return groups, stats


def encode_integrand(key, origins) -> dict:
    scale, kernels, propagators = key
    rational = lambda value: {
        "numerator": value.numerator,
        "denominator": value.denominator,
    }
    return {
        "omega_p_inverse_square_power": scale,
        "coefficient": rational(sum(origins.values(), Fraction(0))),
        "kernels": [
            {
                "degree": degree,
                "arguments": [list(form) for form in arguments],
            }
            for degree, arguments in kernels
        ],
        "propagators": [list(form) for form in propagators],
        "origins": [
            {
                "term": name,
                "rank_insertions": rank,
                "coefficient": rational(coefficient),
            }
            for (name, rank), coefficient in sorted(origins.items())
            if coefficient
        ],
    }


def exact_l4_crosscheck() -> dict[str, Fraction]:
    one = (0, 2, 4, 2)
    momenta = list(itertools.product(range(4), repeat=4))

    def omega(q):
        return sum(one[value] for value in q)

    def shift(q, amount):
        return ((q[0] + amount) % 4, q[1], q[2], q[3])

    x_value = Fraction(0)
    y_value = Fraction(0)
    a = 2
    cosines = (Fraction(1), Fraction(0), Fraction(-1), Fraction(0))
    for q in momenta[1:]:
        b = omega(q)
        qp = shift(q, 1)
        if qp != (0, 0, 0, 0):
            c = omega(qp)
            vertex = a * a + b * b + c * c - 2 * (a * b + a * c + b * c)
            x_value += Fraction(vertex * vertex, 36 * b * b * c * c)
        cosine = cosines[q[0]]
        sine_squared = 1 - cosine * cosine
        k4 = Fraction(a, 6) * (
            2 * sine_squared
            + (2 - cosine) * b
            + a * (1 - cosine) ** 2
        )
        y_value += k4 / (b * b)
    denominator = 256 * a * a
    return {
        "X": x_value,
        "Y": y_value,
        "Y2": Fraction(72, denominator) * y_value * y_value,
        "XY": Fraction(108, denominator) * x_value * y_value,
        "R": Fraction(162, denominator) * x_value * x_value,
    }


def is_bubble_square(row: dict) -> bool:
    if decode(row["coefficient"]) != 81:
        return False
    kernels = [
        (kernel["degree"], tuple(tuple(form) for form in kernel["arguments"]))
        for kernel in row["kernels"]
    ]
    propagators = [tuple(form) for form in row["propagators"]]
    if len(kernels) != 4 or len(propagators) != 4:
        return False
    for axis in (0, 1):
        other = 1 - axis
        selected = [
            arguments
            for degree, arguments in kernels
            if degree == 3 and any(form[axis] for form in arguments)
        ]
        lines = [
            form for form in propagators if form[axis] and not form[other]
        ]
        if len(selected) != 2 or len(lines) != 2:
            return False
        if any(any(form[other] for form in arguments) for arguments in selected):
            return False
        if tuple(sorted(neg(form) for form in selected[0])) != selected[1]:
            return False
        external = [form for form in selected[0] if not form[0] and not form[1]]
        internal = [form for form in selected[0] if form not in external]
        if len(external) != 1 or abs(external[0][2]) != 1:
            return False
        if tuple(sorted(even_form(form) for form in internal)) != tuple(sorted(lines)):
            return False
    return True


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False
        if file_hash(data["data"]) != data["data_sha256"]:
            return False
        if file_hash(data["producer"]) != data["producer_sha256"]:
            return False
        with open(os.path.join(ROOT, data["data"]), encoding="utf-8") as handle:
            producer_data = json.load(handle)
        expected_atlas = {
            "volume_scope": producer_data["volume_scope"],
            "affine_notation": producer_data["affine_notation"],
            "statistics": producer_data["statistics"],
            "exact_cancellations": producer_data["exact_cancellations"],
            "surviving_integrands": producer_data["surviving_integrands"],
            "status": producer_data["status"],
        }
        if data["two_loop_atlas"] != expected_atlas:
            return False
        if data["factorized_conditioning_sector"] != producer_data[
            "factorized_conditioning_sector"
        ]:
            return False

        groups, stats = reconstruct()
        atlas = data["two_loop_atlas"]
        if atlas["statistics"] != stats:
            return False
        canceled = [
            encode_integrand(key, origins)
            for key, origins in sorted(groups.items())
            if sum(origins.values(), Fraction(0)) == 0
        ]
        surviving = [
            encode_integrand(key, origins)
            for key, origins in sorted(groups.items())
            if sum(origins.values(), Fraction(0)) != 0
        ]
        if atlas["exact_cancellations"] != canceled:
            return False
        if atlas["surviving_integrands"] != surviving:
            return False
        scale_one = [row for row in surviving if row["omega_p_inverse_square_power"] == 1]
        if len(scale_one) != 2 or not all(is_bubble_square(row) for row in scale_one):
            return False
        cancellation_patterns = Counter(
            tuple(
                sorted(
                    (origin["term"], origin["rank_insertions"])
                    for origin in row["origins"]
                )
            )
            for row in canceled
        )
        if cancellation_patterns != Counter(
            {
                tuple(sorted((("Cov(U31^2,U30^2)", 1), ("Cov(U31^2,v*U31^2/2)", 0)))): 2,
                tuple(sorted((("-2*U31*U41*U30", 0), ("-2*U31*U41*U30", 1)))): 2,
                tuple(sorted((("U41^2", 0), ("U41^2", 1)))): 1,
            }
        ):
            return False

        exact = exact_l4_crosscheck()
        fixture = data["factorized_conditioning_sector"][
            "exact_L4_normalization_crosscheck"
        ]
        expected = {
            "X_4": exact["X"],
            "Y_4": exact["Y"],
            "canceled_72_Y_squared_over_N_omega_p_squared": exact["Y2"],
            "each_canceled_108_XY_over_N_omega_p_squared": exact["XY"],
            "surviving_R_4": exact["R"],
        }
        if any(decode(fixture[key]) != value for key, value in expected.items()):
            return False

        # Independent arithmetic audit of the analytic constants.  The shell
        # cardinality is 64*m^3+16*m; H_R<=1+log R and
        # sum m^-3<=3/2 give 11/32+(1/4)log R after the sine chord bound.
        if (2 * 3 + 1) ** 4 - (2 * 3 - 1) ** 4 != 64 * 3**3 + 16 * 3:
            return False
        if Fraction(1, 4) + Fraction(3, 32) != Fraction(11, 32):
            return False
        if Fraction(4, 9) * 16 != Fraction(64, 9):
            return False
        if Fraction(162, 256) != Fraction(81, 128):
            return False

        required = {
            "generic_L_at_least_five_complete_two_loop_formula": "PROVED",
            "power_sized_Y_squared_and_XY_tadpole_survival": "CANCELED_EXACTLY",
            "factorized_conditioning_sector": "POSITIVE_O_LOG_SQUARED",
            "factorized_conditioning_sector_on_tuned_running_branch": "UNIFORMLY_BOUNDED",
            "remaining_fourteen_unfactorized_two_loop_kernel_bound": "OPEN",
            "large_volume_complete_M4_sign_and_scaling": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        if any(data["method_disposition"].get(key) != value for key, value in required.items()):
            return False
        return all(data["checks"].values())
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
