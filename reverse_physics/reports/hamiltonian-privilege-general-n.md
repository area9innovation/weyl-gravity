# General n: the separation exists at every n ≥ 2 and grows quadratically

**Certificate** `REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_GENERAL_N_V1`
**Generality** `G2_ALL_n_LINEAR_VECTOR_FIELDS`
**Lifecycle** `reverse-physics-v0 : NECESSITY_CERTIFIED`
**Closes** the `GENERAL_N_NOT_ESTABLISHED` gate left open by the G0 certificate

## What was open

The G0 certificate computed n = 1 and n = 2 only. Its central claim — marginal
information conservation is necessary but not sufficient, with a 4-dimensional
residual gap — was therefore an **n = 2 datum, not a theorem in n**. It was
consistent with the reading that n = 2 is a special small case.

## Closed forms

| | closed form | n=1 | n=2 | n=3 | n=4 |
|---|---|---|---|---|---|
| `dim sp(2n)` | `n(2n+1)` | 3 | 10 | 21 | 36 |
| `dim marginal` | `4n² − n` | 3 | 14 | 33 | 60 |
| `dim sl(2n)` | `4n² − 1` | 3 | 15 | 35 | 63 |
| codim sp in marginal | `2n(n−1)` | 0 | 4 | 12 | 24 |
| codim sp in sl | `(2n+1)(n−1)` | 0 | 5 | 14 | 27 |

## The theorem

**The separation threshold is exactly n = 2.** `codim(sp in marginal) = 2n(n−1)`
vanishes precisely at `n ∈ {0, 1}` and is strictly positive for every `n ≥ 2`. So
marginal information conservation is insufficient at *every* number of degrees of
freedom above one — the G0 result was not an artefact of the smallest interesting
case.

**The gap grows quadratically.** The assumption becomes *less* adequate, not more,
as the system gets larger. Necessity is unaffected: `sp ≤ marginal ≤ sl` holds at
every n.

## How it is derived

Seven steps, each machine-checked, and each uniform in n:

1. `Ωᵀ = −Ω` and `Ω² = −I`, by construction.
2. `A ∈ sp ⟺ ΩA` symmetric `⟺ ΩA + AᵀΩ = 0` — the two characterisations are
   compared on a spanning set, not asserted equal.
3. `S ↦ ΩS` is a linear bijection `Sym(2n) → sp(2n)`, with the explicit inverse
   `A ↦ −ΩA` verified by round trip.
4. `dim Sym(2n) = n(2n+1)`, counted over the symmetric basis.
5. The n marginal functionals have pairwise disjoint support, hence are
   independent.
6. The trace functional is nonzero, hence has rank 1.
7. Both codimension identities are polynomials in n of degree ≤ 2 on each side.
   **Agreement at 4 > 2+1 distinct points forces equality as polynomials** — this
   is a proof of the identity, not a sample of it.

Steps 1–6 are re-checked concretely for n = 1…7 so a construction error cannot
hide behind the prose.

## Rails

Rail B uses **none** of the structural argument. It builds the defining constraint
systems directly and computes brute-force exact ranks by fraction-free Bareiss for
n = 1…6, then compares. A slip in the bijection argument and a slip in the
elimination would have to coincide to survive both.

A mutation test confirms the identity check is not vacuous: an off-by-one closed
form `2n² − 2n + 1` is detected.

## What this does not establish

- **Not a formally verified induction.** The steps are machine-checked and the
  identities are proved, but the *assembly* of the steps into a derivation is
  human-authored. `FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT` is `false`. See the
  README's note on the Rocq route — this is the certificate that most obviously
  wants to be a theorem rather than a computation.
- Nothing about nonlinear carriers, infinite-dimensional carriers, or field theory.
- Still no reversal over a base theory, so still no equivalence in the
  reverse-mathematics sense.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_TORUS_G1` — whether any of this survives on
a carrier that is a manifold rather than a vector space.

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_general_n --check
PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_general_n
PYTHONPATH=. python3 -m unittest reverse_physics.tests.test_hamiltonian_privilege_general_n -v
```

## Tier receipt

- **Tier 0** — compiled; `git diff --check` clean; schema validated against draft
  2020-12 (`jsonschema` 4.19.2); certificate byte-determinism confirmed by
  `--write` then `--check`.
- **Tier 1** — generator 3.1 s, independent rail 0.11 s, 9 tests 3.3 s. Within the
  60 s fast-feedback budget. The G0 suite was re-run unchanged (21 tests, pass):
  this certificate imports G0's constraint builders, so G0 is a direct consumer.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/`
  imports or is imported by this tree; there is no transitive chain to rebuild.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
