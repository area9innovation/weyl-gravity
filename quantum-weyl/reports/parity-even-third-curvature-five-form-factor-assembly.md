# Parity-even third-curvature five-form-factor assembly

## Disposition

The maximal generic scalar-flat parity-even five-carrier quotient currently
determined by the repository is now frozen. It contains the complete physical
Hessian, ghost \(n=3\), and pure-vector ghost \(n=1+n=2\) contributions:

```text
11 raw labelled orientation channels
10 effective channels
I28_123 + I28_132 + I28_231 = 0 coefficientwise
```

Every channel retains the seven-function representation

```text
J_triangle
log_x2_over_x1
log_x3_over_x1
rational_corner
M14_singlet
M15_standard_u
M16_standard_v
```

and the physical relative-IBP boundary fluxes and \(H_1\)-\(H_2\) contact
endpoints are included. This is a coefficient-computed **partial BV**
representative, not the complete one-loop BV five-function table.

## First missing analytic datum

The exact Hodge/Schur reduction has already combined all three open
longitudinal Diff--Weyl ghost towers into

\[
S_L(W)=\frac23 I+\frac13\delta(F+W)^{-1}d .
\]

The weighted-trace certificate determines its scale response,

\[
\frac{d}{d\log\mu}\log\operatorname{Det}_{(3,R_\mu)}S_L
=
\frac1{(4\pi)^2}\int
\frac{5R^2+22R_{\mu\nu}R^{\mu\nu}}{54},
\]

but does not determine the finite reference-scale values
\(R_{\mu_0}(K)\), \(\operatorname{FP}R_{\mu_0}(K^2)\), or the generic
\(\det_3(I+K)\) tail. A finite-rank smoothing perturbation preserves the full
homogeneous symbol and every Wodzicki residue while changing those finite
traces. Thus the first missing object is:

```text
GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL
```

The certificate carries a strict receiver contract for the content-addressed
primed Green/resolvent kernel or equivalent complete spectral measure,
zero-mode projector, common Mellin/proper-time subtraction, five-carrier
variations, and specialization checks.

## Holdouts and normalization

- The equal-box contact row is retained exactly.
- The flat-TT leading normalization is \(1/2\).
- The round-\(S^4\) finite Schur rows are exact special-background holdouts.
- The \(S^2(1)\times S^2(2)\) weighted rows and \(\det_3\) tail are rigorous
  interval holdouts.
- None of those special-background results is interpolated into a generic
  form factor.
- The additive strict \(C^2\) normalization remains unfixed.
- A dressed \(R^2\) normalization is a separate action-dependent constant
  outside the strict scalar-flat carrier. Neither local constant is folded
  into a nonlocal function.

## Independent rail

The verifier does not import or call the producer. It follows every pinned
source hash, reconstructs all eleven partial-BV channels from the original
physical, ghost-triangle and vector-ghost inputs with exact SymPy rational
functions, and proves the \(I_{28}\) relation coefficientwise. It separately
checks contact, scale, full-BV multiplicity, round-\(S^4\),
\(S^2\times S^2\), flat-TT, local-normalization and receiver-contract rows.

Five adversarial mutations are rejected:

1. one channel digest/sign;
2. the equal-box contact coefficient;
3. the Schur scale density;
4. the round-\(S^4\) zero-mode policy;
5. promotion to complete generic BV form factors.

The mutation rail is deliberately split from the full reconstruction. The
exact reconstruction runs once; each mutation reruns only the invariant it
targets. This keeps the scoped suite below the repository's approximately
60-second fast-rail threshold without weakening the checks.

## Claim boundary

The result is tagged `LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL`, with terminal
status `OBSTRUCTED` for the requested **full** generic-BV assembly. It does not
compute the missing longitudinal finite rows, complete \(\Gamma_1\) or \(Q_1\),
decide or restore the QME, authorize residual transfer, or establish a
Lorentzian, Hadamard, state-space, particle, scattering, or unitarity claim.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.parity_even_third_curvature_five_form_factor_assembly \
  --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_parity_even_third_curvature_five_form_factor_assembly
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_parity_even_third_curvature_five_form_factor_assembly \
  -v
```

EVIDENCE:
`quantum-weyl/spectral/euclidean/certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json`

CLOSE-OUT: OBSTRUCTED — the maximal exact partial-BV quotient is frozen and
the first missing generic finite Schur kernel has a complete receiver contract.
