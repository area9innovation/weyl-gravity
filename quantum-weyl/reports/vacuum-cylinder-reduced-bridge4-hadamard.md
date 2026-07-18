# Vacuum-cylinder reduced Bridge 4 Hadamard/Krein carrier

## Result

Bridge 4 is now certified on the free, reduced physical E/A/L carrier of the
unit vacuum conformal cylinder.  The three activation inputs live on the same
background:

- normalized all-energy E/A/L classical modes;
- advanced/retarded Green blocks for the reduced physical system;
- the transported Green/Cauchy-current pairing with signs (+E,-A,-L).

This does not certify Bridge 4 on Berger space or on the full off-shell BV
distributional complex.

## Complex structure

For branch frequency (N), positive residue (R_\alpha(N)), and Cauchy data
((q,p)), the compatible complex structure is

\[
J_N(q,p)=(-N^{-1}p,Nq).
\]

With

\[
\Omega_\alpha=s_\alpha R_\alpha
\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\qquad
(s_E,s_A,s_L)=(1,-1,-1),
\]

the exact identities are

\[
J_N^2=-1,
\qquad
J_N^T\Omega_\alpha J_N=\Omega_\alpha,
\qquad
\Omega_\alpha J_N
=s_\alpha R_\alpha\operatorname{diag}(N,N^{-1}).
\]

The normalized positive-frequency mode

\[
v_{\alpha,N}
=\frac{(1,-iN)}{\sqrt{2R_\alpha(N)N}}
\]

satisfies (i\Omega_\alpha(\bar v,v)=s_\alpha).

## Two-point distributions

For each normalized harmonic (u_{\alpha NM\chi}), the stationary kernel is

\[
W_\alpha^+(x,x')
=\sum_{N,M,\chi}
\frac{s_\alpha e^{-iN(t-t'-i0)}}{2R_\alpha(N)N}
u_{\alpha NM\chi}(x)
\overline{u_{\alpha NM\chi}(x')}.
\]

The branch data are

| branch | (N_{\min}) | (R_\alpha(N)) | sign |
|---|---:|---:|---:|
| E | 2 | (4(N+1)) | (+1) |
| A | 3 | (2(N^2-4)) | (-1) |
| L | 4 | (4(N-1)) | (-1) |

Every mode is an exact bisolution and obeys

\[
W_\alpha^+-(W_\alpha^+)^{\sharp,\mathrm{swap}}
=i\Delta_\alpha.
\]

Quadratic harmonic multiplicity and rapid decay of smooth test-function
coefficients give a global distribution on the compact cylinder.  The
ultrastatic positive-frequency pseudodifferential construction has the
standard (C^+) wavefront relation.  Applying a finite-order elliptic residue
inverse, or multiplying by a nonzero Krein sign, preserves that relation.

## State-space disposition

- E is a positive quasifree Hadamard sector.
- A and L are negative-Krein Hadamard distributions, not positive states.
- Their direct sum is an infinite-index Krein quasifree functional.

Thus the result is a reduced free quantum carrier, not a positive graviton
Hilbert space, scattering theory, or interacting quantum theory.

## Fail-closed boundary

Still open:

- ghost and antifield covariances on the full distributional BV complex;
- a full BRST-compatible Hadamard state;
- the Berger stationary-mode crosswalk;
- renormalized Lorentzian time-ordered products;
- interacting-QME and residual-transfer consequences.

The strict fixed-field-content one-loop QME obstruction remains unchanged.

## Receipts

- Producer: `quantum-weyl/lorentzian/vacuum_cylinder_reduced_bridge4_hadamard.py`
- Certificate: `quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json`
- Schema: `quantum-weyl/lorentzian/schema/vacuum-cylinder-reduced-bridge4-hadamard-v1.schema.json`
- Independent replay: `quantum-weyl/lorentzian/verify_vacuum_cylinder_reduced_bridge4_hadamard.py`
- Tests: `quantum-weyl/lorentzian/tests/test_vacuum_cylinder_reduced_bridge4_hadamard.py`

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.
