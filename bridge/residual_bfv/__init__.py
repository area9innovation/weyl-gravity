"""Residual ``SO(4,2)`` BFV algebra, ghosts, and canonical pairing."""

from .conformal_ce import ConformalCE, ExteriorPolynomial, Monomial
from .coefficient_complex import (
    CoefficientCEComplex,
    CoefficientModule,
    columns_to_matrix,
    compose,
    modular_rank,
)

__all__ = [
    "CoefficientCEComplex",
    "CoefficientModule",
    "ConformalCE",
    "ExteriorPolynomial",
    "Monomial",
    "columns_to_matrix",
    "compose",
    "modular_rank",
]
