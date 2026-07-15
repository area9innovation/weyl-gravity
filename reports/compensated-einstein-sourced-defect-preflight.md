# Compensated Einstein sourced-defect preflight receipt

Date: 2026-07-15

## Established

On flat space in the constant-compensator phase, the Weyl-invariant metric
perturbation is

```text
h_hat_mn=h_mn+2(varphi/v)eta_mn.
```

Exact linear tensor algebra certifies

```text
B1=Q(G1),
Q(S)_mn=(1/2)Box S_mn-(1/6)(eta_mn Box-partial_m partial_n)tr(S).
```

For the Einstein--Weyl equation `c1 G1+2 alpha B1=T`, a solution of the
conventional same-source Einstein equation `c1 G1=T` solves the former if and
only if

```text
Q(T)=0.
```

Conservation and the compensator trace Ward identity do not imply this
condition.  The exact conserved traceless Fourier-symbol source
`p=(1,0,0,0)`, `T=diag(0,1,-1,0)` has `Q(T)=T/2!=0`.  Arbitrary same-source
Einstein truncation is therefore refuted at linearized flat level.

The gauge-covariant source-relative defect

```text
Delta=G1(h_hat)-T/c1
```

obeys

```text
(c1 I+2 alpha Q)Delta=-(2 alpha/c1)Q(T).
```

The TT reduction reproduces
`(D+M2)delta=-(D J)/M2`, so the new tensor result matches the prior reduced
source audit.

Verdict:

```text
ARBITRARY_SAME_SOURCE_EINSTEIN_TRUNCATION_REFUTED_LINEAR_FLAT
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Classification improvement

A fixed nonzero external source defines an affine solution locus, not a linear
BV subcomplex.  A genuine sourced BV theorem must include the matter fields,
ghosts when present, antifields, equations, and Diff x Weyl Ward identities.

The local dressed source

```text
T_EW=T_E+(2 alpha/c1)Q(T_E)
```

does embed a chosen Einstein response, but changes the source coupling and is
not conventional same-source equivalence.

The next gate is `COMPENSATED_QUADRATIC_BV_FREEZE`, followed by a defect chain
map and retarded/advanced propagation theorem on declared spaces.

## Claim boundary

This is a linearized flat tensor/source compatibility theorem.  The explicit
source witness is a Fourier-symbol counterexample, not a global matter
solution.  The result does not construct the compensated or matter-inclusive
BV complexes, a retarded/advanced Green complex, nonlinear closure, null
infinity, scattering, or a quantum theory.  It carries no `LORENTZIAN-CAUSAL`
claim.

## Provenance

Input base commit: `c9098557717623ade475649cd0d9e97c9b6c0fe8`.

| Artifact | SHA-256 |
|---|---|
| `compensated_einstein_sourced_defect_preflight.py` | `236b2331abc888908e2dcedce715a279bb173a37728c3326dc0c9f9b70bfd3ea` |
| `compensated_einstein_sourced_defect_preflight.schema.json` | `8045a28d64a1973386865b2016a544b406cc9e8312b6d870f1885365f2eb2354` |
| `compensated_einstein_sourced_defect_preflight.json` | `169555bea3a34d1797933804c212a4dc70b854fbda02711291ac9dc1c2c77625` |
| `test_compensated_einstein_sourced_defect_preflight.py` | `c45c8bdf26a728a1259a426b52d0618bfed76fad72ced422dc7c4d003dd8b66d` |
| `conformal-compensated-einstein-sourced-defect-preflight.md` | `5dfdeeb38b4a96824d0c0341a28a66e87a06553cf5d5d1b457bc63eba9c8413f` |
| imported `compensator_einstein_phase.json` | `b5c9f6caa05a263cdb006c33e6bbf60139139d8c30303706e073948a62e7a6b4` |
| imported `compensated_einstein_causal_subsector.json` | `ec91bb684fc0b306517de5d1bcd9763a5b69b1520fe3bd4a6b61de7e697b73b9` |
| imported `compensated_einstein_local_projectors.json` | `0a895b5f4f3f5ed3d29c8474a4174bdc9f486579b7a57cc3accc8303c602818a` |
| imported `free_bv_complex.json` | `015d829312c2d4337d6dc4a2212e4ab81a5ec699a1e8c79c76c3fe5128ce4bde` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator and test | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on schema and certificate | under 0.1 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.compensated_einstein_sourced_defect_preflight --verify bridge/certificates/compensated_einstein_sourced_defect_preflight.json` | 4.06 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 15.73 s | PASS (84 tests) |
| 2 | local-projector and causal-subsector upstream verifiers | 1.14 s | PASS |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | under 0.2 s per run | Final PASS (10/10 guards); one intermediate run failed closed during concurrent registry regeneration |

The intermediate coordination failure was not counted as a pass.  The
concurrent team completed exact regeneration before the final check; none of
its D-quotient programme files are included with this theorem.

Tier 3 was not run because this is not a freeze, release, shared-core algebra,
full BV, Lorentzian-causal, scattering, or quantum theorem promotion.
