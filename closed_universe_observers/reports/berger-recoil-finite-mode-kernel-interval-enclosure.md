# Berger finite mode-kernel interval enclosure

## Result

`BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE` turns one block of the
exact finite kernel payload into outward rational interval matrices.  It
supports every Maxwell scalar/one-form and massive two-form block through
`two_j=4`, with a runtime-declared strictly positive rational mass-squared
interval for the massive family.

For (A=\Delta_p+\mu^2), the callable exports the first six matrices in

\[
 \frac{\sin(\sqrt A\,\tau)}{\sqrt A}
 =\sum_{n=0}^{5}\frac{(-1)^n A^n\tau^{2n+1}}{(2n+1)!}+R_5(\tau).
\]

All rational and square-root entries are enclosed without floating point.
Writing (x=\lVert A\rVert_\infty L^2), the tail uses the geometric majorant

\[
 \sup_{0\leq\tau\leq L}\lVert R_N(\tau)\rVert_\infty
 \leq \frac{Lx^{N+1}}{(2N+3)!}
 \left(1-\frac{x}{(2N+4)(2N+5)}\right)^{-1}.
\]

The call fails closed if this ratio is not below one.  The exact Maxwell
zero mode returns the identity coefficient at `tau_power=1` and zero tail;
the massive `two_j=0`, degree-one fixture on `mu_squared in [1,2]` has
operator norm upper bound `58/9`.

## Boundary

This is a finite-mode, runtime-parametric kernel enclosure.  It does not
select physical masses, multiply the exact clock switches, import detector
profile intervals, contract spacetime form blocks, or evaluate any
`I_abc`.  The complete recoil stream, second-order cone, physical-branch
bridge and quantum observer remain open.

## Verification

```text
python3 -m pytest -q closed_universe_observers/tests/test_berger_recoil_finite_mode_kernel_interval_enclosure.py
PYTHONPATH=. python3 closed_universe_observers/verify_berger_recoil_finite_mode_kernel_interval_enclosure.py
```
