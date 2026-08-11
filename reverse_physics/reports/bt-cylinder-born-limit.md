# BT thermodynamic cylinder Born limit

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The squeezed finite-volume projectors need not converge in positive trace norm
for conditional probabilities of finitely supported paired processes to have a
thermodynamic limit.  Each unused squeezed spectator corner has Krein trace
one.  Tensoring it onto a local process therefore changes neither numerator nor
denominator of the conditional generalized-Born weight.

An exact weak-ghost fixture gives weights

\[
 9/25,\qquad16/25,\qquad0.
\]

They remain nonnegative and sum to one for every spectator volume.  At the
same time, the positive trace norm of the representing corner grows as
\((4/3)^N\).  Thus the directed cylinder functional exists precisely where a
normal density-operator limit does not.

Because the completed signed parent trace vanishes pointwise before momentum
integration, spectator extension multiplies zero by one.  Its thermodynamic
pair-cylinder coefficient is therefore exactly zero and regulator independent
on this net.

This is not yet the complete physical result.  The certificate does not prove
that the inclusive LSZ momentum-window projector is affiliated with the
pair-cylinder completion, does not construct a spacetime-local AQFT state, and
does not supply the dynamical \(p=0\) module or higher composite orders.

Verification uses the producer, an independent exact Kronecker-product
verifier, and seven tests including five decisive claim/data mutations.  All
commands ran sequentially under `ulimit -v 500000`: certificate generation
and producer checks took 0.12 s each (21/21, 20,828 KB peak RSS), the verifier
took 0.23 s (9/9, 30,028 KB), and the tests took 1.00 s (7/7, 30,272 KB).
Papers V and VI compiled twice; their final passes took 0.48 s and 0.50 s with
at most 51,016 KB peak RSS.  Tier 3 was not run because no all-order,
inclusive-LSZ, freeze, release, or physical theorem is promoted.  The event is
an append-only manual fallback with a reproduced FNV id; no coordinator pass
is claimed.
