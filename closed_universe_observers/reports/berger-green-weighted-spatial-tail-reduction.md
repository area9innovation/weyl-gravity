# Berger Green-weighted spatial-tail reduction

Status: `CERTIFIED` for the exact Maxwell operator reduction; the evaluated detector-profile tail remains `OPEN`.

Completing the exact Maxwell charge-block diagonals gives the common shift lower bound `-9/124`.  Each tridiagonal coupling is at most `(27/80)(j+1/2)`, and no row has more than two.  Gershgorin therefore gives

`Delta1 >= Lambda(j) = j^2 + 13j/40 - 1017/2480`

on every form representation `j`.  For the first omitted representation above retained `two_j=1024`, the certificate exports `Lambda(1025/2)` and the exact factors `Lambda^-N`, `N=1,...,4`.

The exact-T spatial multiplier `cos(T sqrt(Delta1))` is contractive.  So is the coderivative multiplier `delta sin(T sqrt(Delta1))/sqrt(Delta1)`, since `delta^dagger delta<=Delta1`.  Consequently the Maxwell Green step adds no `L2` tail amplification.

This is a reduction theorem, not a numerical tail.  The exact detector one-form in the Berger Haar convention and a clock-uniform enclosure of `||Delta1^N F_a(t)||_L2` remain to be evaluated.  The massive-two-form continuation, response, recoil, and tangent-cone restriction also remain open.
