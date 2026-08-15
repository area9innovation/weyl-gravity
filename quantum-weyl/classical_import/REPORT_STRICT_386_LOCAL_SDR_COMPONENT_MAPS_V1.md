# Strict 386-row local SDR component maps v1

## Outcome

Yes. In the published split coordinates the thirty Gate endpoint rows are retained verbatim, while the repaired thirty-six-row generalized-auxiliary summand and the 320-row curvature mapping cone are contracted by one exact order-zero H_alg with 190 rational entries. The endpoint inclusion and projection each have thirty identity entries; P_end is the endpoint diagonal and P_alg is the complementary 356-row diagonal. Across all 70 unary derivative multiindices, q1 H_alg+H_alg q1=P_alg has zero defects. The inclusion and projection are chain maps, p_end i_end=I_30, i_end p_end=P_end, both projectors are complementary commuting idempotents, all normalized side conditions hold, and H_alg^T Omega-D Omega H_alg has zero exact defects. The maps are support-local finite data formalizable in PRA and add no choice operation. This closes the split local-SDR route only. The degree-zero T/A/B canonical shear that transports the split presentation to the unshifted curvature graph remains a separate component-jet object, and advanced/retarded Green actions still require represented analytic spaces. Therefore no common Gate-A snapshot, local D, q2, Hadamard or QME claim is promoted.

## Exact map inventory

| map | shape | degree | nonzero exact entries |
|---|---:|---:|---:|
| `H_alg` | 386 x 386 | -1 | 190 |
| `P_alg` | 386 x 386 | 0 | 356 |
| `P_end` | 386 x 386 | 0 | 30 |
| `i_end` | 386 x 30 | 0 | 30 |
| `p_end` | 30 x 386 | 0 | 30 |

## Independent exact identities

- `q1 H_alg + H_alg q1 = P_alg`: **PASS** across 70 derivative multiindices.
- `p_end i_end = I_30` and `i_end p_end = P_end`: **PASS**.
- inclusion/projection chain maps and commuting complementary projectors: **PASS**.
- normalized side conditions `H_alg^2=H_alg i_end=p_end H_alg=0`: **PASS**.
- `H_alg^T Omega-D Omega H_alg=0`: **0 defects**.

## Coordinate boundary

These are the local SDR maps for the certified **split** unary presentation.
The finite-order degree-zero `T/A/B` canonical shear is not part of primitive
`q1` and is not silently folded into `H_alg`.  It remains the next finite
component-jet certificate.  Represented advanced/retarded actions are a later
analytic contract.

## Claim boundary

Gate A remains **FAIL_CLOSED**.  This result does not construct Green actions,
local `D`, same-carrier `q2`, a Hadamard state, renormalized products or a QME.

## Verification

```bash
python3 quantum-weyl/classical_import/build_strict_386_local_sdr_component_maps.py --check
python3 quantum-weyl/classical_import/check_strict_386_local_sdr_component_maps.py
python3 quantum-weyl/classical_import/verify_strict_386_local_sdr_component_maps.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_local_sdr_component_maps.py -v
```
