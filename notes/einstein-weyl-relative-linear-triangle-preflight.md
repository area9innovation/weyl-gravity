# Einstein--Weyl relative linear triangle preflight

`EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT` closes two exact parts of
the relative problem without promoting the requested all-sector theorem.

First, the already certified principal minimal-BV map has an honest mapping
cone. The cone is exact at a noncharacteristic covector. At a null covector
its cohomology dimensions in degrees `(-1,0,1,2,3)` are

```text
(0,0,4,4,0).
```

This is a BV-relative count, not a particle count.

Second, the full generic axial Fourier-polynomial operators admit the exact
off-shell factorization `L_WM = J_ax L_EM`. The row map uses only `2` and `4`
as denominators; it does not invert momentum, frequency, either dispersion
polynomial, or an exceptional harmonic factor. A polynomial splitting of the
gauge-invariant projection lifts it to the complete ungauged axial
`2 -> 6 -> 6 -> 2` complexes. All chain squares and Noether identities vanish
exactly. The degreewise map ranks are `(2,6,4,0)`: it is injective on ghosts
and fields, but not on equation and identity rows, so this sectoral result is
not advertised as a strict short exact sequence of complexes.

Together with the physical-ring and direct Lee--Wald theorems, this gives a
strict generic axial relative triangle whose solution cofiber is two copies
of the extra primary factor and whose extra current block is nonradical.

The requested `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1` is still open. The
full curved equation and identity row maps have not been constructed in the
polar, exceptional, or global sectors. Consequently a global ordinary
mapping cone is not yet a certified complex: its square is the unresolved
normalized chain defect. Cohomology must not be assigned to that defect-marked
precomplex.

Verification:

```bash
python3 -m bridge.einstein_sector.einstein_weyl_relative_linear_triangle_preflight --verify bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json
python3 bridge/einstein_sector/verify_einstein_weyl_relative_linear_triangle_preflight.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_linear_triangle_preflight
```
