# Parameterized five-form-factor family: independent freeze audit

Date: 2026-07-20

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

An independent rail verifies the terminal theorem that the generic
parity-even third-curvature five-form-factor result is an affine family over
global primed spectral data, rather than a universal finite coefficient
table.

The audit imports the terminal certificate and its complete declared
physical, ghost, contact, zero-mode and Schur dependency closure by hash. It
does not invoke the terminal producer or reuse its ambiguity matrix or rank
calculation.

The independent reconstruction finds:

- an eleven-channel raw carrier with the exact one-dimensional \(I_{28}\)
  relation and a ten-dimensional quotient;
- quotient \(S_3\) character \((10,4,1)\), decomposing as four trivial plus
  three standard representations and no sign representation;
- all 33 labelled contact rows, eleven relative-IBP channels, 33 corners and
  the zero Mellin endpoint finite constant;
- all four full-BV determinant factors and their primed zero-mode policies;
- ten admissible global smoothing completions whose finite third variations
  form an exact rank-ten ambiguity matrix.

A direct finite-matrix determinant model supplies two explicit admissible
completions with identical complete local symbol, residues, scale response,
zero-mode projector and subtraction prescription, but distinct mixed third
variations. Unit completions in the ten quotient coordinates then give an
identity ambiguity matrix. Its transpose kernel is zero:

\[
\dim\ker A^{T}=0.
\]

Therefore no nonzero universal finite Schur-sensitive linear combination of
the five form-factor functions survives. The round-\(S^4\) and
\(S^2\times S^2\) values cannot interpolate the generic datum; an explicit
holdout polynomial vanishes at both special backgrounds and is nonzero at a
generic third point.

## Claim boundary

This freezes the affine-family and zero-universal-kernel theorems only.
It preserves the already certified local-scale and maximal partial-BV
content. It does not compute a universal finite coefficient table,
\(\Gamma_1\), \(Q_1\), a QME disposition, or any Lorentzian, Hadamard, state,
particle, scattering or unitarity result.

## Evidence

- Certificate:
  `quantum-weyl/spectral/euclidean/certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json`
- Producer/check:
  `quantum-weyl/spectral/euclidean/parameterized_five_form_factor_independent_audit.py`
- Independent verifier:
  `quantum-weyl/spectral/euclidean/verify_parameterized_five_form_factor_independent_audit.py`
- Mutation tests:
  `quantum-weyl/spectral/euclidean/tests/test_parameterized_five_form_factor_independent_audit.py`
- Strict Draft 2020-12 schema:
  `quantum-weyl/spectral/euclidean/schema/parameterized-parity-even-five-form-factor-family-independent-audit-v1.schema.json`

The scoped producer check, independent verifier and seven mutation/replay
tests pass exactly. Tier 2 was not run because all imported mathematical
inputs are unchanged and content-addressed. Tier 3 was not run because this
is a scoped independent freeze audit, not a repository release, tag or
shared-core-algebra change.
