"""Exact inputs and fail-closed certification for the curved witness.

The modules in this package deliberately distinguish three levels:

* the exact nonlinear covariant action and its linearized gauge map;
* the exact normal-form algebra of covariant derivatives on the cylinder;
* the action-factorized Hessian and exact four-row witness algebra;
* the expanded Hessian, global operator identities, and separate wave no-go.

The exact operator identity is promoted independently of scalar-wave Green
realizability.  Mixed-order and curvature-prolonged Green realizations remain
separate fail-closed flags.
"""

from .action_hessian import ActionDerivedAuxiliaryHessian
from .covariant_action import CovariantAuxiliaryAction
from .conventions import CurvedBVConventions, FirstOrderOperator
from .curvature_evolution import CurvatureEvolutionPrincipalSymbol
from .curvature_prolongation_status import CurvatureProlongationStatus
from .covariant_jets import CovariantJetBasis
from .derivative_normal_form import ParallelCylinderNormalForm
from .eliminated_density import EliminatedVectorDensityIdentity
from .globalization_lemma import CurvedOperatorGlobalization
from .four_row_kernel import CurvedFourRowKernel
from .invariant_pairings import InvariantFibrePairingAnsatz
from .null_symbol_rank_obstruction import NullSymbolRankObstruction
from .null_symbol_quotient import CurvedNullSymbolQuotient
from .status import CurvedOperatorIdentityStatus

__all__ = [
    "ActionDerivedAuxiliaryHessian",
    "CovariantAuxiliaryAction",
    "CurvedBVConventions",
    "CurvatureEvolutionPrincipalSymbol",
    "CurvatureProlongationStatus",
    "CovariantJetBasis",
    "FirstOrderOperator",
    "ParallelCylinderNormalForm",
    "EliminatedVectorDensityIdentity",
    "CurvedOperatorGlobalization",
    "CurvedFourRowKernel",
    "InvariantFibrePairingAnsatz",
    "NullSymbolRankObstruction",
    "CurvedNullSymbolQuotient",
    "CurvedOperatorIdentityStatus",
]
