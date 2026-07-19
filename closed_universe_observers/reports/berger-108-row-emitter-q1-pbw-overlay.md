# Berger 108-row emitter q1 PBW overlay

Status: `CERTIFIED_SCALAR_EMITTER_Q1_PBW_OVERLAY`.

All six covariant massive-emitter unary ranges are now scalar sparse PBW
blocks. The calculation derives support-local exterior derivative matrices in
the exact noncommuting Berger frame and derives the Lorentzian coderivative by
formal adjunction. Both `d^2` and `delta^2` vanish coefficientwise. The six
blocks occupy 132 distinct matrix positions and contain 204 serialized PBW
terms on rows 59--62 and 96--107 from columns 55--58 and 84--95.

For each emitter the covariant Euler equations contain `-g_b h_b d`,
`-g_b delta(h_b ·)`, and `delta d+m_b^2`.  The scalar overlay now explicitly
Hamiltonian-raises these form-valued equations into the frozen density-valued
BV cotangent rows: `+eta_1` acts on Maxwell-antifield equations and `-eta_2`
on emitter-antifield equations.  This convention bridge was forced by the
complete replay; omitting it produces exactly 24 zeroth-order square terms
and 102 cyclicity terms.  With it, both counts vanish.  The coderivative
product rule keeps every first Berger-frame jet of the exact switch, so the
coexact Maxwell Noether path is not hidden in a covariant formula.

The pinned 64-row q1 remains unchanged. This result is only the emitter
overlay.  The complete first-jet replay is recorded separately: it is cyclic
in all bidegrees but obstructed at the `epsilon_R_squared` nilpotency
coefficient.  Scalar q2, backreaction, tangent-cone, Bridge 3 and quantum
gates therefore remain unavailable.
