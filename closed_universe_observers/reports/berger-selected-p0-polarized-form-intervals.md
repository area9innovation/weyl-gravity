# Berger selected (p=0) polarized form intervals

Status: `CERTIFIED` for 18 selected detector-component intervals at form `two_j=1024`; higher clock powers and complete form/infinite rails remain `OPEN`.

The 12 recurrence-closed scalar rows are combined with the exact Clebsch–Gordan coefficients and detector-specific coordinate prefactors. The common pointwise factor `a(t)=cos(lambda s)` is then applied with its certified range `82915/82944 <= a(t) <= 1`. The resulting complex intervals are uniform over the full normalized clock support. At each anchor (r=128,256,384), this constructs all six declared detector components: diagonal (y_0,y_3) entries and upper-first-off-diagonal (y_1,y_2) entries for `D0` and `D1`.

All 54 scalar-term applications are serialized. Every maximum real/imaginary interval width is below `0.1`; the widest selected family remains below `0.099`. Deleting one scalar term and dropping the common external clock factor are rejected.

This is the first actual high-scale polarized input rail, but it is deliberately selected and (p=0) only. It does not provide powers (p=2,ldots,28), every form row, a Sobolev/infinite-mode tail, Maxwell or massive Green images, detector response, recoil, tangent-cone restriction or active Bridge 3. The coefficientwise mixed (epsilon_R^2kappa) apparatus sequencing remains unchanged.
