# Analytic axial incoming connection theorem

The exact RW/RW/spin-one triangular filtration makes the previously
transport-defined incoming connection block analytically accessible.

This package applies the exact carrier quotient and Einstein master maps to
the frozen horizon-regular and past-null-infinity bases.  After determinant-
one triangular changes of basis, both endpoint frames contain one Jost line
for each diagonal factor:

* one spin-two Regge--Wheeler line from the Einstein metric kernel;
* one spin-two Regge--Wheeler line from the Ricci carrier;
* one spin-one Regge--Wheeler line from the carrier quotient.

For the two real short-range potentials, Wronskian conservation gives
\(\lvert A_{\rm in}\rvert^2-\lvert A_{\rm out}\rvert^2=1\).
The exact incoming connection determinant is therefore

\[
\det T_-=
-\frac{(2\omega-i)(4\omega-i)^2}{4(\omega-i)}
A_{{\rm in},2}(\omega)^2A_{{\rm in},1}(\omega),
\]

and never vanishes for real
\(\omega\in[1/2,3/4]\).

Only \(T_-\) is classified.  Reflection coefficients may vanish, and no
rank statement for the future-null-infinity block \(T_+\), complex-frequency
pole theorem, stability, CPT, or full scattering unitarity is inferred.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_incoming_connection_analytic.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_incoming_connection_analytic.tests.test_connection
```
