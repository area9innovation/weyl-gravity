# Streamable Berger polarization sectors

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

Axial invariance makes the normalized scalar profile matrices diagonal.
Multiplication by `y0` or `y3` preserves the matrix index, while `y1` and
`y2` create only the first off-diagonals.  This gives at most `5d-4` input
entries for detector D0 and `4d-2` for D1 in representation dimension `d`.

In the coframe `theta_+,theta_3,theta_-`, the one-form Laplacian preserves
`q=m+s`, with coframe helicity `s=+1,0,-1`.  Every form Green matrix function
therefore splits into charge blocks of dimension at most three.  The existing
low-mode interval certificate is compatible: every conservative off-support
Taylor-remainder enclosure contains zero.  Exact Laplacian commutators pass
independently, while reversing the helicity signs breaks commutation.

Through the necessary dimension-139 capacity rail, the two detector inputs
need at most 86,736 streamed entries.  Applying all charge blocks to all
Fourier columns has an upper count 8,066,172, below one percent of the earlier
dense 852,056,100 count.

The selection rule is not a high-mode coefficient evaluation.  Convergence,
the Green-weighted operator-norm tail, full images, recoil, the tangent-cone
restriction, physical-branch interpretation, and quantum claims remain open.
