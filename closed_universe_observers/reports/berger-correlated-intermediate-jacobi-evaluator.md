# Correlated intermediate Jacobi evaluator

The directed tensor Darboux method now keeps both exact factors inside one
interval integrand:

```text
P_r^(0,d)(1-2X) (1-X)^(d/2)
cos(d atan2(sqrt(Z),sqrt(1-X-Z))),  d=two_j-2r.
```

The `16 x 16` audit at `two_j=4,r=1` overlaps the published low rail.  On a
`64 x 64` grid, the adjacent even/odd rows `two_j=512,r=128` and
`two_j=513,r=128` both have width below `0.1`.  Halving each axis at the first
sentinel leaves width above `0.1`, so that resolution mutation is rejected.

This certifies two intermediate external-clock `p=0` sentinels, not a
complete diagonal or odd-representation stream.  Other clock powers,
polarization, the infinite spectral tail, Green images, recoil and detector
response remain open.
