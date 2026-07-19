# Berger recoil massive diagonal preparation

`BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION` closes the first switched massive
stage of the finite detector-selected preparation.  It derives the physical
detector center and emitter support endpoints from their exact certificates,
translates `T=t_detector_center-source_time` to the advanced coordinate
`y=t_support_right-source_time`, and multiplies the `Dhat_1` two-form source by
the normalized whole-support switch interval.

The source is then convolved with the interval-enclosed degree-two massive
sine kernel.  The corrected sparse adapter places its six matrices at their
actual powers `1,3,5,7,9,11`, not at dense series indices.  Exact beta factors
and source/kernel remainder propagation enclose the diagonal advanced-wave
image at the support-left slice for every finite mode and passive column.

The whole-support switch hull is intentionally coarse but rigorous.  The
result is not the physical massive two-form Green operator: applying
`I+mu^-2 Dhat_1 Deltahat_2`, differentiating the image for Cauchy momentum,
and constructing the positive-energy dual remain separate open gates.
