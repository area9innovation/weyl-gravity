# Outgoing `R+` correlated transport: bounded first chunk

## Established

The selected repeated-spin-two outgoing Jost column was advanced through 16
panels from \(r=32\) to \(r=63/2\) in
`IvTaylor4_omega tensor dual_tau`.  At every panel the direct repeated-block
transport and the dual-number partial jet had identical coefficients and
overlapping interval enclosures after the same exponential-tail padding.

The terminal enclosure width was `1.6181993507662789`; the largest propagated
tail was `1.950214997671813e-09`.

## Throughput bottleneck

An uncheckpointed 896-panel native attempt toward \(r=4\) was stopped after
more than 360 seconds without a terminal result.  This is recorded fail closed
as a throughput/checkpointing bottleneck, not as a mathematical refusal.
Replaying all earlier panels for every continuation is not an acceptable
scoped workflow.  The next implementation gate is exact serialization of the
mixed Taylor/dual seed at \(r=63/2\), followed by independently verified
bounded chunks.

## Complementary endpoint audit

The endpoint certificate supplies the complementary factor line

\[
S_+=\frac{i}{2\omega}\,\mathrm{XI3}.
\]

Its finite formal head is available, but an all-order coupled remainder has
not been enclosed: the spin-one base column drives the carrier lift and its
intrinsic tangent simultaneously.  The same partial-jet representation should
be used for that column once the checkpoint format exists.

The endpoint shear \(K_+\) is not yet certified.  A raw leading tangent
coefficient from the selected \(R_+\) head cannot be compared directly with
the Einstein column because their printed formal powers differ.  A common
power and analytic normalization must be issued before extracting the shear.

## Does not establish

- transport from \(r=63/2\) to \(r=4\);
- the all-order complementary spin-one outgoing column;
- the endpoint \(K_+\) shear;
- \(T_+\), reflection, scattering, or flux.
