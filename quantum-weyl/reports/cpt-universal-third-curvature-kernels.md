# Exact universal third-curvature kernels

Status:
`FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED_REPOSITORY_CONFORMAL_GRAVITON_TRACE_SUBSTITUTION_OPEN`

Dependency tag: `EUCLIDEAN-SPECTRAL`.

## What is now computed

The primary covariant-perturbation-theory source ships a Mathematica
ancillary file for its third-curvature effective-action form factors.  The
five rows relevant to the certified scalar-flat pure-gravity carrier quotient
have now been imported exactly:

| carrier | source row | source-generic stabilizer | effective scalar-flat stabilizer | derivatives | box degree of \(\Gamma_i\) |
|---|---:|---|---|---:|---:|
| `I10` | 10 | \(S_3\) | \(S_3\) | 0 | -1 |
| `I24` | 24 | \(S_2(23)\) | \(S_2(23)\) | 2 | -2 |
| `I25` | 25 | \(S_2(23)\) | \(S_2(23)\) | 2 | -2 |
| `I28` | 28 | \(S_2(12)\) | \(S_2(12)\) | 4 | -3 |
| `I29` | 29 | \(C_3\) | \(S_3\) | 6 | -4 |

The `I29` source row is written with cyclic generic-Ricci symmetry, but its
imported alpha numerator is already fully `S3` symmetric.  This agrees with
the independently certified reversal identity after restriction to the
transverse scalar-flat `K` carrier.  Both symmetry levels are retained so the
source convention is not silently rewritten.

Each function is stored in the exact form

\[
 \Gamma_i=\left\langle\frac{dff_i(\alpha,\Box)}{-\Omega}\right\rangle_3
 +T_i(\Box)+L_i(\Box),
\qquad
 \Omega=\alpha_2\alpha_3\Box_1+
 \alpha_1\alpha_3\Box_2+
 \alpha_1\alpha_2\Box_3.
\]

The machine independently checks rational arithmetic, simultaneous label
symmetrization and box homogeneity.  In the rank-one minimal scalar-Laplacian
fixture with \(P=0\) and zero bundle curvature, these five functions are the
complete coefficient-bearing pure-gravity third-curvature rows in the source
normalization

\[
 -W=\frac1{2(4\pi)^2}\int\sqrt g\,\sum_i\Gamma_i\mathcal R_i.
\]

## Why this is not yet the Weyl-graviton answer

The repository conformal-graviton ledger supplies special-background
constrained determinant factors, multiplicities and local \(b_4\) matches.
That data does not determine the generic-background substitution into the
universal kernels.  For tensor and ghost bundles, the Laplace-type
endomorphism \(P\) and bundle connection curvature \(\mathcal R_{\mu\nu}\)
are already linear in the spacetime curvature.  Their cubic CPT rows therefore
feed the same five pure-gravity carriers.  Summing only the four constrained
bundle ranks would omit those contributions.

There is also a sharp information mismatch: the available special-background
fixtures determine finitely many local heat-kernel coordinates, while the
target is five three-variable functions modulo the one symmetric
four-dimensional relation.  The repository coefficient problem is therefore
non-identifiable from the current ledger.

The minimal missing physical import is a same-gauge generic-background
full-BV Hessian, reduced either to minimal Laplace-type blocks with complete
bundle trace substitutions through curvature order three, or treated by a
direct nonminimal fourth-order covariant-perturbation calculation, together
with its matching generic-background measure.

## Provenance and replay

Primary source: Barvinsky, Gusev, Zhytnikov and Vilkovisky,
*Covariant perturbation theory. IV. Third order in the curvature*,
[arXiv:0911.1168](https://arxiv.org/abs/0911.1168), section 7 and
`anc/ffwa.m`.  The certificate pins both the source-archive and ancillary-file
SHA-256 digests.

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.cpt_universal_third_curvature_kernels --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_cpt_universal_third_curvature_kernels
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_cpt_universal_third_curvature_kernels.py -v
```

Certificate:
`quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json`.

## Claim boundary

This computes five universal source kernels and a coefficient-bearing scalar
fixture.  It does not compute the five repository conformal-graviton
functions or coefficients, classify the parity-odd derivative carrier sector,
fix finite normalizations, supply complete \(\Gamma_1\) or \(Q_1\), authorize
residual transfer, or establish any Lorentzian or particle statement.
