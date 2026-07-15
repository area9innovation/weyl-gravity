# Einstein-defect asymptotics receipt

Date: 2026-07-15

## Established

For each flat Cartesian TT scalar amplitude, the exact reduced defect field

```text
chi=Box phi=-2 Ric_1
```

turns the two equations into

```text
Einstein: chi=0,
Weyl:     Box chi=0.
```

For the formal retarded series

```text
phi=sum_(j>=0) r^(-p-j)f_jY_L,
chi=sum_(j>=0) r^(-p-j-1)g_jY_L,
```

the generated coefficient map is

```text
g_j=2(p+j-1)d_u f_j
    +[(p+j-1)(p+j-2)-L]f_(j-1).
```

The certificate proves algebraically that applying the wave recursion to
these `g_j` reproduces every biwave coefficient.  A separate direct check
extracts `chi` and `Box chi` from six-term radial series at `p=0,1,2`.

The branch data are:

```text
p=0: g_0=-2d_u f_0, g_1=-Lf_0,

p=1: g_0=0,
     g_1=kappa=2d_u f_1-Lf_0,
     g_2=rho=4d_u f_2+(2-L)f_1.
```

Their first propagation rows are

```text
4d_u kappa=0,
6d_u rho+(6-L)kappa=0.
```

Hence `kappa=0` implies only that `rho` is `u`-independent.  It does not
imply `rho=0`, and therefore does not isolate the Einstein sector.  The
versioned certificate makes this a required false claim flag.

This is a `REDUCED-MODE` result.  The full tensor expansion, characteristic
data classification, causal zero-defect theorem, physical status of the
defect coefficients, and scattering equivalence all remain false and
fail-closed.

## Downstream effect

The asymptotically flat bootstrap imports the new certificate by SHA-256.
It now records Einstein as `chi=0` and rejects each of these as individually
sufficient:

- `p=1` falloff;
- fixed unphysical boundary metric;
- `kappa=0`.

`AF-E4` remains `PARTIAL`: the correct zero-defect target is known, but its
causal preservation on admissible null-infinity spaces is open.  `AF-E8`
remains `PARTIAL`: the reduced `p=0`, `kappa`, and `rho` defect data are known,
while tensor, soft, Coulombic, and corner data remain open.

## Provenance

Input base commit: `efa5708d91b235c5c2cfe056c536f2194a2d23dc`.

| Artifact | SHA-256 |
|---|---|
| `flat_tt_bach_operator.json` | `a4aa604755c3a6adecdd747e0411d555b82d8bcdfd483c451c7bdb42ee920242` |
| `bondi_bach_indicial.json` | `0c66fcf5f86f009769c652ed5aac8bcd117f9153c1e5d1d7d64f6ea53a617eee` |
| `einstein_defect_asymptotics.py` | `48cdc1c78a942860c5f4fca85c7e686841a2b55ac5cfe4902fb300f469ee2b46` |
| `einstein_defect_asymptotics.schema.json` | `66aafeaffc378200302aa5671384a6e8bd0946eb3c4dddb5529576d586e1435c` |
| `einstein_defect_asymptotics.json` | `75780eb8b9800ff035897b725d67a099d658c0a7779c2ecd878bf730725639a0` |
| `asymptotic_bootstrap.py` | `723518b1023109d15a5c5291598d4f5a8376fdcf16bdb3ea7112ec596a7dbda4` |
| `asymptotic_bootstrap.schema.json` | `4509ac0ddbca1bd372cd36924b43d7965e6f22abb4cb7b41b360e95b46fdf2e2` |
| `asymptotically_flat_einstein_bootstrap.json` | `26d3b88e0fcf9971e3a928b2860b3e83c7b40e4dffe714d207c2fae2b951502d` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on both changed generators and their tests | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on both changed schemas and certificates | 0.14 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.einstein_defect_asymptotics --verify bridge/certificates/einstein_defect_asymptotics.json` | 1.33 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.39 s | PASS |
| 1 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 8.86 s | PASS (32 tests) |

The tests cover the exact coefficient factorization, direct finite-series
extraction, `p=0`, `kappa`, and `rho` identities, schema and provenance
guards, the downstream import boundary, and rejection of forged
`kappa`-sufficiency, causal, tensor, and scattering promotions.

Tier 2 was limited to the direct downstream asymptotic certificate.  The
content-addressed flat TT and indicial inputs were unchanged and were checked
by hash.  Tier 3 was not run because no freeze, release, shared core-algebra
change, paper theorem, or `LORENTZIAN-CAUSAL` promotion occurred.

## Unresolved fields

- full tensor Bondi expansion of `chi_mn` and every Bach constraint;
- admissible radiative, soft, Coulombic, and corner data for `chi_mn`;
- residual Diff x Weyl action and surface charges on defect data;
- a retarded/advanced or characteristic uniqueness theorem forcing `chi=0`;
- symplectic comparison with the Einstein radiative phase space;
- nonlinear propagation of the Einstein-defect constraint.

## Concurrent work

Unrelated publication restructuring, quantum reports, medical data, workflow,
and backgammon changes were present in the shared tree.  They were neither
staged nor modified by this work.
