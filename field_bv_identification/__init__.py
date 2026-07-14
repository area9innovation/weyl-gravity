"""Field-theoretic identification of the certified pure-Weyl BV bridge.

The package deliberately starts from the metric BV variables, rather than
from the already reduced Weyl module.  Its first milestone is the exact
comparison between the tangent complex of the quadratic minimal master
action and the raw polynomial detour chain used by the residual calculation.
"""

from .minimal_master_action import MinimalBVBlock, MinimalBVVariable
from .raw_chain_comparison import MinimalRawComparison

__all__ = ["MinimalBVBlock", "MinimalBVVariable", "MinimalRawComparison"]
