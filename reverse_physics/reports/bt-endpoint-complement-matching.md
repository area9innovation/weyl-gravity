# BT endpoint-complement matching law

**Certificate:** `REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The simplest fixed endpoint-extension route cannot supply the missing
public-to-physical Krein block over the physical continuum.  The obstruction
is exact and already appears on three rational physical fixtures.

This statement has a deliberately narrow domain.  It applies to the fixed
two-profile lift

\[
 v_0(z)=1,\qquad v_1(z)=z(1-z),
\]

whose three products are exactly the independent reflection-even endpoint
probes used in the certified extension classification.  It does not classify
spectator-dependent counterterms or every possible dynamical profile lift.

## The affine endpoint extension

Write the complete extension as

\[
 H_c=H_+ +c_0E_0+c_1E_1+c_2E_2,
\]

where \(H_+\) is the symmetric triple-plus reference and

\[
 E_0=\delta_0+\delta_1,\qquad
 E_1=\delta'_0-\delta'_1,\qquad
 E_2=\delta''_0+\delta''_1.
\]

On

\[
 f_{00}=1,\qquad f_{01}=z(1-z),\qquad
 f_{11}=z^2(1-z)^2,
\]

the endpoint jets act by

\[
 A=
 \begin{pmatrix}
 2&0&0\\
 0&-2&-4\\
 0&0&4
 \end{pmatrix},
 \qquad \det A=-16.
\]

The affine reference matters.  Direct Taylor-subtracted integration gives

\[
 \bigl(H_+[f_{00}],H_+[f_{01}],H_+[f_{11}]\bigr)
 =\left(0,0,\frac32\right).
\]

Therefore the induced symmetric Gram is

\[
 K(c)=
 \begin{pmatrix}
 2c_0&-2c_1-4c_2\\
 -2c_1-4c_2&\frac32+4c_2
 \end{pmatrix}.
\]

Dropping the \(3/2\) reference term would incorrectly treat the affine
extension space as a vector space and would change the constant parts of the
matching coefficients.

## Unique pointwise matching law

The finite physical Møller-column theorem forces the missing pullback Gram

\[
 G_{\rm miss}(\rho)=
 \begin{pmatrix}
 0&-\rho\\
 -\rho&-2
 \end{pmatrix},\qquad \rho>0.
\]

Solving \(K(c)=G_{\rm miss}(\rho)\) gives the unique result

\[
 \boxed{
 c_0=0,\qquad c_1=\frac74+\frac\rho2,
 \qquad c_2=-\frac78.}
\]

Thus a pointwise endpoint match is algebraically possible.  But it is not a
fixed extension: the coefficient of
\(\delta'_0-\delta'_1\) must change with the physical external-jet invariant
\(\rho\).

This conclusion does not depend on choosing the triple-plus reference.  If an
arbitrary fixed affine reference acts on the three probes by
\((\beta_{00},\beta_{01},\beta_{11})\), then

\[
 c_0=-\frac{\beta_{00}}2,\qquad
 c_2=\frac{-2-\beta_{11}}4,
\]

\[
 c_1=\frac{\rho+\beta_{01}+\beta_{11}+2}{2}.
\]

Changing the reference shifts the intercepts but leaves

\[
 \frac{dc_1}{d\rho}=\frac12
\]

unchanged.

## Exact physical witnesses

The three imported external-jet fixtures give

\[
 \rho_1=\frac{819}{4000},\qquad
 \rho_2=\frac{4416}{4913},\qquad
 \rho_3=\frac{16275}{70304}.
\]

They are pairwise distinct.  Relative to \(H_+\), their required
\(c_1\) values are respectively

\[
 \frac{14819}{8000},\qquad
 \frac{43223}{19652},\qquad
 \frac{262339}{140608}.
\]

The universal obstruction is immediate.  If the same fixed \(c\) matched two
fibres, then

\[
 0=G_{\rm miss}(\rho_a)-G_{\rm miss}(\rho_b)
 =\begin{pmatrix}
 0&\rho_b-\rho_a\\
 \rho_b-\rho_a&0
 \end{pmatrix},
\]

so \(\rho_a=\rho_b\).  The physical domain contains exact fixtures for which
this is false.

## Meaning for Eq. (19)

The old endpoint ambiguity is not, by itself, the missing universal BT
mechanism.  A single fixed reflection-even prescription for the public
endpoint distribution cannot turn the rank-one public leg into the physical
two-direction Gram across external kinematics.

There remains a sharper constructive possibility: BT dynamics could generate
a spectator-dependent endpoint coefficient equivalent to

\[
 c_1(\rho)=\frac74+\frac\rho2
\]

after a fixed choice of reference.  Nothing in the public finite
order-\(\lambda\) map, the current zero-mode trace, or the published Appendix C
derives that law.  The next calculation should therefore compute the
covariant zero-mode and squeezed-vacuum endpoint distribution on the same
external-jet domain and test this exact target.

The result does not prove or disprove all-order Eq. (19).  It does not alter
the exact finite physical vacuum column.  It rules out one universal shortcut
and converts the remaining endpoint possibility into a falsifiable dynamical
coefficient law.

## Claim boundary

Established exactly:

- the complete affine endpoint Gram on the fixed two-profile probe lift;
- the unique pointwise matching coefficients;
- reference-independent slope \(dc_1/d\rho=1/2\);
- failure of one fixed coefficient triple on three physical rational
  fixtures.

Not established:

- a no-go for spectator-dependent local counterterms or another dynamical
  profile lift;
- derivation of \(c_1(\rho)\) from BT zero-mode, vacuum, or composite dynamics;
- the all-order projector pushforward or Eq. (19);
- a fourth jump, complete BT probability, two-sided spacetime S operator,
  gravity/BRST transfer, new dimension, or anything `LORENTZIAN-CAUSAL`.

## Verification

All scientific commands run sequentially under `ulimit -v 500000`:

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_endpoint_complement_matching.py --write --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_endpoint_complement_matching.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_endpoint_complement_matching
```

