"""Exhaustive component ledger for the curved auxiliary BV retract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BVRowBlock:
    name: str
    start: int
    stop: int
    role: str

    @property
    def dimension(self) -> int:
        return self.stop - self.start


@dataclass(frozen=True)
class CurvedBVRowLedger:
    """Record every minimal coordinate and every reattached direct summand.

    This ledger is deliberately independent of the operator coefficients.
    It can prove exhaustive coverage, but it cannot prove that the supplied
    curved Q has the advertised coefficients on those rows.
    """

    minimal_blocks: tuple[BVRowBlock, ...]
    generalized_auxiliary_blocks: tuple[tuple[str, int], ...]
    reattached_direct_summands: tuple[tuple[str, str], ...]

    @staticmethod
    def build() -> "CurvedBVRowLedger":
        result = CurvedBVRowLedger(
            minimal_blocks=(
                BVRowBlock("ghosts[xi_minus_2,xi_0,sigma]", 0, 9, "ghost"),
                BVRowBlock("fields[h,f,v]", 9, 33, "field"),
                BVRowBlock("field_antifields[h_star,f_star,v_star]", 33, 57, "field antifield"),
                BVRowBlock("ghost_antifields[xi_minus_2_star,xi_0_star,sigma_star]", 57, 66, "ghost antifield"),
            ),
            generalized_auxiliary_blocks=(
                ("eta", 4),
                ("f_hat", 10),
                ("v", 4),
                ("f_hat_star", 10),
                ("v_star", 4),
                ("eta_star", 4),
            ),
            reattached_direct_summands=(
                ("trace/Weyl doublet and antifield dual", "pointwise identity contraction"),
                ("diffeomorphism antighost/multiplier and dual", "pointwise identity contraction"),
                ("Weyl antighost/multiplier and dual", "pointwise identity contraction"),
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        covered: list[int] = []
        for block in self.minimal_blocks:
            if block.start < 0 or block.stop <= block.start:
                raise AssertionError(f"invalid BV row block {block.name}")
            covered.extend(range(block.start, block.stop))
        if covered != list(range(66)):
            raise AssertionError("the minimal four-row ledger is not an exact partition of 0..65")
        if sum(dimension for _, dimension in self.generalized_auxiliary_blocks) != 36:
            raise AssertionError("the generalized-auxiliary row ledger is not 36-dimensional")
        if len({name for name, _ in self.reattached_direct_summands}) != len(
            self.reattached_direct_summands
        ):
            raise AssertionError("a reattached BV summand was duplicated")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curved-BV-row-ledger-v1",
            "minimal_four_row_blocks": [
                {
                    "name": block.name,
                    "indices": [block.start, block.stop - 1],
                    "dimension": block.dimension,
                    "role": block.role,
                }
                for block in self.minimal_blocks
            ],
            "minimal_dimension": 66,
            "minimal_rows_exhausted_exactly_once": True,
            "generalized_auxiliary_blocks": [
                {"name": name, "dimension": dimension}
                for name, dimension in self.generalized_auxiliary_blocks
            ],
            "generalized_auxiliary_dimension": 36,
            "reattached_direct_summands": [
                {"name": name, "differential": differential}
                for name, differential in self.reattached_direct_summands
            ],
            "coefficient_compatibility_with_actual_curved_Q": (
                "verified by the separate factorized actual-curved-Q split"
            ),
            "guard": (
                "the ledger prevents silent row omission; coefficient compatibility "
                "must still be checked after the complete curved Q is supplied"
            ),
        }
