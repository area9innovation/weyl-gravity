# Generic ghost n=3 symmetric-point simplex integration

## Result

The exact five-carrier Feynman-simplex projection of the three-Ricci Endo
ghost triangle is now integrated at the normalized nonexceptional Euclidean
point

\[
x_1=x_2=x_3=1.
\]

Write

\[
e_2=\alpha_0\alpha_1+\alpha_1\alpha_2+\alpha_2\alpha_0,
\qquad
e_3=\alpha_0\alpha_1\alpha_2,
\]

and define the scalar triangle master

\[
J_\triangle=\int_{\Delta_2}\frac{d^2\alpha}{e_2}
=\frac{4}{\sqrt3}\operatorname{Cl}_2\!\left(\frac\pi3\right)
=2.343907238689458890601562288872277\ldots .
\]

The eleven exact integrated quotient coordinates are

\[
\begin{aligned}
I_{10,123}&=-\frac{8}{2187}(592J_\triangle+55),\\
I_{24,123}=I_{24,213}=I_{24,312}
 &=\frac{32}{6561}(7J_\triangle-17),\\
I_{25,123}=I_{25,213}=I_{25,312}
 &=\frac{20}{6561}(88J_\triangle-179),\\
I_{28,123}=I_{28,132}=I_{28,231}&=0,\\
I_{29,123}&=-\frac{8}{6561}(62J_\triangle-145).
\end{aligned}
\]

The upstream `W=-2 Ric` substitution and third-order trace-log multiplier
`-8/3` are already included. The common loop prefactor `(4*pi)^-2` remains
excluded.

## Exact reduction

At equal box invariants the simplex measure and denominator are invariant
under all permutations of the three Feynman parameters. Averaging each raw
numerator therefore preserves its integral. The eleven averages reduce to

\[
\begin{aligned}
N_{10}^{\rm sym}
 &=-\frac4{81}e_2(3e_2^3-2e_2^2e_3+45e_2^2-7e_3^2),\\
N_{24}^{\rm sym}
 &=-\frac8{243}e_2e_3(e_2^2+e_2-7e_3),\\
N_{25}^{\rm sym}
 &=\frac8{243}e_2e_3(2e_2^2+21e_2+7e_3),\\
N_{28}^{\rm sym}&=0,\\
N_{29}^{\rm sym}&=-\frac{16}{27}e_3^3.
\end{aligned}
\]

Only four moments beyond the area and `J_triangle` occur. Exact rational
vector fields on the simplex give

\[
\begin{aligned}
\int\frac{e_3}{e_2}
 &=\frac{11-4J_\triangle}{54},&
\int\frac{e_3}{e_2^2}
 &=\frac{J_\triangle-2}{3},\\
\int\frac{e_3^2}{e_2^3}
 &=\frac{10J_\triangle-23}{54},&
\int\frac{e_3^3}{e_2^4}
 &=\frac{62J_\triangle-145}{486}.
\end{aligned}
\]

For each identity the certificate stores a polynomial `P`, the rational
vector field

```text
X1 = alpha1*alpha0*P(alpha1,alpha2)/e2^k
X2 = alpha2*alpha0*P(alpha2,alpha1)/e2^k
```

and verifies its divergence exactly. The explicit coordinate factors kill
the normal flux on the three open edges. Stored Taylor orders at all three
vertices prove that the punctured-corner fluxes vanish as well. Thus these
are integration-by-parts certificates with a checked boundary disposition,
not numerical fits.

The scalar master is independently reduced by splitting the simplex into
the three regions where one barycentric coordinate is largest and mapping
one region to the unit square. Integrating one square coordinate gives

\[
3\int_0^1
\frac{\log\!\frac{(1+x)(1+2x)}{x(x+2)}}{x^2+x+1}\,dx.
\]

With `x=(sqrt(3) tan(phi)-1)/2`, the four logarithms become four sine
integrals on adjacent sixths of the circle, yielding
`4 Cl2(pi/3)/sqrt(3)`.

## Independent replay and branch guard

The verifier reconstructs every symmetric numerator from the upstream 837
term parametric projection, checks all four rational divergence identities,
checks the open-edge and corner-flux conditions, and separately quadratures
the smooth sector representation of each master. It also compares the
one-dimensional scalar-triangle integral with the Clausen value.

This matters because direct iterated symbolic integration of the unsymmetrized
rational functions can choose inconsistent logarithm branches at the moving
simplex endpoint. That route produces attractive but false rational/logarithmic
answers. It is deliberately absent from the certificate path.

## Claim boundary

This is an `EUCLIDEAN-SPECTRAL` coefficient-bearing fixture for the `n=3`
ghost block at one normalized symmetric point. It does not compute:

- the generic functions of `(x1,x2,x3)`;
- the complete generic ghost determinant;
- the generic physical fourth-order Hessian;
- the complete five repository form factors or their combined coefficients;
- the parity-odd derivative sector;
- complete `Gamma1`, complete `Q1`, residual transfer, or a QME disposition;
- any Lorentzian, Hadamard, particle, positivity, scattering, or unitarity
  theorem.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n3_symmetric_point_simplex_integration
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_ghost_n3_symmetric_point_simplex_integration
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n3_symmetric_point_simplex_integration --check
```
