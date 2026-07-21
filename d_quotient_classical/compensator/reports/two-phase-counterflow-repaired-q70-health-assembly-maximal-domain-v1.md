# Repaired-q70 health assembly: maximal certified domain

## Result

The exact repaired-q70 block ledgers certify a complete physical-health
quotient on precisely the imported isotypes

\[
j=0,\quad j=\tfrac12,\quad j=1,
\]

with every left weight \(m\), every right weight \(k\), and all 70 rows.
They do not certify the physical quotient for \(j\ge\tfrac32\).  The correct
assembly is therefore a typed maximal-certified-domain theorem, not an
extrapolated all-isotype spectrum.

The terminal state is

```text
OBSTRUCTED_LINEAR_PHYSICAL_HEALTH_WITH_TYPED_HIGHER_J_CENSUS_SHORTFALL
```

This has two independent truth values:

- `health_obstruction_complete = true`: every computed isotype already has
  a non-gauge, nonradical physical instability;
- `all_isotype_spectral_census_complete = false`: higher-isotype physical
  quotients and spectra were never computed by the generic prerequisite.

## Immutable inputs

| Role | SHA-256 |
| --- | --- |
| repaired q70 parent | `3f41cb5258f0883b217c9343e037074faf841728f29e03c306f101487411d2cf` |
| repaired q70 payload | `c59b1a74aced082155db3446c40aa1b14e3982e66670a3c097539b25d5d5c938` |
| first generic health certificate | `d78fa16e9772924ded1b8262f33e3989a9e94acd01891257309bc07f7f7f282c` |
| first generic health payload | `43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797` |
| low-j/stabilizer certificate | `fa0d158301a1bf2076d7d7622866f4545d6a15370ec576ddcbe120837224d364` |
| low-j/stabilizer payload | `291071bab2494a4b4bdb21702be1bf28d672a2a6157b588003743aec5d0b5b5e` |

No oracle field from a generated output is consumed.

## Exact block ledger

| \(j\) | all-\(m,k\) q70 dimension | retained dimension | physical dimension | unstable physical sector |
| ---: | ---: | ---: | ---: | --- |
| \(0\) | 70 | 26 | 7 | real exponential pair; inertia `(3,3,0)` |
| \(1/2\) | 280 | 104 | 28 | Hamiltonian--Hopf quartet; inertia `(4,4,0)` per fixed-\(m\) reality sector |
| \(1\) | 630 | 234 | 63 | two complex-frequency sectors; inertias `(4,4,0)` and `(8,12,0)` |
| **total** | **980** | **364** | **98** | — |

The dimensions follow independently from \(70(2j+1)^2\),
\(26(2j+1)^2\), and \(7(2j+1)^2\).  Every displayed characteristic sector
has zero pairing radical.  The low-j theorem accounts for the only spatial
stabilizer exceptions, \(2j=0,2\), while the generic theorem supplies the
first nonstabilizer block, \(2j=1\).

## Cross-isotype proof and remaining carrier

Peter--Weyl spins are indexed by the nonnegative integer \(n=2j\).  The
certified sources cover \(n=0,1,2\).  For every \(n\ge0\), exactly one of
\(n\le2\) or \(n\ge3\) holds, so the disjoint remaining carrier is exactly

```text
two_j >= 3, all m=-j,...,+j, all k=-j,...,+j.
```

On it, the 70-row causal parent is imported, but the physical quotient,
characteristic spectrum and pairing inertia are all `NO_CERTIFIED_MAP`.
This is not a missing stabilizer theorem: the stabilizer census is complete.
It is a missing higher-isotype physical quotient.

## Charge and generator disposition

- On the unrestricted global action--angle carrier, \(R_{\rm rel}\) is a
  charged global symmetry, raw \(D\) is Hamiltonian with
  \(H_D=\Omega Q_{\rm rel}\), and
  \(K=D-\Omega R_{\rm rel}\) is the background stabilizer.
- The derived fixed-charge level set followed by the \(R_{\rm rel}\)
  quotient removes this entire two-dimensional clock carrier; \(D\) is null
  there.
- The \(j=0,1\) zero-frequency classes are spatial Killing reducibilities,
  with \(D=R_{\rm rel}=K=0\) on their specialization.
- The repaired diagonal-\(U(1)\) sector is contractible and has zero local
  Gauss charge.
- Every certified nonzero-frequency instability survives fixed charge.  The
  prerequisites do not export separate \(R_{\rm rel}\) and \(K\) matrices on
  the \(j=0,1\) physical quotient bases, so the assembly does not invent
  them.

## Claim boundary

Dependency tags are `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, and
`LORENTZIAN-CAUSAL`.  The result establishes a linear physical-health
obstruction on the selected fixed-action Berger theory and a support-local
causal parent on the remaining carrier.  It does not establish a higher-j
spectrum, nonlinear instability, finite-time blow-up, observer map,
Hadamard state, anomaly/QME result, particle interpretation, positive state
space, or unitarity.

## Replay

```bash
python3 d_quotient_classical/compensator/two_phase_counterflow_repaired_q70_health_assembly.py --check
python3 d_quotient_classical/compensator/verify_two_phase_counterflow_repaired_q70_health_assembly.py
python3 -m pytest -q d_quotient_classical/compensator/tests/test_two_phase_counterflow_repaired_q70_health_assembly.py
python3 d_quotient_classical/atlas/generate_two_phase_counterflow_repaired_q70_health_assembly_atlas_fragment.py --check
python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-repaired-q70-health-assembly-maximal-domain-fragment-v1.json
```
