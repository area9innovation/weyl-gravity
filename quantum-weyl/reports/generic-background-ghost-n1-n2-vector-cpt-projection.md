# Generic-background ghost vector \(n_1+n_2\) CPT projection

## Result

On the four-dimensional Euclidean scalar-flat source complement, the two
pure-vector Hodge carriers combine into the exact CPT-IV kernel

\[
  6\Gamma_1\mathcal S_1
  -2\Gamma_3\mathcal S_3
  -2\Gamma_{14}\mathcal S_{14}.
\]

The source is the pinned CPT-IV ancillary file `anc/ffwa.m` from arXiv
0911.1168.  Its archive and ancillary hashes are recorded in the certificate.
The result follows from the sign flip between the minimal vector potentials
\(P_F=-\mathrm{Ric}\) and \(P_H=+\mathrm{Ric}\): even-\(P\) rows cancel,
single-\(P\) scalar traces vanish when \(R=0\), and only rows 1, 3 and 14
survive.  The overall determinant sign is calibrated against the independently
certified zero-longitudinal \(n_3\) sector.

The two nontrivial source tensors were projected to the ordered
\(I_{10},I_{24},I_{25},I_{28},I_{29}\) quotient.  Ten training fixtures,
125 exact transverse-traceless tensor products per fixture and two source
structures give 2,500 exact projection identities.  Another 750 identities
check the linearized Riemann/Ricci contraction and contracted Bianchi
conventions.  An independent verifier uses two unseen momentum fixtures and
detects a deliberate coordinate mutation.

## Minimal missing-carrier theorem

This does **not** evaluate all five Hodge-resolvent carriers.  The remaining
three are

```text
N1_LONGITUDINAL_SCALAR
N2_VECTOR_LONGITUDINAL
N2_LONGITUDINAL_LONGITUDINAL
```

and each contains

\[
  D_W=\delta Wd,
  \qquad
  \sigma_2(D_W)(p)=W^{\mu\nu}p_\mu p_\nu.
\]

This is a curvature-dependent anisotropic principal-symbol insertion, not a
minimal bundle endomorphism \(P\).  The mixed row also couples scalar and
vector resolvents.  Therefore the imported minimal-Laplace CPT \(P\)-sector
kernels cannot evaluate those carriers.  The smallest additional input is a
covariant scalar/vector kernel with one and two \(D_W\) insertions through the
required curvature order, or an equivalent direct nonminimal Endo
form-factor calculation.

## Claim boundary

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The certificate supplies the combined pure-vector \(n_1+n_2\) contribution
only.  It does not supply the complete generic ghost determinant, the physical
fourth-order Hessian kernel, the complete renormalized \(\Gamma_1\) or
\(Q_1\), residual transfer, a Lorentzian QME, Hadamard data, particles,
positivity, scattering or unitarity.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n1_n2_vector_cpt_projection --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n1_n2_vector_cpt_projection
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n1_n2_vector_cpt_projection -v
```
