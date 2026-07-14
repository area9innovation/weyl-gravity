"""Exact level-by-level match between reduced fields and E/A/L modules."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.metric_preimages.all_energy import BRANCH_MINIMUM, block_dimension


N = sp.symbols("N", integer=True, positive=True)
R = sp.symbols("r", integer=True, nonnegative=True)


@dataclass(frozen=True)
class EALFieldDictionary:
    def verify(self, maximum_regression_energy: int = 12) -> None:
        if BRANCH_MINIMUM != {"E": 2, "A": 3, "L": 4}:
            raise AssertionError("the certified E/A/L low-energy exceptions changed")

        tt_multiplicity = 2 * (R + 1) * (R + 5)
        vector_multiplicity = 2 * (R + 1) * (R + 3)
        identities = {
            "E": sp.expand(
                tt_multiplicity.subs(R, N - 2) - 2 * block_dimension("E", N)
            ),
            "A": sp.expand(
                vector_multiplicity.subs(R, N - 2)
                - 2 * block_dimension("A", N)
            ),
            "L": sp.expand(
                tt_multiplicity.subs(R, N - 4) - 2 * block_dimension("L", N)
            ),
        }
        if any(value != 0 for value in identities.values()):
            raise AssertionError(f"all-energy E/A/L multiplicity mismatch: {identities}")

        for energy in range(2, maximum_regression_energy + 1):
            expected = {
                family: int(2 * block_dimension(family, energy))
                for family, minimum in BRANCH_MINIMUM.items()
                if energy >= minimum
            }
            field = {"E": 2 * (energy - 1) * (energy + 3)}
            if energy >= 3:
                field["A"] = 2 * (energy - 1) * (energy + 1)
            if energy >= 4:
                field["L"] = 2 * (energy - 3) * (energy + 1)
            if field != expected:
                raise AssertionError(f"field/module dictionary failed at N={energy}")

        # r=0 transverse vectors are Killing fields.  They have |C_1|=2,
        # but their symmetrized gradient vanishes, so no A_2 metric mode exists.
        if int(2 * block_dimension("A", 2)) != 6:
            raise AssertionError("unexpected formal A_2 continuation")
        if 2 >= BRANCH_MINIMUM["A"]:
            raise AssertionError("the Killing-vector band was included as A_2")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-eal-field-dictionary-v1",
            "parity_complete": True,
            "branches": {
                "E": {
                    "field_origin": "lower-frequency TT Bach branch",
                    "harmonic_label": "r=N-2>=0",
                    "frequency": "N=r+2",
                    "multiplicity": "2(r+1)(r+5)=2(N-1)(N+3)",
                    "minimum_energy": 2,
                },
                "A": {
                    "field_origin": "transverse-vector metric branch",
                    "harmonic_label": "r=N-2>=1",
                    "frequency": "N=r+2",
                    "multiplicity": "2(r+1)(r+3)=2(N-1)(N+1)",
                    "minimum_energy": 3,
                },
                "L": {
                    "field_origin": "upper-frequency TT Bach branch",
                    "harmonic_label": "r=N-4>=0",
                    "frequency": "N=r+4",
                    "multiplicity": "2(r+1)(r+5)=2(N-3)(N+1)",
                    "minimum_energy": 4,
                },
            },
            "important_correction": (
                "|C_1| has an N=2 Killing band on all transverse vectors, "
                "but the metric A tower starts at N=3 because symgrad(Killing)=0"
            ),
            "all_energy_symbolic": True,
            "not_character_only": True,
        }
