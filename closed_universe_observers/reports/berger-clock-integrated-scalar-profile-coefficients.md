# Clock-integrated scalar profile coefficients

Writing the normalized detector clock coordinate as

```text
s=(Theta-Theta_a)/(1/64),
```

the certified rate `dTheta/dt=3/4` gives `t-t_a=s/48`.  The rod amplitude is
therefore `cos(sqrt(58)s/288)`.  Every spatial moment of degree `2k` acquires
the same clock factor `sec(sqrt(58)s/288)^(2k)`.

The product of this secant factor with the flat bump is strictly decreasing
on `[0,1]` for every required `k=0,...,6`.  Directed-rounding dyadic Darboux
sums therefore give validated normalized clock averages.  Combining them
with the published radial moment reduction produces clock-integrated scalar
Fourier amplitudes through `two_j=4`; exact Hopf phases distinguish the two
detector centers.

This does not yet apply the detector polarization, coderivative, or
form-valued Peter--Weyl blocks.  It also does not control modes above the
audited range or provide the infinite spectral tail needed for full Green
images.
