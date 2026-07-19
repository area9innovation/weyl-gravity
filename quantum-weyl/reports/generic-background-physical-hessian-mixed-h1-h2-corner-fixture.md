# Physical mixed \(H_1\)-\(H_2\) corner fixture

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The imported algebraic \(H_2\) block is now operational on one rational
equal-box scalar-flat TT fixture. The external momenta obey

\[
 k_1+k_2+k_3=0,
 \qquad k_1^2=k_2^2=k_3^2=1,
\]

and all arithmetic is exact. The nine scalar-flat source rows are polarized
between two labelled external curvatures, averaged over the two field slots,
and projected to the rank-nine traceless representation. All three resulting
\(H_2\) matrices have rank nine and are formally self-adjoint. A separate
round-row replay reproduces the relevant entries of the imported source
ledger term by term.

## The correct carrier comparison

The three-\(H_1\) term is a two-dimensional, three-propagator Feynman-simplex
density. The mixed term is instead a one-dimensional, two-propagator bubble:

\[
 \frac16\operatorname{Tr}(G H_1)^3,
 \qquad
 -\frac12\operatorname{Tr}(G H_1 G H_2).
\]

It is therefore invalid to add \(H_2\) to the interior triangle numerator.
The certificate uses one common dimensionless endpoint cutoff and compares
all three triangle corners with both endpoints of all three labelled mixed
bubbles.

For the two cyclic \(H_1^3\) orientations, the three corner weights are

\[
 \left(-\frac{161}{72},-\frac{137}{108},-\frac{461}{432}\right),
 \qquad
 \left(-\frac{461}{432},-\frac{137}{108},-\frac{161}{72}\right).
\]

Including cyclic multiplicity three for each orientation gives

\[
 c_{H_1^3}^{\rm raw}=-\frac{1975}{72}.
\]

The left and right endpoint weights of the three mixed bubbles are equal
within each row:

\[
 \frac{1127}{54},\qquad \frac{115}{9},\qquad \frac{887}{54},
\]

so

\[
 c_{H_1H_2}^{\rm raw}=\frac{2704}{27}.
\]

The combined raw logarithmic coefficient is therefore

\[
 \boxed{
 c_{\rm physical}^{\rm raw}
 =-\frac{1975}{72}+\frac{2704}{27}
 =\frac{15707}{216}\ne0
 }
\]

before the common \((4\pi)^{-2}\) factor.

## What this establishes

One exact counterexample is enough to reject a universal algebraic identity
in which the imported \(H_2\) automatically cancels the isolated
three-\(H_1\) corner. The remaining route is to declare and certify a local
covariant subtraction/distribution extension, then assemble the renormalized
mixed rows.

This does not yet dispose the `M14` relative class: the bubble endpoints and
triangle interior live on different parameter carriers until that
renormalized extension is fixed. It also does not complete the five physical
form factors, alter the anomaly/QME result, or make a Lorentzian claim.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_mixed_h1_h2_corner_fixture --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_mixed_h1_h2_corner_fixture
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_mixed_h1_h2_corner_fixture
```

## Verification receipt

Recorded on 2026-07-19 from the shared `master` worktree:

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_mixed_h1_h2_corner_fixture --check` | 30.04 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_mixed_h1_h2_corner_fixture` | 0.67 s | PASS |
| 1 | `PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_mixed_h1_h2_corner_fixture` | 29.92 s | PASS, 6 tests |
| 2 | `PYTHONPATH=quantum-weyl python3 -m verify_active_frontier` | 0.59 s | PASS |
| 2 | `PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment` | 1.58 s | PASS |
| 2 | `python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py` | 0.23 s | PASS |

The generator and unit suite were measured concurrently and nevertheless stay
inside the 60-second scoped-test rail. Tier 3 was not run: this chunk changes
no theorem-freeze or lifecycle state and does not modify shared core algebra.
