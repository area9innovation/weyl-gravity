"""Exact inputs and fail-closed certification for the curved witness.

The modules in this package deliberately distinguish three levels:

* the exact nonlinear covariant action and its linearized gauge map;
* the exact normal-form algebra of covariant derivatives on the cylinder;
* the still-incomplete expanded Hessian/witness jet calculation.

The first two levels are executable theorems.  They do not by themselves
promote ``curved_operator_identity``.
"""

from .covariant_action import CovariantAuxiliaryAction
from .derivative_normal_form import ParallelCylinderNormalForm
from .globalization_lemma import CurvedOperatorGlobalization
from .status import CurvedOperatorIdentityStatus

__all__ = [
    "CovariantAuxiliaryAction",
    "ParallelCylinderNormalForm",
    "CurvedOperatorGlobalization",
    "CurvedOperatorIdentityStatus",
]
