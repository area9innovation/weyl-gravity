# Polar metric-side indicial structure and the mu = 0 shearing obstruction

## Verdict

`BH2C_POLAR_METRIC_INDICIAL_MU0_REQUIRES_SHEARING`
(certificate `black_hole_programme/certificates/BH2C_POLAR_METRIC_INDICIAL.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Second split of `black-hole-asymptotic-jordan-metric-reconstruction`, and
the **metric-side** counterpart of `BH2C_SYMBOLIC_INDICIAL` (which covered
the carrier). It records one established result and one exact
obstruction, with the evidence that separates them.

## Established

The 4-dim polar h-system at infinity has leading characteristic
polynomial **λ³(λ + 2iω)** at symbolic ω, which reduces to the certified
fixture value **λ³(5λ + 6i)/5** at ω = 3/5.

Sector **μ = −2iω is semisimple** (algebraic = geometric = 1) with
Frobenius exponent σ₀ = **−4iω + 1** — exactly the value the certified
`BH2C_POLAR_FLUX_CLASS` producer feeds to `column_jets` for the
homogeneous h-jets in that sector.

## The obstruction

Sector **μ = 0 has algebraic multiplicity 3 but geometric multiplicity
1**. The kernel staircase `dim ker(A₀)^k = [1, 2, 3]` gives a **single
Jordan chain of length 3**.

When the leading matrix is non-semisimple at an eigenvalue, the Frobenius
exponents are *not* the eigenvalues of A₁ projected onto the generalized
eigenspace — that reduction presupposes diagonalizability. The
singularity is irregular there, and a **Moser/Turrittin shearing
transformation** is required, with ramified exponents admissible a
priori.

The obstruction is self-diagnosing:

| sector | naive extraction | certified σ₀ | verdict |
|---|---|---|---|
| μ = −2iω (semisimple) | −4iω + 1 | −4iω + 1 | **match** — positive control |
| μ = 0 (Jordan, chain 3) | {−3, 0, 0} | 1 | **no match** — negative control |

The same procedure reproduces certified data exactly where it is valid
and fails to reproduce it exactly where the Jordan block makes it
invalid. **The μ = 0 metric exponents are NOT established**, and the
values {−3, 0, 0} are recorded as a *refuted artifact* of an inapplicable
method — never as a result.

## What is explicitly NOT claimed

The Jordan chain does **not** explain the composed-metric log tails
reported by `BH2C_FLUX_CLASS`. The exponent matrix is itself semisimple
in every sector (log-factor count 0 throughout), consistent with
`BH2C_ASYMPTOTIC_JORDAN`'s log-free verdict for the homogeneous formal
systems. The log tails arise in the **sourced** composition, not in this
homogeneous indicial data. An earlier working hypothesis that the chain
was the log mechanism was tested and dropped; any narrative linking the
two is unsupported.

## Verification discipline

Jordan structure is read from the kernel dimension staircase
`dim ker(A₀ − μ)^k`, never inferred from the characteristic polynomial —
the work item forbids exactly that inference. The extraction method is
validated by a positive control and falsified by a negative control, so
its domain of validity is established rather than assumed. No floating
point, no `nsimplify`.

## What was NOT established

- the Moser/Turrittin shearing analysis of the μ = 0 metric sector, and
  hence the μ = 0 metric exponents (possibly ramified);
- all-orders metric reconstruction maps;
- the symbolic-frequency finite-flux power table;
- the assembled endpoint-nonselection theorem;
- general ℓ.

## Receipts

```bash
python3 black_hole_programme/bh2c_polar_metric_indicial.py          # producer (~29 s)
python3 black_hole_programme/verify_bh2c_polar_metric_indicial.py   # independent verifier (~29 s)
python3 -m pytest black_hole_programme/tests/test_bh2c_polar_metric_indicial.py -q
```

## Close-out

```text
CLOSE-OUT: SHORTFALL — the metric-side leading indicial structure is established at symbolic frequency and cross-validated against the certified fixture value, and the semisimple sector's exponent reproduces the certified producer input exactly. The mu = 0 sector carries a length-3 Jordan chain which invalidates the projection method used elsewhere; its exponents are NOT established and the exact first obstruction is the need for a Moser/Turrittin shearing analysis. That obstruction, not a result, is the deliverable for this split, per the standing constraint that the exact first obstruction is the deliverable when the main construction fails.
EVIDENCE: black_hole_programme/certificates/BH2C_POLAR_METRIC_INDICIAL.json (producer 29 s, fast rail 6/6, independent VbGeo verifier 29 s all checks passed)
```
