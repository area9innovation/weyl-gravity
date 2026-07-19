# Generic physical-Hessian H1-H2 contact-residue projection

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The generic logarithmic endpoint kernels of all three mixed physical-Hessian
contact cells are now exact.  If leg (i) carries (H_1), while the other
two labelled legs (j,k) enter the polarized algebraic (H_{2,jk}), the two
resolved bubble endpoints are

\[
 \operatorname{Res}_{i,0}
 =-\frac{\operatorname{tr}\!left(H_{2,jk}H_{1,i}(k_i,0)\right)}
          {2(k_i^2)^2},
 \qquad
 \operatorname{Res}_{i,1}
 =-\frac{\operatorname{tr}\!\left(H_{2,jk}H_{1,i}(k_i,-k_i)\right)}
          {2(k_i^2)^2}.
\]

Direct exact tensor evaluation proves

\[
 \operatorname{Res}_{i,0}=\operatorname{Res}_{i,1}
\]

on all 28 training and two unseen nonexceptional scalar-flat momentum
fixtures.  The loop-momentum pair term is finite at both endpoints and does
not contribute to the logarithmic residue.

Each endpoint is projected onto the same eleven raw labelled channels of the
five-carrier manifest used by the physical three-(H_1) numerator.  The
symmetric (I_{28}) relation reduces these to the ten-dimensional quotient.
For a carrier of explicit derivative order (d), every coordinate is stored
as

\[
 \frac{P_{5-d/2}(x_1,x_2,x_3)}{(x_1x_2x_3)^2},
\]

where (P) is an exact homogeneous rational polynomial.  There are 33
stored rows: eleven raw coordinates for each of the three contacts.  The
interpolation digest is
`bce52f6ef0af9104989f0707ce9b33fa1b94e7514f63f953586ef126333966bb`.
Both unseen fixtures have zero channel defects, and the (I_{28}) relation
is checked coefficient by coefficient after interpolation.

The common Mellin extension therefore fixes the scale-bearing contact term

\[
 2\operatorname{Res}_{i,0}\log\frac{\mu^2}{x_i}
\]

for every projected channel.  On the earlier equal-box TT fixture, the
single-endpoint coefficients are

\[
 \frac{1127}{54},\qquad \frac{115}{9},\qquad \frac{887}{54},
\]

and the six-endpoint sum is exactly (2704/27), reproducing the independent
fixture certificate.

This is not yet the renormalized mixed physical form factor.  Finite local
contact rows have not been fixed, the triangle and contact boundary incidence
has not been assembled, and the isolated three-(H_1) `M14` corner class has
not been disposed.  No QME or Lorentzian status changes.

## Replay

The normal rail consumes the content-addressed fixture ledger:

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_h1_h2_contact_residue_projection --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_h1_h2_contact_residue_projection
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_h1_h2_contact_residue_projection
```

The exhaustive exact tensor replay is intentionally separate:

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_h1_h2_contact_residue_projection --rebuild-fixtures --workers 4
```

## Verification receipt

Recorded on 2026-07-19.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 2 generation | `...contact_residue_projection --rebuild-fixtures --workers 4` | 91 s | PASS, 30 exact fixtures and 33 rows |
| 0/1 | `...contact_residue_projection --check` | 0.65 s | PASS |
| 1 | `python3 -m unittest ...test_generic_background_physical_hessian_h1_h2_contact_residue_projection` | 0.66 s | PASS, 5 tests |
| 1 | `...verify_generic_background_physical_hessian_h1_h2_contact_residue_projection` | 10.06 s | PASS, unseen tensor replay |
| 2 | `PYTHONPATH=quantum-weyl python3 -m verify_active_frontier` plus scoped tests | 0.9 s | PASS |
| 2 | quantum atlas emit, independent verifier and scoped tests | 3.3 s | PASS |
| 2 | Paper 12 claim-map emit and independent verifier | 0.2 s | PASS |
| 2 | Paper 12 main (two passes) and supplement (three passes) | 4.3 s | PASS; final passes warning-free |

Tier 3 is not required: this closes a scoped coefficient-bearing
contact-residue gate without a theorem freeze or lifecycle promotion.
