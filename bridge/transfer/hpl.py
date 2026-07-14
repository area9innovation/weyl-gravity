"""Finite local-to-residual HPL corrections in raw metric-BV rows."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.cyclic_retract import RawPolynomialRetraction
from bridge.residual_bfv import ConformalCE


def generator_grade(name: str) -> int:
    if name.startswith("K-_"):
        return -1
    if name.startswith("K+_"):
        return 1
    return 0


def raw_generator_map(
    source: RawPolynomialRetraction,
    target: RawPolynomialRetraction,
    name: str,
) -> sp.Matrix:
    """Return one residual chain map in the residual-BFV convention."""

    grade = generator_grade(name)
    if target.block.energy != source.block.energy + grade:
        raise ValueError("generator target has the wrong compact energy")
    if name == "D":
        return sp.Matrix(source.block.dilation)
    if name.startswith("R") and len(name) == 3:
        return sp.Matrix(source.block.rotation(int(name[1]), int(name[2])))
    if name.startswith("K-_"):
        return sp.Matrix(
            source.block.translation_to(target.block, int(name.split("_")[1]))
        )
    if name.startswith("K+_"):
        # RawResidualModule uses minus coordinate-special so that its
        # structure constants agree with ConformalCE.
        return -sp.Matrix(
            source.block.special_to(target.block, int(name.split("_")[1]))
        )
    raise ValueError(f"unknown residual generator {name}")


@dataclass(frozen=True)
class HPLCorrectionReport:
    retracts: dict[int, RawPolynomialRetraction]
    tested_sources: tuple[int, ...]
    tested_ordered_pairs: int
    nonzero_second_corrections: tuple[tuple[int, str, str], ...]
    nonzero_third_stems: tuple[tuple[int, str, str], ...]

    @classmethod
    def build(cls) -> "HPLCorrectionReport":
        retracts = {
            energy: RawPolynomialRetraction.build(energy)
            for energy in range(2, 6)
        }
        names = ConformalCE.build().names
        # Energy four is the centered top shell.  Paths which stay in, or
        # return to, the available coefficient buffer are checked directly.
        # The only omitted path is double raising 4 -> 5 -> 6; its two
        # negative-degree raising ghosts wedge to zero on the already
        # saturated four-ghost energy-four cochains.
        tested_sources = (2, 3, 4)
        tested = 0
        nonzero_second = []
        nonzero_third = []
        for source_energy in tested_sources:
            source = retracts[source_energy]
            for first in names:
                middle_energy = source_energy + generator_grade(first)
                if middle_energy not in retracts:
                    continue
                middle = retracts[middle_energy]
                rho_first = raw_generator_map(source, middle, first)
                first_stem = middle.homotopy * rho_first * source.inclusion
                for second in names:
                    target_energy = middle_energy + generator_grade(second)
                    if target_energy not in retracts:
                        continue
                    target = retracts[target_energy]
                    rho_second = raw_generator_map(middle, target, second)
                    tested += 1
                    correction = (
                        target.projection
                        * rho_second
                        * middle.homotopy
                        * rho_first
                        * source.inclusion
                    )
                    if correction != sp.zeros(
                        target.cohomology_dimension,
                        source.cohomology_dimension,
                    ):
                        nonzero_second.append((source_energy, first, second))

                    # A third HPL term would contain s rho s rho j.  Its
                    # vanishing is stronger than merely projecting it away.
                    third_stem = target.homotopy * rho_second * first_stem
                    if third_stem != sp.zeros(
                        target.block.dimension,
                        source.cohomology_dimension,
                    ):
                        nonzero_third.append((source_energy, first, second))
        result = cls(
            retracts,
            tested_sources,
            tested,
            tuple(nonzero_second),
            tuple(nonzero_third),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.nonzero_second_corrections:
            raise AssertionError(
                f"nonzero p Delta s Delta j terms: {self.nonzero_second_corrections}"
            )
        if self.nonzero_third_stems:
            raise AssertionError(
                f"nonzero s Delta s Delta j stems: {self.nonzero_third_stems}"
            )
        if self.tested_ordered_pairs <= 0:
            raise AssertionError("no residual-generator pairs were tested")
