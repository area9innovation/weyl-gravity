# Scalar-flat Berger vector-Schur high-mode trace-majorant obstruction

Date: 2026-07-21

Science Forge work item:
`sf:program/work/quantum-scalar-flat-berger-vector-schur-high-mode`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The terminal low-block theorem supplies a unique self-adjoint pencil and
normalization,

\[
A(t)=F+tW,
\qquad
S_L(t)=\frac23 I+\frac13\delta A(t)^{-1}d,
\]

with \(F=\nabla^*\nabla+\operatorname{Ric}\),
\(W=-2\operatorname{Ric}\), \(\delta=d^\dagger\), and the normalized product
Haar representation norm.  The import gate therefore passes.

The requested ordinary summable majorants for all three metric insertions do
not exist.  The first insertion already fails.  The fixed-domain Ward
reduction gives

\[
B_1=-\frac13\Delta_0^{-1}\delta Wd\,\Delta_0^{-1}.
\]

On the exact \(n=0\) scalar mode \((j,m)\),

\[
q_{jm}=j(j+1)-\frac34m^2,
\qquad
p_{jm}=2j(j+1)-3m^2,
\]

and hence

\[
b_{1;jm}=-\frac{p_{jm}}{3q_{jm}^2}.
\]

The independent rail reconstructs \(A(t)\) directly from the representation
matrices and Levi-Civita connection and verifies this diagonal formula against
the exact derivative of \(S_L(t)\) for four nontrivial spins.

## Exact divergent subfamily

For \(j\geq1\) and \(|m|\leq j/2\),

\[
q_{jm}\geq \frac14j^2+j>0,
\]

and

\[
p_{jm}-\frac54j^2
=2j+3\left(\frac{j^2}{4}-m^2\right)\geq0,
\]

while

\[
2j^2-q_{jm}
=j(j-1)+\frac34m^2\geq0.
\]

Therefore

\[
|b_{1;jm}|\geq\frac{5}{48j^2}.
\]

Writing \(N=2j\), the central-band count is exactly
\(\lfloor3N/4\rfloor-\lceil N/4\rceil+1\); the four residue classes of
\(N\bmod4\) prove that this is at least \(N/4=j/2\).  The left regular
multiplicity is \(2j+1\geq2j\).  Thus every spin shell satisfies

\[
(2j+1)\sum_{|m|\leq j/2}|b_{1;jm}|\geq\frac5{48}.
\]

The sum over \(j\) diverges by comparison with
\(\sum_{j\geq1}5/48\).  This is an exact representation-theoretic
non-trace-class witness, not a cutoff observation or an asymptotic
\(O\)-estimate.

## Disposition

The work package requested summable majorants for the first three insertions.
That gate is obstructed at the first insertion.  A correct determinant route
must instead retain a declared regulator/subtraction for \(B_1\), a finite-part
prescription for the order-minus-four \(B_2\) term, and use an ordinary trace
only for the trace-class tail beginning at cubic order.

This certificate does **not** decide the separate high-mode invertibility of
\(A(t)\), classify its finite exceptional blocks, compute a regulated
\(B_1\) or finite \(B_2\) value, or produce a global determinant.  It does not
compute an anomaly coefficient, a Slavnov breaking, a QME disposition, a
Lorentzian causal object, a Hadamard state, particles, positivity, scattering,
or unitarity.

## Evidence and verification

```text
python3 quantum-weyl/spectral/euclidean/scalar_flat_berger_vector_schur_high_mode_trace_obstruction.py --check
python3 quantum-weyl/spectral/euclidean/verify_scalar_flat_berger_vector_schur_high_mode_trace_obstruction.py
python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_scalar_flat_berger_vector_schur_high_mode_trace_obstruction.py -v
```

EVIDENCE: `quantum-weyl/spectral/euclidean/certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1.json`

CLOSE-OUT: DONE — the dependency import gate passes and the requested ordinary
three-majorant tail preflight has its first exact obstruction at \(B_1\).
