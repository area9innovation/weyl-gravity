# G0: marginal information conservation is necessary but not sufficient

**Certificate** `REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_LINEAR_G0_V1`
**Generality** `G0_LINEAR_VECTOR_FIELDS_ONE_AND_TWO_DEGREES_OF_FREEDOM`
**Lifecycle** `reverse-physics-v0 : SEPARATION_CERTIFIED`
**Dependency tags** `LOCAL-ALGEBRAIC`
**Assumption tags** consumed `RP-DETERMINISTIC`, `RP-REVERSIBLE`, `RP-LINEAR-CARRIER`;
under test `RP-INFORMATION-CONSERVING`, `RP-MARGINAL-INFORMATION-CONSERVING`

## The question

Deterministic and reversible evolution is standardly said to conserve
information, and Hamiltonian structure is standardly said to follow. Reverse
physics asks which assumption actually does the work. This certificate answers
that on the smallest carrier where the question has content.

## Carrier

Linear vector fields `ẋ = Ax` on ℝ^{2n}, coordinates ordered
`(q₁, p₁, …, q_n, p_n)` so that degree of freedom *k* is literally the 2×2
diagonal block *k*. The symplectic form is `Ω = diag(J, …, J)`, `J = [[0,1],[-1,0]]`.

The degree-of-freedom split is **part of the carrier, not derived**. That matters:
the assumption under test — "each degree of freedom independently conserves
information" — is not even *statable* without it.

Three conditions on `A`:

| condition | meaning | equation |
|---|---|---|
| Hamiltonian | flow preserves Ω | `ΩA` symmetric, i.e. `A = ΩS`, `S` symmetric |
| marginal | each DOF preserves its own area | `tr A_kk = 0` for every *k* |
| Liouville | total phase-space volume preserved | `tr A = 0` |

## Result

Exact dimensions, computed by rank over ℚ:

| | n = 1 | n = 2 |
|---|---|---|
| ambient `gl(2n)` | 4 | 16 |
| Hamiltonian `sp(2n)` | **3** | **10** |
| marginal | **3** | **14** |
| Liouville `sl(2n)` | **3** | **15** |
| codim sp in Liouville | 0 | **5** |
| codim sp in marginal | 0 | **4** |
| codim marginal in Liouville | 0 | **1** |

The inclusion chain `sp ≤ marginal ≤ sl` is checked by rank, not assumed.

**At n = 1 the question is invisible.** All three spaces coincide. Any argument
that global volume preservation forces Hamiltonian structure is *correct but
uninformative* on a single degree of freedom, because there the three conditions
are the same condition. **n = 2 is the minimal separating carrier.**

**At n = 2 global information conservation is not enough.** A 5-dimensional gap
survives.

**Marginal information conservation is necessary and non-vacuous.** It is implied
by Hamiltonian structure (`sp ≤ marginal`), and it strictly cuts the Liouville
space, 15 → 14. Witness for the strictness, `global_not_marginal`:

```
A = diag(I₂, −I₂)      DOF 1 expands, DOF 2 contracts at the matching rate
```

Total volume is preserved; neither degree of freedom preserves its own area.

**But it is not sufficient.** A 4-dimensional gap survives. Witness,
`marginal_not_hamiltonian` — pure inter-DOF shear:

```
q̇₁ = q₂,  ṗ₁ = p₂,  q̇₂ = 0,  ṗ₂ = 0
```

Both diagonal blocks vanish, so *both* degrees of freedom independently conserve
their information exactly; the flow is still not symplectic.

**The residual obstruction is located exactly.** The surviving 4 dimensions are
the inter-DOF block condition `J A₁₂ = −(A₂₁)ᵀ J`. It couples distinct degrees of
freedom, so **no condition formulated per degree of freedom can close the gap** —
this is a structural statement about the *form* of the missing assumption, not
just a dimension count.

## Strengthened to finite time

The separating witness is nilpotent (`A² = 0`), so the time-1 flow map is exactly
`M = I + A` — no series, no truncation, no floating point. Exactly:

```
det M = 1                                  volume preserving
MᵀΩM − Ω = [[0,0,0,1],[0,0,−1,0],
            [0,1,0,1],[−1,0,−1,0]] ≠ 0     not symplectic
```

So the failure is not an infinitesimal artefact: the finite-time evolution map
itself conserves information, per degree of freedom and globally, and is not a
canonical transformation.

## Rails

Rail B is not a rerun. Dimensions come from explicit spanning sets rather than
constraint nullspaces; elimination is fraction-free Bareiss over ℤ rather than
Gauss–Jordan over ℚ; Hamiltonicity is tested as `AᵀΩ + ΩA = 0` rather than
"`ΩA` symmetric"; the determinant is the Leibniz permutation sum rather than
Gaussian elimination. The rails share only `carriers.py`, which computes nothing.

21 tests, including a positive control (`hamiltonian_control` really is in
`sp(4)`, so the predicates are not vacuously false) and three mutation tests that
fail if the verifier is a rubber stamp.

## What this does not establish

- Nothing about nonlinear vector fields; the dimension count has no direct analogue there.
- Nothing at n ≥ 3 or general n. **The codimension-4 insufficiency is an n = 2 datum, not a theorem in n.** This is the open gate.
- Nothing about infinite-dimensional or field-theoretic state spaces.
- **Not a reproduction, confirmation, or refutation of Carcassi–Aidala's own derivation.** This tests one candidate assumption on one carrier; it does not reconstruct their argument.
- **Not an equivalence in the reverse-mathematics sense.** There is no reversal over a base theory here — only implication and separation. `EQUIVALENCE_CERTIFIED` is unreachable with the rails available.
- That the degree-of-freedom split is itself physically forced. It is an input.
- No quantum, causal, or field-theoretic claim of any kind.

## Next gate

`REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_GENERAL_N_DOF` — prove
`dim sp = n(2n+1)`, `dim marginal = 4n² − n`, `dim sl = 4n² − 1` for all *n*, so
the codimension `2n² − 2n` becomes a statement in *n* rather than a pair of data
points.

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_linear_g0 --check
PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_linear_g0
PYTHONPATH=. python3 -m unittest reverse_physics.tests.test_hamiltonian_privilege_linear_g0 -v
```

## Tier receipt

- **Tier 0** — compiled all changed sources; `git diff --check` clean; certificate schema validated against draft 2020-12 (`jsonschema` 4.19.2); certificate byte-determinism confirmed by a `--write` then `--check` cycle.
- **Tier 1** — generator, independent rail, and the 21-test suite: all pass, 0.23 s wall for the three commands together.
- **Work item** — `planning/work-items/reverse-physics-hamiltonian-privilege-necessity.json` validated against the real `work-v0` schema: `sfc import-program planning/work-items` reports 1313 nodes, **0 invalid items, 0 malformed events**, and `sfc work-package` renders the brief.
- **Tier 2 — not run, and not required.** This tree has no shared mathematical input with any existing certificate chain: it imports nothing outside `reverse_physics/` and the standard library, and no existing artifact imports it. There is no transitive chain to rebuild.
- **Tier 3 — not run, and not required.** No freeze, tag, paper-theorem promotion, lifecycle promotion, or change to shared core algebra.
