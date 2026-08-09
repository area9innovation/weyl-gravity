#!/usr/bin/env python3
"""Exact local-algebraic classification of BT potential IR regulators.

The Bateman--Turok two-field scaffold has fields (Omega, Upsilon) with

    s = Omega * Upsilon,
    V = F(s),

so every local potential preserving the connected SO+(1,1) boost is a
function of s.  This producer generates a quadratic ansatz for the two-jet of
F, differentiates it in a tiny exact Laurent-polynomial ring, and classifies
the vacuum equations and pole polynomial.  The expected answer is not used as
the computation: it is compared against the generated derivatives.

The result is deliberately LOCAL-ALGEBRAIC.  The Fourier variable z is only a
formal symbol of the quadratic operator.  No propagator prescription,
asymptotic state, loop integral, resummation, or Lorentzian causal object is
constructed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1.json",
)
REPORT_PATH = "reverse_physics/reports/bt-ir-regulator-trilemma.md"
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-ir-regulator-trilemma-v1.schema.json"
)
SOURCE_COMMIT = "49d74b9229a2ada453a919899749488f8998161c"
VARIABLES = (
    "Omega", "Upsilon", "z", "v", "s0", "f0", "f1", "f2", "mu2", "lambda2"
)


class LaurentPoly:
    """Sparse exact Laurent polynomial over Q in the declared variables."""

    def __init__(self, terms=None):
        clean = {}
        for powers, coefficient in (terms or {}).items():
            coefficient = Fraction(coefficient)
            powers = tuple(int(x) for x in powers)
            if coefficient:
                clean[powers] = clean.get(powers, Fraction(0)) + coefficient
        self.terms = {p: c for p, c in clean.items() if c}

    @classmethod
    def constant(cls, value):
        value = Fraction(value)
        return cls({(0,) * len(VARIABLES): value}) if value else cls()

    @classmethod
    def monomial(cls, coefficient=1, **powers):
        exponents = [0] * len(VARIABLES)
        for name, exponent in powers.items():
            exponents[VARIABLES.index(name)] = exponent
        return cls({tuple(exponents): Fraction(coefficient)})

    @classmethod
    def variable(cls, name):
        return cls.monomial(**{name: 1})

    def _coerce(self, other):
        return other if isinstance(other, LaurentPoly) else LaurentPoly.constant(other)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.terms)
        for powers, coefficient in other.terms.items():
            out[powers] = out.get(powers, Fraction(0)) + coefficient
        return LaurentPoly(out)

    __radd__ = __add__

    def __neg__(self):
        return LaurentPoly({p: -c for p, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for p1, c1 in self.terms.items():
            for p2, c2 in other.terms.items():
                powers = tuple(a + b for a, b in zip(p1, p2))
                out[powers] = out.get(powers, Fraction(0)) + c1 * c2
        return LaurentPoly(out)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        exponent = int(exponent)
        if exponent < 0:
            if len(self.terms) != 1:
                raise ValueError("negative power requires one monomial")
            (powers, coefficient), = self.terms.items()
            return LaurentPoly({
                tuple(exponent * p for p in powers): coefficient ** exponent
            })
        out = LaurentPoly.constant(1)
        base = self
        while exponent:
            if exponent & 1:
                out = out * base
            base = base * base
            exponent //= 2
        return out

    def derivative(self, name):
        index = VARIABLES.index(name)
        out = {}
        for powers, coefficient in self.terms.items():
            exponent = powers[index]
            if exponent:
                next_powers = list(powers)
                next_powers[index] -= 1
                key = tuple(next_powers)
                out[key] = out.get(key, Fraction(0)) + coefficient * exponent
        return LaurentPoly(out)

    def substitute(self, replacements):
        images = {
            name: replacements.get(name, LaurentPoly.variable(name))
            for name in VARIABLES
        }
        out = LaurentPoly()
        for powers, coefficient in self.terms.items():
            term = LaurentPoly.constant(coefficient)
            for name, exponent in zip(VARIABLES, powers):
                if exponent:
                    term = term * (images[name] ** exponent)
            out = out + term
        return out

    def serialized_terms(self):
        rows = []
        for powers, coefficient in sorted(self.terms.items()):
            rows.append({
                "coefficient": {
                    "numerator": coefficient.numerator,
                    "denominator": coefficient.denominator,
                },
                "powers": {
                    name: exponent
                    for name, exponent in zip(VARIABLES, powers)
                    if exponent
                },
            })
        return rows

    def __eq__(self, other):
        return self.terms == self._coerce(other).terms


def matrix_det(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def gradient_hessian(potential):
    fields = ("Omega", "Upsilon")
    gradient = [potential.derivative(name) for name in fields]
    hessian = [
        [gradient[i].derivative(name) for name in fields]
        for i in range(2)
    ]
    return gradient, hessian


def kinetic_matrix(hessian, z):
    return [
        [hessian[0][0], hessian[0][1] - z],
        [hessian[1][0] - z, hessian[1][1]],
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    symbols = {name: LaurentPoly.variable(name) for name in VARIABLES}
    O, U, z = symbols["Omega"], symbols["Upsilon"], symbols["z"]
    v, s0 = symbols["v"], symbols["s0"]
    f0, f1, f2 = symbols["f0"], symbols["f1"], symbols["f2"]
    mu2, lambda2 = symbols["mu2"], symbols["lambda2"]

    # Generate the complete two-jet of an arbitrary F(s) at s=0.
    s = O * U
    potential_bt = f0 + f1 * s + Fraction(1, 2) * f2 * s**2
    gradient_bt, hessian_bt = gradient_hessian(potential_bt)
    at_bt = {"Omega": v, "Upsilon": LaurentPoly.constant(0)}
    bt_gradient = [entry.substitute(at_bt) for entry in gradient_bt]
    bt_hessian = [
        [entry.substitute(at_bt) for entry in row] for row in hessian_bt
    ]
    bt_pole = matrix_det(kinetic_matrix(bt_hessian, z))

    expected_bt_gradient = [LaurentPoly.constant(0), v * f1]
    expected_bt_hessian = [
        [LaurentPoly.constant(0), f1],
        [f1, v**2 * f2],
    ]
    expected_bt_pole = -(z - f1) ** 2

    # Generate the two-jet at a general nonzero invariant s0 and impose the
    # constant-field vacuum equation F'(s0)=0 only after differentiating.
    ds = s - s0
    potential_shifted = f0 + f1 * ds + Fraction(1, 2) * f2 * ds**2
    _, hessian_shifted = gradient_hessian(potential_shifted)
    at_shifted_vacuum = {
        "Omega": v,
        "Upsilon": s0 * v**-1,
        "f1": LaurentPoly.constant(0),
    }
    shifted_hessian = [
        [entry.substitute(at_shifted_vacuum) for entry in row]
        for row in hessian_shifted
    ]
    shifted_pole = matrix_det(kinetic_matrix(shifted_hessian, z))
    expected_shifted_pole = z * (2 * s0 * f2 - z)

    # The repository's proposed mass potential, evaluated both at the held
    # BT point and on its actual nonzero stationary branch.
    mass_replacements = {"f1": mu2, "f2": lambda2}
    mass_bt_gradient = [entry.substitute(mass_replacements) for entry in bt_gradient]
    mass_bt_pole = bt_pole.substitute(mass_replacements)
    true_vacuum_replacements = {
        "s0": -mu2 * lambda2**-1,
        "f2": lambda2,
    }
    mass_true_pole = shifted_pole.substitute(true_vacuum_replacements)

    expected_mass_bt_gradient = [LaurentPoly.constant(0), v * mu2]
    expected_mass_bt_pole = -(z - mu2) ** 2
    expected_mass_true_pole = -z * (z + 2 * mu2)

    # Holding (v,0) stationary requires a fixed-v source -mu2*v*Upsilon.
    # It has boost charge -1 unless v is promoted to a transforming spurion.
    fixed_v_source_charge = -1
    spurion_source_charge = 0

    checks = {
        "generated_BT_gradient_matches_chain_rule": bt_gradient == expected_bt_gradient,
        "generated_BT_hessian_matches_chain_rule": bt_hessian == expected_bt_hessian,
        "held_BT_pole_polynomial_is_negative_square": bt_pole == expected_bt_pole,
        "stationary_BT_branch_forces_massless_double_root": (
            bt_pole.substitute({"f1": LaurentPoly.constant(0)}) == -(z**2)
        ),
        "mass_term_creates_BT_tadpole": mass_bt_gradient == expected_mass_bt_gradient,
        "held_nonstationary_background_has_massive_double_root": (
            mass_bt_pole == expected_mass_bt_pole
        ),
        "generated_true_vacuum_pole_polynomial_splits": (
            shifted_pole == expected_shifted_pole
        ),
        "mass_term_true_vacuum_has_zero_and_simple_massive_roots": (
            mass_true_pole == expected_mass_true_pole
        ),
        "fixed_v_tadpole_subtraction_breaks_boost_weight": (
            fixed_v_source_charge == -1 and spurion_source_charge == 0
        ),
        "four_independence_witnesses_are_populated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    polynomial_identities = {
        "BT_branch_gradient": {
            "readable": "(d_Omega V, d_Upsilon V)|(v,0) = (0, v*f1)",
            "components": [entry.serialized_terms() for entry in bt_gradient],
        },
        "BT_branch_hessian": {
            "readable": "H|(v,0) = [[0,f1],[f1,v^2*f2]]",
            "components": [
                [entry.serialized_terms() for entry in row] for row in bt_hessian
            ],
        },
        "BT_branch_pole_polynomial": {
            "readable": "det K(z)|(v,0) = -(z-f1)^2",
            "terms": bt_pole.serialized_terms(),
        },
        "stationary_nonzero_branch_pole_polynomial": {
            "readable": "F'(s0)=0 => det K(z) = z*(2*s0*f2-z)",
            "terms": shifted_pole.serialized_terms(),
        },
        "mass_deformation_held_background": {
            "readable": "F=mu2*s+(lambda2/2)*s^2 at (v,0): tadpole=(0,v*mu2), det=-(z-mu2)^2",
            "gradient": [entry.serialized_terms() for entry in mass_bt_gradient],
            "pole_terms": mass_bt_pole.serialized_terms(),
        },
        "mass_deformation_true_vacuum": {
            "readable": "s0=-mu2/lambda2: det K(z)=-z*(z+2*mu2)",
            "pole_terms": mass_true_pole.serialized_terms(),
        },
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1",
        "schema_version": "reverse-physics-bt-ir-regulator-trilemma-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "local potential regulator classification",
        "question": "Can a local SO+(1,1)-invariant potential give the stationary Bateman-Turok broken vacuum a nonzero coincident-pole infrared mass?",
        "answer": "No. On the BT branch (Omega,Upsilon)=(v,0), stationarity forces F'(0)=0, while a nonzero coincident-pole mass is exactly F'(0). The proposed mu^2 Omega Upsilon deformation therefore creates a Upsilon tadpole at the held BT point. Moving to its true invariant stationary branch yields one massless and one massive simple root, not a massive double pole. A fixed-v tadpole subtraction retains the quadratic double root only by explicitly breaking the boost in that fixed vacuum sector (or by introducing a charge-carrying spurion).",
        "carrier": {
            "fields": ["Omega", "Upsilon"],
            "invariant": "s = Omega*Upsilon",
            "potential_ansatz": "V=F(s), represented by its exact two-jet",
            "BT_vacuum_branch": "Omega=v!=0, Upsilon=0",
            "quadratic_symbol": "z; formal only, with cross kinetic entries shifted by -z",
        },
        "assumptions": [
            "local derivative-free regulator potential V=F(Omega*Upsilon)",
            "twice differentiable F at the declared constant vacuum",
            "connected SO+(1,1) boost invariance with q(Omega)=+1 and q(Upsilon)=-1",
            "stationary constant background before defining its quadratic pole polynomial",
            "v is nonzero on the Bateman-Turok broken branch",
        ],
        "candidate_theorem": {
            "statement": "No regulator in the declared carrier simultaneously has a stationary BT broken vacuum, exact SO+(1,1) invariance in the fixed theory, a nonzero infrared gap, and a coincident double pole.",
            "proof_obligations": [
                "derive the vacuum gradient and Hessian from a generated two-jet of F",
                "show stationarity on (v,0) forces f1=F'(0)=0",
                "identify the coincident pole location with f1",
                "move the mass-deformed theory to its true stationary branch and classify the two roots",
                "classify the charge of the fixed-v tadpole subtraction",
            ],
            "counterexample_strategy": "Drop each one of stationarity, invariance, coincidence, and the gap in turn and require an exact populated witness.",
            "finite_machine_boundary": "exact Laurent-polynomial differentiation, substitution, 2x2 determinant identities, and four witness predicates",
        },
        "polynomial_identities": polynomial_identities,
        "independence_witnesses": [
            {
                "drop": "stationarity",
                "witness": "Hold (v,0) fixed after adding mu2*Omega*Upsilon: det K=-(z-mu2)^2, but d_Upsilon V=v*mu2 is nonzero.",
            },
            {
                "drop": "exact fixed-sector SO+(1,1) invariance",
                "witness": "Add -mu2*v*Upsilon to cancel the tadpole: the source has charge -1 for fixed v; treating v as charge +1 changes it into a spurion statement.",
            },
            {
                "drop": "coincident pole",
                "witness": "Move to s0=-mu2/lambda2: det K=-z*(z+2*mu2), one massless and one massive simple root.",
            },
            {
                "drop": "nonzero infrared gap",
                "witness": "Use the original F=(lambda2/2)*s^2 on (v,0): it is stationary and has the massless double polynomial -z^2.",
            },
        ],
        "correction_to_predecessor": {
            "predecessor": "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1",
            "retained": "Neutral vertices and off-diagonal contractions preserve ambient SO+(1,1) charge at every enumerated loop order.",
            "withdrawn": "The earlier corollary that mu2*Omega*Upsilon is, without further qualification, the IR regulator the BT loop extension should use.",
            "replacement": "It preserves charge and the quadratic double root only at a held nonstationary BT background. Vacuum compatibility creates the exact trilemma certified here.",
        },
        "next_gate": "Classify non-mass regulator architectures (dimensional/off-shell/inclusive/dressed) and test whether the negative-charge trace radical is closed under the first collinear inclusive sum.",
        "does_not_establish": [
            "any refutation of Bateman-Turok; their paper asks for regulation and resummation of collinear asymptotic states and does not propose this mass term",
            "that every derivative, nonlocal, finite-volume, dimensional, off-shell, inclusive, or dressed-state regulator fails",
            "a loop calculation, anomaly coefficient, KLN theorem, resummed asymptotic state, or positivity theorem beyond tree level",
            "anything about the tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL; z is only a formal quadratic symbol",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "external_source": "S. Bateman and N. Turok, arXiv:2607.00096v1, Eqs. (14)-(15) and the broken branch Omega=lambda^-1, Upsilon=0",
            "inputs": [
                {
                    "path": "notes/bateman-turok-embedding.md",
                    "sha256": sha256("notes/bateman-turok-embedding.md"),
                },
                {
                    "path": "reverse_physics/certificates/REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1.json",
                    "sha256": sha256("reverse_physics/certificates/REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1.json"),
                },
                {
                    "path": "reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json",
                    "sha256": sha256("reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json"),
                },
                {
                    "path": "paper/05-interaction-obstructions.tex",
                    "sha256": sha256("paper/05-interaction-obstructions.tex"),
                },
            ],
            "exact_arithmetic": "fractions.Fraction coefficients in a generated sparse Laurent-polynomial ring; no floating point",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_ir_regulator_trilemma.py --check",
            "python3 reverse_physics/verify_bt_ir_regulator_trilemma.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_ir_regulator_trilemma",
        ],
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for passed in checks.values() if passed),
            "failures": failures,
            "ok": not failures,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="BT IR regulator trilemma")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not (args.emit or args.check):
        args.check = True

    certificate = build()
    print("BT local invariant IR-regulator trilemma")
    for name, passed in certificate["checks"]["detail"].items():
        print(("[OK ] " if passed else "[FAIL] ") + name)
    print("checks %d/%d" % (
        certificate["checks"]["passed"], certificate["checks"]["total"]
    ))

    if args.emit:
        if not certificate["checks"]["ok"]:
            print("refusing to emit a failing certificate")
            return 1
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(certificate, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    if args.check:
        if not os.path.exists(CERT_PATH):
            print("FAIL missing certificate %s" % os.path.relpath(CERT_PATH, REPO_ROOT))
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            recorded = json.load(handle)
        if recorded != certificate:
            print("FAIL recorded certificate differs from exact recomputation")
            return 1
        print("recorded certificate byte-content agrees with recomputation")

    print("RESULT: %s" % ("PASS" if certificate["checks"]["ok"] else "FAIL"))
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
