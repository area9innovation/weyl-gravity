# All-m axial ell=2 second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For non-axisymmetric axial `ell=2` data,

```text
V_2 tensor V_2 = V_0 + V_1 + V_2 + V_3 + V_4.
```

Parity sends even `L` to polar outputs and odd `L` to axial outputs.  The
axisymmetric calculation omitted `L=1,3`; both are now closed.

At zero frequency:

* the `L=0` source is fixed for all `m` by Schur's lemma and equals the
  Hamiltonian moment-map matrix, so `H=0` removes it;
* the physical `L=1` cokernel is exactly the rotation triplet, so
  `J_1=J_2=J_3=0` removes it;
* polar `L=2,4` and axial `L=3` are invertible.

For all nine nonzero self/cross frequency types, exact minimal-polynomial
witnesses show that axial `L=1` misses the twist, the new `omega^2=4/3`
fourth-order primary, and the standard `omega^2=4` shell.  Axial `L=3`
misses both generic `p` and `q` shells.  The inherited polar `L=2,4` blocks
are likewise nonresonant.

Therefore every finite real axial `ell=2,k=0` tangent with all `m`, both
extra polarizations, and complete `H=J_i=0` balance has a full second-order
correction.  Polar input parity, symbolic `ell`, opposite momenta, and
all-orders integration remain open.
