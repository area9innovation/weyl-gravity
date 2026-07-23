# Axial future-horizon to \(r=4\) transport preflight

This isolated package validates one missing input to the Phase-3 axial global
connection.  Its declared scope is strict four-dimensional pure Weyl gravity
on Schwarzschild with \(M=1\), \(\ell=2\), and the shared affine frequency cell

\[
  \widehat\omega=M\omega\in[1/2,129/256].
\]

It imports the certified future-horizon initializer at
\(\rho=r-2=2^{-22}\), retains only the three future-regular complex columns
`XH0a`, `XH0b`, `EH0`, propagates them in the certified sheared chart
\((P,P',Q,Q',H_1,\rho F)\), and converts to the standard metric state at
\(r=4\).  The raw future-regular column selector `(0,1,2)` corresponds to
public horizon columns `(0,1,4)`.

The attempted output was a parameter-correlated \(12\times6\) real affine
enclosure.  The preflight ends fail-closed before emitting it.  Full-column
interval boxes lose the invariant regular-plane geometry, even after the
Frobenius tail is reduced by starting at \(\rho=2^{-40}\).  A one-shell graph
control confirms that the regular plane and its amplitude must be propagated
separately, but the present factor-box implementation does not certify the
required multi-shell parameter correlation.

The exact missing dependency is a validated parameter-correlated
Grassmann/Riccati flow with certified chart resets.  See `controls.json` and
`certificate.json`.  This is a numerical-method shortfall, not a singularity
or a physical result.  In particular, the package does not define an infinity
basis, connection matrix, endpoint flux, scattering channel, pole, stability
statement, or CPT metric.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_horizon_to_r4_transport_preflight.produce
```

The generated Forge rails are retained as falsification controls.  They are
expected to refuse before \(r=4\); a future successor must pass under both
native and C backends before a transport artifact can be emitted.
