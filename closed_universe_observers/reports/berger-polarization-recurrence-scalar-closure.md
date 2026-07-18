# Berger polarization-recurrence scalar closure

Status: `CERTIFIED` for the scalar companion set needed by 18 selected form entries at `two_j=1024`; the polarized intervals themselves remain `OPEN`.

For each anchor (r=128,256,384), all six detector components are selected in their exact support: diagonal entries for (y_0,y_3) and the upper first off-diagonal for (y_1,y_2). The all-finite-spin Clebsch–Gordan recurrence mechanically produces a 12-row scalar closure:

- shell `two_j=1023`: (r-1,r);
- shell `two_j=1025`: (r,r+1).

Three shell-`1025` rows are imported by content hash from the adaptive scale rail. Nine new companions are evaluated with directed correlated Jacobi integration. All 12 widths are below `0.1`; indices at or above `383` use the certified radial-only `128 x 64` refinement, while the others use `64 x 64`.

A same-index-only mutation retains only ((1023,r)) and ((1025,r)). It omits six exact recurrence neighbors—((1023,r-1)) and ((1025,r+1)) at the three anchors—and is rejected. Thus no polarized entry is constructed from a scalar set that is not closed under the certified recurrence.

This does not yet combine the rows with detector prefactors, add clock powers above (p=0), establish a complete scalar/form rail or infinite tail, evaluate Green images or recoil, restrict to the second-order cone, or activate Bridge 3. The coefficientwise mixed (epsilon_R^2kappa) unary sequencing remains unchanged.
