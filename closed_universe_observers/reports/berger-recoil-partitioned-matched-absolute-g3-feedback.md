# Berger partition-refined matched absolute-g3 feedback

Status: `MATCHED_FEEDBACK_INTERVALS_STRICTLY_NARROWED_ZERO_CONTAINMENT_PERSISTS`.

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The whole-support matched-channel calculation loses dependency information at
four distinct switch occurrences: the advanced massive source, its physical
one-form correction, the leading emitter current, and the final feedback
pairing.  The partitioned successor propagates all four on a common causal
cell decomposition.

For each output cell, causally earlier or later full source cells use their
exact integration length.  The single diagonal Volterra triangle is enclosed
with a length in `[0,cell_width]`.  This is rigorous and its over-enclosure
contracts as the cells narrow.

On the validation domain `m_0^2,m_1^2 in [1,2]`, the real and imaginary
interval widths of both `I_000[0,0]` and `I_111[0,0]` strictly decrease along
the `2 -> 4 -> 8` partition rail.  The 8-cell widths are also strictly below
the original whole-support widths.  Both refined complex rectangles still
contain zero, so the calculation does not certify a sign, nonzero feedback
coefficient, or recoil-corrected response rank.

The next gate is to evaluate the six mismatched `(a,b,c)` channels with this
partitioned causal backend.  Further time/mass refinement, physical masses,
higher shells, tail aggregation, the four recoil scalars, tangent-cone
restriction, Bridge 3, full apparatus quotient and quantum claims remain
open.
