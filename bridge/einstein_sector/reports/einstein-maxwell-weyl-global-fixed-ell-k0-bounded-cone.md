# Global bounded cone at every fixed generic ell

The direct Bach--Maxwell tensor engine now keeps the angular eigenvalue
symbolic by using formal Legendre jets at a regular sphere point.  It gives

```text
C_A = -3 i omega_minus (3 sqrt(2 lambda)-1),
C_P = lambda^2 (2 lambda-1)/6.
```

These are the leading axial and polar `b` pivots.  Locality supplies the full
triangular chains: `(b,a,d)=(C_A,2C_A,C_A)` in axial parity and
`(C_P,3C_P,3C_P)` in polar parity.  Both bases are nonzero for every physical
`lambda=ell(ell+1)>=6`; this is a symbolic identity, not finite-ell
interpolation.

The even and odd formal jets are local normalizations of the unique
`SO(3)`-equivariant coefficient on `V_ell`; they do not identify different
physical `m` values or harmonic parities.  The jet is retained through order
8, safely beyond the fourth sphere-derivative order of the Bach--Maxwell
operator used in the contraction.

Combining that ideal with the existing every-fixed-`ell` common-moment-map
wave theorem yields the complete declared global cone.  The static branch is
`(c,d,W_x,A)`.  On any nonzero wave branch, `a=b=d=Q_e=B=0`, while
`c,W_x,A` remain spectators and the wave amplitudes satisfy
`mu_H=mu_J1=mu_J2=mu_J3=0`.

The electric exclusion is applied only after the common Hamiltonian moment
map has removed the wave contribution: the remaining homogeneous
pure-electric coefficient is independently `E11=Q_e^2/2`, while the bounded
zero-frequency homogeneous image vanishes.

The result is blockwise in one fixed `ell` at `k=0`.  Cross-`ell` products and
nonzero momentum remain open.
