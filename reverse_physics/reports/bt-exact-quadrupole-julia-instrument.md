# Exact normalized BT quadrupole Julia instrument

**Certificate:** `REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

## Result

The compact-spacetime quadrupole response admits an exactly normalized
finite-strength operational detector on the certified active-pair packet
carrier.  This removes the expansion in an external detector coupling.  It
does not remove the perturbative BT expansion in \(\lambda\), and it does not
turn the resulting Kraus operators into bounded-region local-algebra
operators.

Let \(D_h\) be the degree-four local quadrupole density with the compact
spacetime switching from the predecessor.  Its pair-creation response vector
is

\[
 w_2=P_2D_hP_0|0\rangle,
\]

where \(P_0\) and \(P_2\) are the vacuum and two-particle projections.  The
strict compact-spacetime \(q_8\) theorem implies \(w_2\ne0\).  Normalize it:

\[
 u_2={w_2\over\|w_2\|}.
\]

On the active pair-packet Hilbert space, define

\[
 K_{\rm click}={1\over2}|0\rangle\langle u_2|.
\]

This is a bounded strict contraction of norm \(1/2\), with

\[
 K_{\rm click}^*K_{\rm click}={1\over4}P_u,
 \qquad
 K_{\rm click}K_{\rm click}^*={1\over4}P_0,
 \qquad P_u=|u_2\rangle\langle u_2|.
\]

## Exact click/no-click normalization

The source defect is

\[
 D_X=(I-K_{\rm click}^*K_{\rm click})^{1/2}
 =I+\left({\sqrt3\over2}-1\right)P_u,
\]

and the one-dimensional output defect is \(D_Y=\sqrt3/2\).  Therefore

\[
 K_{\rm no}=D_X,
 \qquad
 E_{\rm click}={1\over4}P_u,
 \qquad
 E_{\rm no}=I-{1\over4}P_u,
\]

and

\[
 E_{\rm click}+E_{\rm no}=I
\]

exactly.  In the fixture basis \((u_2,u_2^\perp;0_{\rm click})\), the Julia
operator is

\[
 U_J=
 \begin{pmatrix}
 \sqrt3/2&0&-1/2\\
 0&1&0\\
 1/2&0&\sqrt3/2
 \end{pmatrix}.
\]

Direct exact multiplication gives

\[
 U_J^*U_J=U_JU_J^*=I.
\]

Thus

\[
 \Psi\longmapsto(K_{\rm no}\Psi,K_{\rm click}\Psi)
\]

is an exact detector isometry, and

\[
 p_{\rm click}(\Psi)={1\over4}|\langle u_2,\Psi\rangle|^2,
 \qquad
 p_{\rm no}(\Psi)=\|\Psi\|^2-p_{\rm click}(\Psi).
\]

There is no \(O(g_{\rm det}^4)\) qualification in this operational
instrument.

## Exact darkness and strict response

The leading BT pair packet is angle-independent on every timelike pair
fibre:

\[
 X_2(P,n)=x_2(P).
\]

The response mode contains the trace-free quadrupole factor.  Hence

\[
 \langle u_2,X_2\rangle=0
\]

because

\[
 \int_{S_P^2}F_2(P,r)d\Omega_P=0
\]

separately for every \(P\).  This is exact on the complete fibrewise scalar
leading subspace, not one momentum fixture.

The compact-spacetime predecessor proves that the same response functional
has nonzero overlap with \(X_4\).  Normalizing its response vector cannot
change nonvanishing, so

\[
 \langle u_2,X_4\rangle\ne0.
\]

For the perturbative BT output \(X(\lambda)\), the exact instrument therefore
has

\[
 p_{\rm click}[X(\lambda)]
 ={1\over4}|\langle u_2,X(\lambda)\rangle|^2
 ={\lambda^8\over4}|\langle u_2,X_4\rangle|^2
 +O(\lambda^{10}),
\]

with a strictly positive order-eight coefficient.

This separates two expansions.  Detector normalization is exact at finite
strength.  The BT state remains known only coefficientwise in \(\lambda\).

## Why the full local exponential is not substituted

It would be incorrect to identify this Julia instrument with the exponential
of the full local quadratic Hamiltonian.  Although

\[
 \int_{-1}^{1}P_2(c)dc=0,
\]

three insertions contain a scalar component:

\[
 \int_{-1}^{1}P_2(c)^3dc={4\over35},
 \qquad
 {1\over2}\int_{-1}^{1}P_2(c)^3dc={2\over35}.
\]

Thus an odd third detector order can couple scalar input to scalar output.
The one-insertion dark identity does not structurally exponentiate.  This is
why the exact bounded instrument is constructed by defect completion rather
than by deleting higher terms of the microscopic exponential.

## Locality ledger

The underlying \(D_h\) is a finite-derivative local density smeared by a
function in \(C_c^\infty\).  The click Kraus operator is only its normalized
selected matrix-element compression:

\[
 K_{\rm click}
 ={1\over2\|P_2D_hP_0|0\rangle\|}P_0D_hP_2.
\]

It explicitly contains:

- the global vacuum projection \(P_0\);
- the global two-particle projection \(P_2\); and
- global response-mode normalization.

The no-click Kraus operator contains the global rank-one projector
\(P_u=|u_2\rangle\langle u_2|\).  Consequently the compact support of the
underlying density proves the locality of the insertion that supplies the
matrix element; it does not prove that \(K_{\rm click}\), \(K_{\rm no}\), or
\(U_J\) belongs to a bounded-region local AQFT algebra.

This is a nonidentification, not a no-go theorem.  A different bounded local
functional calculus or enlarged apparatus might still realize the same
effect locally.

## Claim boundary

Established:

- an exact finite-strength click/no-click instrument;
- exact effect normalization and an exact Julia unitary;
- exact darkness on every fibrewise angle-independent \(X_2\) packet;
- a strictly positive order-eight response to \(X_4\);
- removal of the external detector-coupling remainder; and
- the precise global projections preventing a local-Kraus promotion.

Not established:

- a bounded-region local-algebra realization of either Kraus operator;
- generation of the Julia unitary by \(D_h\);
- exact darkness of the full microscopic local exponential;
- public BT selection of the detector or vacuum readout;
- a convergent all-order BT probability in \(\lambda\);
- the \(\lambda^{10}\) and higher BT amplitudes;
- forward, collinear, real--virtual, or KLN completion;
- an all-time Moller, LSZ, or S operator;
- the standard scalar projector or general Eq. (19);
- gravity, metric BV--BRST, QME restoration, residual transfer, or anything
  `LORENTZIAN-CAUSAL`;
- literature priority.

The next physical gate is a bounded rotational-rank-two functional calculus
inside one compact local algebra.  If that cannot preserve exact darkness,
the first exact local-algebra obstruction is the deliverable.  The
BT-dynamical alternatives remain the \(\lambda^{10}\) dark remainder and
general Eq. (19).

## Verification commands

```text
ulimit -v 500000; python3 reverse_physics/bt_exact_quadrupole_julia_instrument.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_exact_quadrupole_julia_instrument.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_exact_quadrupole_julia_instrument
```

## Verification receipt

All Python and TeX commands below ran sequentially under
`ulimit -v 500000`; no out-of-memory event occurred.

- Producer: 28/28 checks passed in 1.34 s, peak 254680 KiB.
- Independent verifier: 34/34 checks passed in 1.12 s, peak 258512 KiB.
- Scoped mutation suite: 40/40 tests passed in 1.21 s wall time, peak
  277000 KiB (0.070 s unittest time).
- Paper 05 compiled twice in 1.57 s per pass, with peak 263332 KiB and
  272816 KiB.  The resulting 72-page, 708811-byte PDF has SHA-256
  `3ff9592708971ca1d473b393b6b915c43e78bed0f08b21038e198cc4b6ea0fe3`.
- Paper 06 compiled twice in 1.57 s and 1.55 s, with peak 272252 KiB and
  269964 KiB.  The resulting 63-page, 674545-byte PDF has SHA-256
  `3cff9e31d1a5283c74a3691edfc8e93a3975f5b9195a57208111e68d195c441e`.
  Both paper logs had no undefined references or citations and no new
  overfull boxes.
- Tier 3 ran 2784 tests in 703.160 s (704.27 s wall, peak 391448 KiB).
  The 40 new tests passed.  The run remained fail-closed with 31 failures
  and 9 skips; its sorted failure-name SHA-256 was
  `83a116976bf2fb697b95070337c41d79df0ffc80697a508f29d1240ff0f1bbc0`,
  exactly matching the predecessor baseline.  This is baseline stability,
  not a Tier-3 pass.
- Science Forge planning import wrote 1551 nodes with zero invalid work
  items and zero malformed events in 5.91 s, peak 222368 KiB.
- The advisory Science Forge shadow rail inventoried 1615 certificates and
  1393 verifiers in 1.98 s, peak 335656 KiB.  It again reported the known
  Forge-stdlib hash mismatch and `E9118` bridge-audit failure, plus corpus
  drift from the 2026-07-19 baseline.  The advisory wrapper exited zero, but
  the bridge audit is recorded as a failure and establishes no certificate
  pass.

The generated certificate SHA-256 is
`42f130a4d30abd1ccf533d14d3624340db52d1d15b4d9073398911f3551ffea9`.
