# Berger endpoint A24 Cauchy export

The four endpoint factors already used by the classical causal theorem are now
serialized in the quantum consumer contract. Their two canonical factor-graph
companions give exact `12 x 12` first-order Cauchy blocks:

| block | sparse entries | sha256 |
| --- | ---: | --- |
| `ghost_A12` | 27 | `e32f6eb6d3f79b5cd1441e3399eab730b75eb32591a3ac334f3a4e6e1c03d393` |
| `identity_A12` | 27 | `28fde1881defd32f6f64e7bd5c1b9cb3542aaf6fddba5e458f674d0bd60f0e58` |

The factor products reconstruct the certified fourth-order ghost and identity
endpoints, both formal-adjoint relations hold, both temporal leading matrices
are two-sided invertible, and the derived generators have spatial order at
most two.

This artifact closes only the 24-component classical endpoint export.  Its
quantum consumer now assembles the global `A104` independently.  The Cauchy
BRST operator, Krein form, closed spectral realization, zero-frequency ledger
and Hadamard covariance remain downstream.
