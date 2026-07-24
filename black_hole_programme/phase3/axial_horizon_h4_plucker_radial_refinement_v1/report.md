# H4 shell-4/segment-3 radial refinement

## Scope

This bounded successor preserves the exact q00 half-cell split and the
certified shell-4/segment-2 boundary state.  Only shell 4, segment 3 is
re-panelled: first 64 panels (2x), then 128 panels (4x) because the 2x
cover refused.  Each panel tries an existing raw Pluecker coordinate first
and falls back to the existing midpoint-Hermitian functional only after a
typed code-32 refusal.

The independent verifier requires all 19 preceding segment heartbeats to
match the upstream replay byte for byte.

## Result

Neither refinement certifies a nonzero witness on both frequency halves.
All four attempts stop at the same physical left boundary
`725/134217728`: panel 213 at 2x and panel 426 at 4x.  The 4x interval is
narrower radially, but the correlated functional still strictly straddles
zero.

| depth | child | frequency cell | radial width | refusal panel | functional enclosure | enclosure width | refused radial panel |
|---:|---:|---|---|---:|---|---:|---|
| 2x | 0 | `1/2..4097/8192` | `1/134217728` | 213 | `[-3.6338608221874176e-07, 3.6340097815461235e-07]` | `7.267870603733542e-07` | `725/134217728..363/67108864` |
| 2x | 1 | `4097/8192..2049/4096` | `1/134217728` | 213 | `[-3.644630296787931e-07, 3.6447793139035106e-07]` | `7.289409610691441e-07` | `725/134217728..363/67108864` |
| 4x | 0 | `1/2..4097/8192` | `1/268435456` | 426 | `[-3.611012750903941e-07, 3.611161710261836e-07]` | `7.222174461165777e-07` | `725/134217728..1451/268435456` |
| 4x | 1 | `4097/8192..2049/4096` | `1/268435456` | 426 | `[-3.621710864451173e-07, 3.621859881565942e-07]` | `7.243570746017115e-07` | `725/134217728..1451/268435456` |

## Interpretation

This is a certified conditioning obstruction, not a rank-loss theorem.
Radial subdivision by factors two and four does not resolve the q00
shell-4/segment-3 chart with the current interval-Taylor remainder model.
The nearly unchanged functional widths show that panel size is no longer
the dominant enclosure error at the common refusal location.

The result does not establish transport beyond this boundary, a complete
horizon map, canonical endpoint amplitudes, or a scattering theorem.
