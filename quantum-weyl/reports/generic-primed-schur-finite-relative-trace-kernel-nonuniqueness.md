# Generic primed Schur finite relative-trace kernel

## Result

The local longitudinal Schur data do not determine a
background-universal finite relative-trace kernel.

The declared completion class fixes:

- the complete polyhomogeneous symbol of
  \(S_L(W)=\frac23I+\frac13\delta(F+W)^{-1}d\);
- all Wodzicki residues and the scale density;
- the primed zero-mode projector;
- the positive weight \(Q_\mu=(\Delta_0+\Pi_0)/\mu^2\);
- the common Mellin/proper-time subtraction.

It permits self-adjoint smoothing differences on the primed complement.
Those are invisible to every fixed local datum but visible to finite weighted
traces.

## Exact finite-value witness

Choose a primed unit vector \(e\) with

\[
Ke=\frac12e,\qquad
T=\frac7{11}|e\rangle\langle e|.
\]

Extend \(T\) by zero on \(\ker\Delta_0\). Both \(I+K\) and \(I+K+T\) remain
positive. Exact trace differences are

\[
\Delta R_{\mu_0}(K)=\frac7{11},
\qquad
\Delta\operatorname{FP}R_{\mu_0}(K^2)=\frac{126}{121},
\]

\[
\Delta\log\det_3(I+K)=\log\frac{47}{33}-\frac{14}{121}.
\]

Consequently,

\[
\Delta\log\operatorname{Det}_{(3,R)}(I+K)
=
\log\frac{47}{33}\ne0.
\]

The perturbation is finite rank and smoothing, so its complete symbol and
Wodzicki residues vanish. It acts only on the primed complement, so the
zero-mode projector is unchanged.

## Exact third-curvature-row witness

For formal perturbation directions \(u_1,u_2,u_3\), set

\[
T(u)=\frac32u_1u_2u_3|e\rangle\langle e|.
\]

The family and its first two derivatives vanish at the base point. The mixed
third variations are

\[
\Delta\partial_{123}R_{\mu_0}(K)=\frac32,\qquad
\Delta\partial_{123}\operatorname{FP}R_{\mu_0}(K^2)=\frac32,
\]

\[
\Delta\partial_{123}\log\det_3(I+K)=\frac14,
\qquad
\Delta\partial_{123}\log\operatorname{Det}_{(3,R)}(I+K)=1.
\]

Multiplying the amplitude by a selected nonzero linear functional on the
certified ten-dimensional labelled carrier quotient changes that finite cubic
row while preserving the symbol, residues, scale response, zero modes and
subtraction. Thus the missing datum affects the requested form factors, not
only an irrelevant constant.

## Minimal additional input

A background-specific finite answer requires:

1. a content-addressed compact global scalar-flat metric and orientation;
2. complete scalar/vector domains and boundary conditions;
3. normalized primed projectors;
4. the global primed resolvent of \(F+W\) and scalar weight \(Q\), or an
   equivalent complete spectral measure with eigenprojectors;
5. the reference scale and determinant phase/contour policy.

These data select a background-specific Green/resolvent kernel. Local jets,
complete symbols, residues, the full-BV multiplicity ledger, and the isolated
round-\(S^4\) and \(S^2\times S^2\) spectra do not supply them. The two special
backgrounds remain holdouts and are not interpolated.

## Independent replay

The verifier does not import the producer. It realizes the primed vector and
deleted zero mode as a two-component exact matrix fixture, checks
\(T\Pi_0=\Pi_0T=0\), reconstructs the finite shifts by matrix traces, and
derives the cubic coefficient from a separate formal log-determinant series.
Five mutations of finite arithmetic, cubic response, zero-mode invariance,
special-background interpolation and full-BV promotion are rejected.

## Claim boundary

This is a `LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL` nonuniqueness theorem.
It completes the work item's permitted theorem branch and parameterizes the
remaining finite rows by global spectral data. It does not compute a
background-specific generic kernel, complete the full-BV five functions,
supply \(\Gamma_1\) or \(Q_1\), decide a QME, or establish Lorentzian,
Hadamard, state-space, particle, scattering or unitarity claims.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_primed_schur_finite_relative_trace_kernel_nonuniqueness \
  --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_primed_schur_finite_relative_trace_kernel_nonuniqueness
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_primed_schur_finite_relative_trace_kernel_nonuniqueness \
  -v
```

EVIDENCE: quantum-weyl/spectral/euclidean/certificates/GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json

CLOSE-OUT: DONE — exact nonuniqueness and the minimal global spectral input are
certified.
