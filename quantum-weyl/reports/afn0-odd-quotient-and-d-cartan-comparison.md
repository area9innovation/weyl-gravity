# Odd AFN0 quotient and local-anomaly/D-Cartan comparison

Dependency tags: `LOCAL-ALGEBRAIC`, and for the numerical even anomaly
coordinates only, `EUCLIDEAN-SPECTRAL`.

## Odd AFN0 result

Orbit-first reduction resolves the three pending parity-odd mixed
signatures without expanding the ambient 2.86-billion-graph inventory.
Each signature has 15 raw graphs and three signed curvature-symmetry orbits.
Every one of the nine orbits contains either

\[
\epsilon^{\cdots abc}R_{[abc]d}
\]

or its uncommuted covariant derivatives, and is therefore zero by the
algebraic Bianchi identity. The independently generated target-native Weyl
quotient has dimension one. Hence

\[
H^{1,4}_{\mathrm{AFN0,odd}}(s\mid d)
=\operatorname{span}\{[\omega C\widetilde C]\}
\]

within the declared four-dimensional, engineering-dimension-four,
Weyl-ghost AFN0 candidate complex. The certificate carries a complete
normalized dual witness. This does not settle the antifield-dependent or
Diff top-form sectors.

## What maps to compact D

The standard conformal-spin-two background trace anomaly has even
coordinates

\[
(c,-a)=\left(\frac{199}{30},-\frac{87}{20}\right).
\]

Restriction to a one-generator reducibility pair multiplies these
coordinates by the Weyl compensator \(\sigma_D\). On the closed vacuum
cylinder, \(D=\partial_t\) is Killing and \(\sigma_D=0\), so the direct local
bulk pullback is the zero matrix. The Minkowski dilation cross-check has
\(\sigma_D=-1\) and returns

\[
\left(-\frac{199}{30},\frac{87}{20}\right).
\]

This is not yet the quantum Cartan defect. The source is a local
ghost-number-one, form-degree-four relative class, while the target is

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q,-]).
\]

There is no canonical arrow between those complexes from grading data
alone. The missing carrier is the renormalized local Ward insertion built
from an actual \(Q_1\), \(\iota_{D,1}\), and \(\mathcal L_{D,1}\), together
with the regulated Slavnov breaking and frozen classical D action.

The resulting fail-closed conclusion is useful: the ordinary bulk trace
anomaly produces no direct local `D_compact` insertion on the vacuum
cylinder. A nonzero quantum D-Cartan defect, if one exists, must enter through
the still-unconstructed operator/Ward map or through measure,
boundary/corner, zero-mode, or antifield-completion data.

## Berger setting-specific classical input

The positive fixed-coupling Berger setting now has a stronger classical
input than the vacuum comparison originally consumed. The complete 54-row
helical `D=e_0` action, unary and contraction equivariance, and cyclicity are
independently imported. A separate conditional theorem reduces any 54-row
retarded/advanced homotopy to a retained 26-row endpoint. The endpoint Green
homotopy itself is not constructed.

Accordingly the Berger row closes the setting-specific classical D-action
carrier, but not the renormalized Ward-insertion carrier. Its quantum Cartan
status remains `NO_VERDICT`; this does not alter the vacuum-cylinder local
pullback calculation.

## Prepared analytic input contracts

The retained 26-row Green/Hadamard endpoint and the renormalized Ward
insertion now have strict content-addressed input contracts.  The former
requires both chain identities, causal support, cyclic adjointness,
`D`-equivariance, zero-mode policy, and a separately gated Hadamard ledger.
The latter accepts a sourced QME-open branch without classification and a
QME-restored branch with an explicit primitive or dual witness as required.

Both receipts are `INTERFACE_READY_PHYSICAL_INPUT_BLOCKED`.  This changes the
engineering gate from an unspecified missing carrier to a declared missing
payload; it does not construct either payload or alter `NO_VERDICT`.

## Receipts

- `local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json`
- `cartan/certificates/LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json`

Verification:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/local_bv/tests/test_h14_odd_canonical_quotient.py -v
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_local_anomaly_comparison.py -v
```

## Verification receipt

| Rail | Result |
|---|---:|
| odd quotient + basis-gap + even direct consumer | 15 pass in 14.14 s |
| local anomaly/D-Cartan comparison | 3 pass in 0.01 s |
| Euclidean coefficient direct consumer | 8 pass in 0.06 s |
| four deterministic certificate `--check` commands | pass |
| changed Python compilation and four JSON parses | pass |

The broader pre-existing Cartan suite was also sampled. Its new comparison
tests pass, while its legacy precertificate reproduction test is stale
against concurrent changes to the external commission note and classical
`D`-quotient status hashes. That certificate was not regenerated here because
the registered cross-programme contribution deliberately pins its published
historical commit. This is recorded as an unrelated affected-chain failure,
not a pass. Tier 3 was not run: neither result freezes the classical datum or
promotes a QME, residual-transfer, or Lorentzian lifecycle state.
