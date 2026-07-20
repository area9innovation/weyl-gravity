# Berger cutoff Volterra microlocal orientation reduction

The cutoff Hadamard problem now has one precise sufficient analytic gate.
On every compact time slab, each finite term of

\[
G_{C,\pm}
=
\sum_{n\geq 0}(-1)^n(G_{0,\pm}N)^nG_{0,\pm}
\]

is a same-sided composition of normally-hyperbolic Green kernels and local
differential kernels.  The primed wavefront relations

\[
\Gamma_\pm=\Delta\cup R_\pm
\]

are closed under these compositions.  Hence every finite term has
wavefront relation contained in \(\Gamma_\pm\).  The exact relation replay
checks both signs and rejects a mixed advanced/retarded composition.

The existing Volterra theorem proves factorial convergence in all declared
finite-slab Sobolev operator norms.  That is not, by itself, convergence in a
fixed wavefront-set class.  A sufficient missing statement is:

> The partial-sum kernels and their formal transposes converge, on every
> compact time slab and for each sign, in the normal topology of
> \(\mathcal D'_{\Gamma_\pm}\).

If this statement is proved, the full cutoff Green kernels inherit the
oriented relations, the cutoff Pauli--Jordan kernel is decomposable, the
Hermitian dilation is decomposable, and the two regular Cauchy morphisms have
the cone action required by Fewster's Theorem 5.16.  A global free seed
covariance is still a separate input.

This certificate does **not** claim that the stronger convergence already
holds.  It does not certify cutoff decomposability, cone mapping, a seed
covariance, a full-BV BRST Hadamard state, positivity, a Lorentzian QME, or a
quantum theory.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_cutoff_volterra_microlocal_orientation_reduction_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_cutoff_volterra_microlocal_orientation_reduction
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_cutoff_volterra_microlocal_orientation_reduction.py -v
```

Tier receipt:
[`BERGER_CUTOFF_VOLTERRA_MICROLOCAL_ORIENTATION_REDUCTION_V1_TIER_RECEIPT.json`](../lorentzian/receipts/BERGER_CUTOFF_VOLTERRA_MICROLOCAL_ORIENTATION_REDUCTION_V1_TIER_RECEIPT.json).
