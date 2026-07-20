# Candidate-16 active restricted current

Candidate 16 is the unique active same-sign collision whose resonant inputs
are both `q_minus` nodes.  Their complete axial/polar Lee--Wald current blocks
are negative definite.  After fixing both nonzero norms and quotienting the
two node phases, the ambient carrier is `CP^9 x CP^9` with a negative weighted
sum of Fubini--Study forms.

The cross-fibre resonance equations define one irreducible affine complex
variety of dimension 12, equivalently a projective complex tenfold after the
two node scalings.  On every complex smooth stratum, every nonzero tangent
vector has strictly negative Hermitian current norm.  Hence the restricted
Lee--Wald form is nondegenerate there.  Resonance cannot create a current
radical in this same-sign case.

This closes the restricted-current gate for candidate 16 only.  The variety
is singular, so the ordinary smooth-orbifold connected-fibre theorem is not
silently applied.  Its singular Hamiltonian stratification and rotation-zero
fibre remain open, as do the indefinite restricted currents on candidates
17--21.

## Verification

The exact producer, independent verifier and three focused unit tests pass.
The regenerated fail-closed Einstein atlas passes its independent verifier
and all 97 focused tests.  Paper 13 compiles in three clean `pdflatex` passes
to 25 pages with no warnings or box errors.
