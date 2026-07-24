# Common-affine projective Evans contour checkpoint

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The common-affine projective rail now certifies a contiguous boundary prefix
through
\[
\frac{105}{512}
\]
of the declared 512-panel contour.  Every accepted cell uses one generator
shared by the horizon endpoint, outgoing endpoint, and the physical mismatch
\[
\Delta=q_H-q_{\rm out}+2i\omega.
\]

Parent panel `104/512` could not exclude zero in its common-affine enclosure,
so the v6a rail failed closed and did not silently lower its threshold.  The
append-only v6b repair reused the hash-linked failed parent and evaluated
exactly its two dyadic children:

\[
\begin{array}{c|c}
\text{child}&\text{certified lower bound for }|\Delta|\\
\hline
208/1024&2.4297690980833245\times10^{-5}\\
209/1024&2.4210622722228526\times10^{-5}
\end{array}
\]

Both children pass.  The next honest boundary gap begins at `105/512`.

Machine authorities:

- `black_hole_programme/phase3/axial_qnm_adaptive_dyadic_boundary_chunk_v6a/`
- `black_hole_programme/phase3/axial_qnm_adaptive_dyadic_boundary_chunk_v6b/`

This remains a boundary-prefix certificate, not a closed-contour theorem.
Boundary nonvanishing after `105/512`, an argument-principle count, a QNM
location, the local Smith selector, and an EP2 or resolvent-pole claim all
remain fail-closed.
