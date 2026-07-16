# Corrected raw Berger endpoint import

The quantum Lorentzian package pins classical commit `3147774e` and consumes
the corrected raw-coordinate 34-row endpoint without executing its producer.
The consumer parses the exact sparse PBW artifacts and independently verifies

\[
q_{34}^{2}=0,
\qquad
P_{34}=q_{34}W_{34}+W_{34}q_{34},
\]

the cyclicity of \(q_{34}\) and \(W_{34}\), nondegeneracy of the pairing, the
BV-canonical raw/dressed coordinate transformation, and reproduction of the
previously imported dressed unary complex.  The raw order-four principal
blocks are exactly \(I_5,I_{10},I_{10},I_5\).  The clock diagonal has no
order-four part, while the metric-to-clock extension has rank one.

The independent \(10+2\) endpoint replay also verifies that the full clock
diagonal is \(I_2\).  Naive clock elimination produces a nonzero order-six
Schur term whose top symbol is rank one and divisible by the wave symbol.  It
therefore identifies the next filtered extension problem; it is not itself a
Green construction.

The ordinary receipt check validates pinned schemas and both file-level and
internal sparse-record hashes.  The full exact PBW replay is intentionally a
separate slow check. A documentation-only provenance refresh can reuse the
validated scientific payload with `--refresh`; mathematical changes require
`--emit` and the full replay:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.raw_endpoint_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.raw_endpoint_import_certificate --replay-check
PYTHONPATH=quantum-weyl python3 -m unittest lorentzian.tests.test_raw_endpoint_import -v
```

No advanced/retarded inverse, causal support theorem, retained Green
homotopy, Hadamard state, QME, or quantum result is claimed.
