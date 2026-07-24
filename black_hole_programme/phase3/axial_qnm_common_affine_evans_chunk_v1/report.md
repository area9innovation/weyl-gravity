# Common-affine projective Evans contour chunk

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

A four-worker checkpointed rail certifies panels `0` through `15` of the 512-panel contour.  Every panel uses one generator shared by the horizon endpoint, outgoing endpoint, and the physical mismatch `Delta=q_H-q_out+2*I*omega`.

All 16 requested panels emit both endpoint polynomials and have a strictly positive physical-mismatch modulus lower bound.  The smallest bound is `[0.00011408738261808397838658527128712654046 +/- 5.35e-42]` on panel `15`.

This is not a closed-contour certificate.  Panels 16 through 511 and the argument-principle count were not run, so no QNM count or EP2 claim follows.
