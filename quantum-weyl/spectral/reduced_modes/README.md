# Reduced-mode spectral bootstrap

Dependency tag: `REDUCED-MODE`

This directory starts Branch C without evaluating a determinant. The
bookkeeping executable imports three hashed, exact upstream certificates and
independently checks:

- the parity-complete `E/A/L` multiplicity at every compact energy;
- the `E >= 2`, `A >= 3`, and `L >= 4` thresholds;
- exclusion of the energy-two transverse-vector Killing band from the metric
  `A` branch;
- the unsigned and signed rational characters;
- the reduced-action residue formulae and `+E,-A,-L` signs.

Run:

```bash
python3 quantum-weyl/spectral/reduced_modes/bookkeeping.py --check
```

To regenerate the deterministic detailed ledger and repository-wide result
envelope:

```bash
python3 quantum-weyl/spectral/reduced_modes/bookkeeping.py --emit
```

The detailed receipt is
`certificates/eal_branch_ledger.json`; the repository-wide result envelope is
`../../../certificates/REDUCED_MODE_SPECTRAL_BOOTSTRAP.json` and conforms to
the common quantum result schema.

The result is bookkeeping only. Kinetic eigenvalues, complete ghost and
auxiliary multiplicities, determinant phases, measure and contour choices,
regularization, analytic extrapolation, and one-loop coefficients remain
`NOT_COMPUTED`. It makes no Euclidean ellipticity, Lorentzian causal, QME,
anomaly-cancellation, or gauge-fixing-independence claim.
