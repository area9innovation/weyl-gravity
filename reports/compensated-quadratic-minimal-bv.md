# Compensated quadratic minimal BV receipt

Date: 2026-07-15

## Established

On the flat `v!=0`, `lambda=0` compensator chart, the exact local field map

```text
rho=varphi/v,
h_hat_mn=h_mn+2 rho eta_mn
```

has determinant `1/v` and sends the original Weyl transformation to the
algebraic doublet transformation `delta rho=-sigma`, `delta h_hat=0`.

The quadratic action factors through the invariant metric:

```text
S2=(1/2)<h_hat,K_EW h_hat>,
K_EW=c1 G1+2 alpha B1.
```

Using the exact Lorentzian symmetric-tensor Gram matrix, off-diagonal
multiplicity two, and the formal adjoint `p->-p`, the 32-coordinate minimal BV
symbol complex satisfies

```text
H R=0,
R^T G_field H=0,
q^2=0,
q(-p)^T Omega+Omega q(p)=0.
```

The four Weyl coordinates `(c_W,rho,rho*,c_W*)` admit an explicit contraction.
With inclusion `i`, homological projection `pi_cl`, and homotopy `s`,

```text
pi_cl i=1,
i pi_cl=1-q s-s q,
s^2=s i=pi_cl s=0.
```

The reduced 28-dimensional Einstein--Weyl metric--diffeomorphism minimal
complex is chain equivalent and inherits a nondegenerate pairing.

Verdict:

```text
COMPENSATED_FLAT_MINIMAL_BV_SPLITS_EW_DIFF_PLUS_WEYL_DOUBLET
```

Dependency tag: `LOCAL-ALGEBRAIC`.

## Boundary and lifecycle ledger

The integrated Yamabe bulk representative differs from the declared raw
density by

```text
-6 zeta nabla_m(phi nabla^m phi).
```

Compact support permits formal integration by parts, but the divergence is
retained for a future BFV lift.

This result is not named a complete classical import freeze.  Physical
cohomology and pairing representatives, global zero modes, the gauge-fixed
nonminimal domain, causal Green data, dynamical matter, and the sourced-defect
chain map remain open.  The next lifecycle gate is
`COMPENSATED_CLASSICAL_IMPORT_FREEZE`.

## Berger-clock coordination

The current classical certificates establish an exact positive-energy
rotating scalar clock on a compact squashed Berger background and a nonzero
internal `O(2)` clock momentum.  They do not establish the total covariant `D`
charge, support-local all-row BV retract, or causal Green complex.  Their next
gate remains `TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT`.

Those certificates use signature `(-,+,+,+)`, while this flat complex uses
`(+,-,-,-)`.  They are imported by current content hash as contextual gates;
no Berger operator or sign formula enters `K_EW`.  The Berger phase clock is
not identified with the contractible Stueckelberg coordinate `rho`.

## Claim boundary

The exact rank fixture is generic and off shell; it is not a physical,
one-particle, or residual cohomology calculation.  No result here constructs a
classical import freeze, nonminimal gauge fixing, Lorentzian propagator,
Hadamard state, matter BV complex, nonlinear closure, boundary/scattering
theory, total Berger `D` charge, or quantum theory.

## Provenance

Input base commit: `c4a1d28bab4d716a281db1c5428a83e515f6a822`.

| Artifact | SHA-256 |
|---|---|
| `compensated_quadratic_minimal_bv.py` | `be159378f57eb21f403336e1cad790f40cd3f9cdf5b6646656f8b78f9006c4f8` |
| `compensated_quadratic_minimal_bv.schema.json` | `fe5e0466d48befc3e1d15de2551c1cb7feff576955ed0d5a7fc11d9c5a43e36e` |
| `compensated_quadratic_minimal_bv.json` | `bb4cfb76211cb4de913f1df2a405c67a7b0b43ccc7122ee3fe151c490296e002` |
| `test_compensated_quadratic_minimal_bv.py` | `8bb0b371e83eaa2fb056e2763121d0a49c378d3f29532659bbd4e77bee936e2c` |
| `conformal-compensated-quadratic-minimal-bv.md` | `21faedf13ed446d0dc95b68ce080af5e56600bbc58d72eb692680c0c618d07b2` |
| imported `compensator_einstein_phase.json` | `b5c9f6caa05a263cdb006c33e6bbf60139139d8c30303706e073948a62e7a6b4` |
| imported `compensated_einstein_sourced_defect_preflight.json` | `169555bea3a34d1797933804c212a4dc70b854fbda02711291ac9dc1c2c77625` |
| imported `free_bv_complex.json` | `015d829312c2d4337d6dc4a2212e4ab81a5ec699a1e8c79c76c3fe5128ce4bde` |
| imported `POSITIVE_BERGER_CLOCK_BACKGROUND.json` | `35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687` |
| imported `BERGER_CLOCK_REDUCED_CHARGE_SEED.json` | `573381287998b6645b37fcbad0273c23c0e5cff58450cbcf7a2dc1152a8dfcd9` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator and test | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on schema and certificate | under 0.1 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.compensated_quadratic_minimal_bv --verify bridge/certificates/compensated_quadratic_minimal_bv.json` | 16.38 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 33.75 s | PASS (95 tests) |
| 2 | compensator-phase and sourced-defect upstream verifiers | 5.58 s | PASS |
| 2 | Berger background and reduced-charge tests | 1.92 s | PASS (9 tests) |
| coordination | `python3 d_quotient_classical/verify_classical_status.py --guards` | 0.07 s | PASS (12/12 guards) |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.18 s | PASS (13/13 guards) |

Tier 3 was not run because this certificate explicitly stops before the
classical freeze and does not promote shared-core, causal, release, or quantum
claims.
