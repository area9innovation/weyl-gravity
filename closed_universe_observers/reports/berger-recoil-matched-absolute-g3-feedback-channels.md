# Berger detector-matched absolute-g3 feedback channels

Status: `TWO_FINITE_MATCHED_ABSOLUTE_G3_CHANNEL_BLOCKS_EVALUATED_ZERO_CONTAINING`.

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The first two physical feedback contractions are now executable.  For the
detector-matched self channels, Green adjunction reduces the complete outer
Maxwell and massive propagation to

\[
 I_{aaa}=\langle V_a^{\rm adv},h_a dA_a^{\rm lead,ret}\rangle,
 \qquad a=0,1.
\]

The advanced field uses the physical massive Green operator

\[
G_{E_a,\mathrm{adv}}
=G_{P_2+m_a^2,\mathrm{adv}}
+m_a^{-2}dG_{P_1+m_a^2,\mathrm{adv}}\delta.
\]

This required adding the previously absent massive scalar block to the exact
finite kernel payload, completing the massive one-form carrier.  The final
pairing uses the Lorentzian sign
`-<alpha,alpha_prime>+<beta,beta_prime>`.

The certificate evaluates `I_000[0,0]` and `I_111[0,0]` on the validation
domain `m_a^2 in [1,2]`.  Both intervals contain zero because the present
feedback rail deliberately retains whole-support switch and switch-derivative
hulls.  They therefore certify executable channel evaluation, not a nonzero
or sign result.

The values are coupling-stripped coefficient blocks.  The factors `g_0^3`,
`g_1^3` and `(two_j+1)/Vol_Berger` have not been applied.  Physical masses,
the six mismatched `(a,b,c)` channels, higher shells, tail stopping, the four
aggregate recoil scalars, recoil-corrected rank, tangent-cone restriction,
Bridge 3, full apparatus gauge descent and quantum claims remain open.