The producer reconstructs the endpoint distributions with exact polynomial
coefficient arithmetic and solves the matching system symbolically.  The
independent verifier instead integrates the Taylor-subtracted polynomial
probes with SymPy, solves the triangular system directly, imports the physical
fixtures independently, and checks the subtraction obstruction.  The focused
tests mutate the affine reference, jet matrix, matching intercept and slope,
physical fixtures, universality statement, dynamic-complement boundary,
Eq. (19) boundary, physical-S boundary, scope ledger, and input hashes.

Primary source boundary: Bateman--Turok,
[arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096v1), especially Eq. (16),
Eq. (19), and Appendix C.

## Verification receipt (2026-08-11)

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile of producer, verifier, and tests | PASS | 0.04 s | 15,348 KB |
| 0 | work-item, certificate, and schema JSON parse | PASS | 0.02 s | 12,692 KB |
| 0 | exact staged `git diff --check` | PASS | 0.01 s | 11,556 KB |
| 1 | exact producer and certificate drift check | PASS, 25/25 | 0.47 s | 68,500 KB |
| 1 | method-distinct symbolic-integration verifier | PASS, 23/23 | 0.58 s | 73,504 KB |
| 1 | producer/verifier plus thirteen falsifying mutations | PASS, 15/15 | 6.21 s | 73,952 KB |
| paper | Paper V two-pass PDF build | PASS, 39 pages | 0.42 / 0.42 s | 50,764 / 50,528 KB |
| paper | Paper VI two-pass PDF build | PASS, 41 pages | 0.47 / 0.45 s | 50,732 / 50,864 KB |

Paper V retains four pre-existing overfull boxes and its pre-existing
PDF-string warnings; the inserted passage creates no new overfull box.  Paper
VI has no overfull box.  PDF text extraction finds the fixed-profile matching
law, certificate identifier, distinct-fixture witness, and
spectator-dependent boundary in both rendered papers.  The added-line audit
finds no changelog prose in either manuscript.

Tier 2 is unnecessary because all mathematical inputs are unchanged and
content-addressed; this certificate is a new consumer and changes no shared
operator, schema, or predecessor result.  Tier 3 is unnecessary because no
freeze, release, all-order Eq. (19), complete physical theory, shared-core
algebra, gravity transfer, or Lorentzian theorem is promoted.

The advisory Science Forge shadow rail was attempted under the same memory
cap.  Its bridge audit is recorded as **FAIL**, not pass: the Go toolchain and
the `cbp callers/where` subprocesses could not reserve page-summary memory.
The separate read-only coverage census completed and reported corpus drift at
1,541 certificates versus the 2026-07-19 baseline of 976.  The advisory
wrapper returned zero by design; neither that exit code nor the census is
counted as scientific evidence.  The memory cap was not relaxed.
