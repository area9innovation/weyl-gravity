# Globally parameterized parity-even five-form-factor family

## Result

The complete finite parity-even table is an affine family over explicitly
declared global spectral data:

\[
F_{\rm full}[D]
=F_{\rm partial\,BV}+F_{\rm Schur}[D]
+c_{C^2}L_{C^2}+c_{\widehat R^2}L_{\widehat R^2}.
\]

Here \(D\) is a content-addressed compact scalar-flat metric together with
domains, primed projectors, a global resolvent or complete spectral measure,
reference scale, and determinant phase/contour. The two local constants remain
separate from the nonlocal functions.

## Universal content

The following remain universal and coefficient-computed within their declared
scope:

- the physical + ghost-\(n=3\) + vector-ghost partial-BV summand;
- eleven raw and ten effective labelled channels;
- the coefficientwise \(I_{28}\) relation;
- source-permutation covariance;
- physical relative-IBP fluxes and contact endpoints;
- the local longitudinal-Schur scale response.

The exact formula and all eleven row digests are imported unchanged.

## Full ambiguity rank

Use the canonical ten-coordinate section obtained by eliminating the trivial
\(S_3\) component of \(I_{28}\). The imported cubic smoothing theorem can be
multiplied by each coordinate functional independently. In this basis the
finite Schur ambiguity matrix is

\[
A=I_{10}.
\]

The certificate stores the matrix and ten normalized dual separators. Hence

\[
\operatorname{rank}A=10,\qquad
\ker A^\mathsf{T}=0.
\]

Therefore no nonzero complete finite Schur-sensitive linear combination is
background-universal. This does not erase the known partial-BV summand; it says
that completing it requires selecting \(D\).

Round \(S^4\) and \(S^2(1)\times S^2(2)\) are individual evaluations at their
own global data. They remain holdouts and do not define a generic section by
interpolation.

## Independent replay

The verifier follows both dependency hashes, reconstructs the canonical
ten-coordinate section, computes the exact matrix rank and transpose
nullspace independently with SymPy, and checks that the partial formula,
channel digests, scale row, unit smoothing source, holdouts, and local
normalizations are unchanged. It rejects mutations of the matrix rank,
interpolation policy, local/nonlocal separation, and full-table promotion.

## Claim boundary

This `LOCAL-ALGEBRAIC`/`EUCLIDEAN-SPECTRAL` result is the strongest exact
five-factor retry permitted by the kernel theorem. It is not a universal
finite coefficient table, complete \(\Gamma_1\) or \(Q_1\), QME disposition,
Lorentzian construction, Hadamard state, particle interpretation, scattering,
or unitarity result.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.parameterized_parity_even_five_form_factor_family --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_parameterized_parity_even_five_form_factor_family
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_parameterized_parity_even_five_form_factor_family \
  -v
```

EVIDENCE: quantum-weyl/spectral/euclidean/certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY.json

CLOSE-OUT: DONE — the exact affine family, its rank-ten ambiguity module, and
the zero-dimensional universal finite Schur quotient are certified.
