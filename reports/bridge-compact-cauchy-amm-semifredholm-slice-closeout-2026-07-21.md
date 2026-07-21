# Compact-Cauchy AMM semi-Fredholm slice closeout

## Split verdict

The compact right-semi-Fredholm data do prove a full-Sobolev second-order
Cauchy tangent-cone theorem:

\[
\mathcal Z_2
=\{u\in\ker D\mathcal C_{\bar z}:\
\mu_H(u)=\mu_{P_x}(u)=\mu_{J_1}(u)=\mu_{J_2}(u)=\mu_{J_3}(u)=0\}.
\]

They do not, on the unextended canonical phase space, satisfy the fixed-group
momentum-map hypothesis needed to invoke the 1981 Arms--Marsden--Moncrief
homogeneous-quadratic normal-form theorem directly.

## Positive theorem: semi-Fredholm Kuranishi reduction

On the imported weighted Sobolev spaces, the nonlinear canonical constraint
map is smooth.  Its derivative has closed range and finite-dimensional
cokernel, and the latter is exactly the five-dimensional lifted stabilizer
space.  Hilbert orthogonal complements therefore give

\[
X=\ker D\mathcal C\oplus(\ker D\mathcal C)^\perp,
\qquad
Y=\operatorname{ran}D\mathcal C\oplus\ker(D\mathcal C)^*.
\]

The restriction from \((\ker D\mathcal C)^\perp\) to the range is a bounded
isomorphism.  The Banach implicit-function theorem solves the range equation
and leaves a five-component Kuranishi obstruction \(\kappa\).  Its Hessian is
the adjoint projection of the quadratic constraint source.  Consequently a
second-order Cauchy correction exists if and only if the five Taub pairings
vanish.  This is necessity and sufficiency for the declared Cauchy correction
class, not merely necessity.

The sixteen physical principal-symbol directions remain in the kernel.  None
is turned into a gauge condition.

## Exact separator: why direct fixed-group AMM fails

The full normal-deformation constraints obey the hypersurface-deformation
bracket

\[
\{H[N],H[M]\}=H_i\!\left[h^{ij}
(N\partial_jM-M\partial_jN)\right]+\cdots .
\]

The inverse metric is a phase-space-dependent structure function.  On the
circle, take \(N=\sin x\) and \(M=\cos x\).  Their Wronskian is exactly \(-1\).
For \(h_{xx}=1\) the resulting shift coefficient is \(-1\); for \(h_{xx}=4\)
it is \(-1/4\).  Therefore no fixed Lie bracket on lapse functions generates
the normal-deformation algebra on a neighborhood of the unextended canonical
phase space.

This is precisely the hypothesis boundary emphasized in the original AMM
analysis: the spatial momentum constraint is a momentum map for spatial
diffeomorphisms, whereas the Hamiltonian constraint requires additional
treatment.  The later Einstein/Einstein--Yang--Mills theorem cannot simply be
imported into fourth-order Weyl--Maxwell theory without proving its analog.

The spatial `Diff(Sigma) x Weyl x based-U(1)` subgroup does admit the expected
Sobolev slice: on the stabilizer-orthogonal complement the elliptic orbit
operator gives an invertible \(A^*A\).  The obstruction concerns the full
seven-constraint fixed-group claim, especially normal deformations.

Primary sources used for positioning:

- Arms, Marsden and Moncrief, *Symmetry and bifurcations of momentum
  mappings*, Commun. Math. Phys. 78 (1981) 455--478.
- Arms, Marsden and Moncrief, *The structure of the space of solutions of
  Einstein's equations II*, Ann. Phys. 144 (1982) 81--106.

## Crosswalk to the finite carrier

Restriction of the five Sobolev adjoint pairings agrees with the imported
finite-harmonic Taub maps.  The finite exponential-polynomial theorem also has
carrier-dependent resonance functionals.  These are not additional
compact-Cauchy adjoint covectors.  Conversely, Cauchy solvability does not imply
bounded quasiperiodic or causal spacetime solvability.

## Repair choices

Any stronger exact homogeneous-quadratic nonlinear normal form must use one of:

1. embedding variables on which spacetime diffeomorphisms act as a fixed group;
2. a proved Lie-algebroid/groupoid slice and Kuranishi theorem; or
3. a Weyl--Maxwell-specific extension of the 1982 several-Killing-field proof.

## Evidence and tests

- `bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json`
- `bridge/einstein_sector/einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice.py`
- `bridge/einstein_sector/verify_einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice.py`
- `residual_atlas/einstein-weyl-compact-cauchy-amm-semifredholm-slice-fragment-v1.json`

The independent verifier reconstructs the metric-dependent bracket witness and
checks that the positive second-order theorem and negative fixed-group claim
cannot be conflated.  Ten scoped tests and the strict atlas validator pass.

CLOSE-OUT: OBSTRUCTED — the exact no-go or first obstruction is certified
EVIDENCE: bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json
