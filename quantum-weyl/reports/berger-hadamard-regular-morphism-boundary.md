# Berger Hadamard regular-morphism boundary

The direct causal Hadamard route is now narrower than the original six-item
microlocal ledger suggested.  Every map in the exact (A_{10}leftrightarrow
C_{20}) graph contraction is a differential operator of order at most two.
Consequently these maps do not enlarge wavefront sets once their input
distribution exists.  The two ghost-wave local Hadamard parametrices are
already present as separate direct-sum factors and do not require the metric
Volterra transport.  These statements close only the finite graph and local
ghost bookkeeping obligations.

The full companion kernel remains open.  The certified Volterra maps act on
finite-slab solution and source Sobolev spaces.  They are not compact-to-
compact maps on test sections and no distribution-kernel wavefront estimate
has been proved for their infinite series.  Therefore they do not yet satisfy
the regular Green-hyperbolic morphism hypotheses needed to pull back a
Hadamard state.

The primary-source comparison fixes the exact boundary:

- [Dappiaggi--Drago](https://arxiv.org/abs/1506.09122) treats normally
  hyperbolic operators differing by a smooth order-zero potential.  The
  Berger companion has an order-two triangular principal coupling.
- [Moretti--Murro--Volpe](https://arxiv.org/abs/2210.09278) supplies the useful
  response-map pattern for Proca fields, including a kernel wavefront estimate
  and propagation from a Cauchy slab, but is not a theorem for this companion.
- [Fewster, Theorem 5.16](https://arxiv.org/abs/2503.12537) gives the general
  transfer mechanism once there is a regular GreenHyp morphism with compact
  support control, a continuous transpose, no one-sided zero covectors in its
  kernel, and the required cone map.  Theorem 5.4(c) then propagates the
  Hadamard property from a Cauchy slab.

The minimal analytic import is therefore a temporal-cutoff companion family:

```text
BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY
  smooth nonstationary coefficients on the compact transition slab
  typed advanced/retarded Green operators for every cutoff
  causal support and formal-adjoint reversal
  finite-slab Sobolev estimates
  no stationarity hypothesis
```

From it the quantum lane must construct the compact-support response map and
verify Fewster regularity and cone mapping.  Independently, a global seed
covariance with an explicit BV/Krein and physical-positivity policy is still
needed.  The local base parametrices alone are not that covariance.

Passing both gates would produce a companion Hadamard two-point distribution.
The BRST Ward identity, physical-cohomology positivity, and the already-ready
26-to-54 contractible lift remain subsequent checks.  No Hadamard state or
quantum lifecycle promotion is made here.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_hadamard_regular_morphism_boundary_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_hadamard_regular_morphism_boundary
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_hadamard_regular_morphism_boundary.py -v
```

Tier receipt:
[`BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY_V1_TIER_RECEIPT.json`](../lorentzian/receipts/BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY_V1_TIER_RECEIPT.json).
