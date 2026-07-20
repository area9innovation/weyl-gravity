# Candidate-17/20 axisymmetric restricted currents

Candidates 17 and 20 share the irreducible product of two
third-transvectant kernels as their active resonance variety.  Their certified
all-axial `m=0` section lies on the square-quartic rank-drop stratum: the
resonance derivative has rank four, so the affine Zariski tangent has complex
dimension 16 although the variety has dimension 14.

That algebraic singularity is not a Lee--Wald degeneracy.  Exact rational
intervals prove on both active extreme rays of each candidate that the
negative `q_minus` occupation exceeds the positive `q_plus` occupation.
Inactive rays add only to the negative occupation, so the inequality holds
throughout the nonzero active scalar cone.

Each parity channel has three unconstrained positive/negative angular pairs
and two constrained negative directions, giving inertia `(3,5,0)`.  The two
parities therefore give affine Zariski-tangent inertia `(6,10,0)`.  Removing
the positive and negative node scalings yields projective inertia `(5,9,0)`
and real symplectic rank 28.

This is a complete active-cone result on the axisymmetric sections only.  It
does not make those singular points smooth or classify the full smooth locus,
the lifted-rotation zero fibre, candidate 18, occupation gluing, or any higher
lifecycle.

## Verification

The deterministic producer, a separately implemented verifier, and three
focused unit tests pass.  The verifier reconstructs the third-transvectant
rank, the exact ray weights, and their rational isolating intervals rather
than importing the producer's conclusions.  The fail-closed atlas generator
and verifier pass with 99 focused atlas tests.  Paper 13 builds cleanly in
three `pdflatex` passes (26 pages), with no undefined references, warnings, or
box errors.
