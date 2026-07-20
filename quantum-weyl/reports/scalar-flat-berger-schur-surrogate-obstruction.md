# Scalar-flat Berger Schur surrogate obstruction

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-scalar-flat-berger-primed-schur-spectral-measure`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Exact result

The selected compact Euclidean datum is

\[
M=S^1_{2\pi}\times SU(2),\qquad
g=d\theta^2+\sigma_1^2+\sigma_2^2+4\sigma_3^2,
\]

with

\[
\operatorname{Ric}=\operatorname{diag}(0,-1,-1,2),\qquad R=0.
\]

Let \(E_i\) be the standard cyclic \(SU(2)\) generators.  The orthonormal
Berger frame is

\[
e_1=E_1,\qquad e_2=E_2,\qquad e_3=\frac12E_3.
\]

Consequently the scalar Fourier/\(SU(2)\) blocks are diagonal:

\[
\Delta_0=n^2+j(j+1)-\frac34m^2,
\]

\[
D_W:=\delta Wd=2j(j+1)-3m^2,\qquad
W=-2\operatorname{Ric}.
\]

The constant block \((n,j,m)=(0,0,0)\) is the sole scalar mode removed by
\(\Delta_0^{-1}\).  Every scalar block has left multiplicity \(2j+1\).

## First exact obstruction

The successor work package named

\[
\widetilde S(t)
=I+\frac t3\Delta_0^{-1}\delta Wd
\]

as the scalar Schur operator.  That formula is not the normalized Schur
operator frozen by the generic determinant factorization.

The correction in \(\widetilde S\) is order zero.  On the four orthonormal
unit covectors \((d\theta,e^1,e^2,e^3)\), its principal-symbol values are

\[
1,\qquad \frac53,\qquad\frac53,\qquad-\frac13.
\]

It therefore does not have identity principal symbol.

The actual normalized Schur operator is

\[
S_L(t)=\frac23I+\frac13\delta(F+tW)^{-1}d.
\]

Its correction begins at pseudodifferential order \(-2\), and its first
variation is

\[
\left.\frac{dS_L}{dt}\right|_{t=0}
=-\frac13\Delta_0^{-1}\delta Wd\,\Delta_0^{-1}.
\]

The first nonconstant representation block already distinguishes the two
operators.  For \(n=0\), \(j=1/2\), \(|m|=1/2\),

\[
\Delta_0=\frac9{16},\qquad D_W=\frac34.
\]

Hence

\[
\left.\frac{d\widetilde S}{dt}\right|_{0}=\frac49,
\qquad
\left.\frac{dS_L}{dt}\right|_{0}=-\frac{64}{81}.
\]

An independent replay constructs the spin-\(1/2\) Pauli matrices directly
and obtains the same two scalar matrices.  It does not import the producer's
Casimir formula.

## Disposition

The complete primed spectral measure cannot be constructed as requested,
because the named one-inverse scalar operator would compute a different
order-zero determinant.  No global mode truncation or analytic continuation
can repair an incorrect operator input.

The next strictly smaller theorem is now explicit:

1. derive the finite vector pencil
   \(A_{njm}(t)=F_{njm}+tW\);
2. derive \(d_{njm}\) and \(\delta_{njm}\) on the same normalized blocks;
3. invert \(A_{njm}(t)\) on the common primed domain;
4. construct
   \[
   S_{L,njm}(t)=\frac23I+\frac13\delta_{njm}
   A_{njm}(t)^{-1}d_{njm};
   \]
5. only then address matched zero-pole factors, insertion projectors and
   uniform determinant tails.

The corrected request is
`planning/forge-requests/scalar-flat-berger-coupled-vector-schur-blocks.json`.

## Claim boundary

This result computes exact scalar blocks and an exact first operator
obstruction.  It does not compute the true coupled vector Schur blocks, a
complete primed resolvent, insertion eigenprojectors, interval tails,
\(\det_3\), weighted finite traces, five background-specific functions,
\(\Gamma_1\), \(Q_1\), a QME disposition, or any Lorentzian, Hadamard, state,
particle, positivity, scattering or unitarity result.

## Verification

```text
python3 -m py_compile <producer> <independent verifier> <tests>
python3 quantum-weyl/spectral/euclidean/scalar_flat_berger_schur_surrogate_obstruction.py --emit
python3 quantum-weyl/spectral/euclidean/scalar_flat_berger_schur_surrogate_obstruction.py --check
python3 quantum-weyl/spectral/euclidean/verify_scalar_flat_berger_schur_surrogate_obstruction.py
python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_scalar_flat_berger_schur_surrogate_obstruction.py -v
```

The producer emit/check passes took 0.10 s and 0.21 s.  The independent
Pauli-matrix replay passed in 0.67 s.  Six tests passed in 0.47 s and reject
principal-symbol, lowest-block, full-resolvent, five-function and
QME/Lorentzian promotions.

EVIDENCE:
`quantum-weyl/spectral/euclidean/certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json`;
`planning/forge-requests/scalar-flat-berger-coupled-vector-schur-blocks.json`

CLOSE-OUT: DONE — the first exact representation/operator obstruction is
proved, and the next smaller coupled-vector Schur theorem is named without
promoting any finite coefficient.
