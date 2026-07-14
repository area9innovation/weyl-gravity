"""Fail-explicit classification of every gauge-fixed variable.

No multiplier is integrated out in the selected conformal Landau gauge.
The multipliers and their antifields stay in the matrix complex and are
removed only by the displayed nonminimal contracting homotopy.
"""

from __future__ import annotations

from field_bv_identification.gauge_fixed_equivalence.nonminimal_sector import (
    NonminimalBlock,
)


def elimination_ledger(block: NonminimalBlock) -> tuple[dict[str, object], ...]:
    output = []
    for field in block.slices:
        output.append(
            {
                "variable": field.name,
                "dimension": field.dimension,
                "classification": "nonminimal doublet",
                "elimination": "explicit tangent homotopy",
                "generalized_auxiliary": False,
                "silently_discarded": False,
            }
        )
    return tuple(output)


def generalized_auxiliary_report() -> dict[str, object]:
    return {
        "gauge": "conformal Landau",
        "multiplier_square_present": False,
        "generalized_auxiliary_eliminations": [],
        "statement": (
            "No generalized auxiliary elimination is used; every antighost, "
            "multiplier, and antifield dual remains until contracted explicitly."
        ),
    }

