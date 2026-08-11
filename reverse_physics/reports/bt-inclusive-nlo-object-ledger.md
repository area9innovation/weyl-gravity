# BT inclusive NLO object ledger

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The field/projector pushforward \(R_t P R_t^\dagger\) and the physical
scattering block \(P_{\rm out}(S-1)P_{\rm in}\) are different operators.  The
complete public order-\(\lambda\) \(R_t\) calculation has exact zero raised
trace.  That remains a valid finite-mode Eq. (19) result, but it cannot replace
the independently computed five-point real-emission process.

In common absolute units, with the factor
\(\lambda^6\log(c)/(\pi^4s)\) suppressed, the exact ledger is

\[
 B=\frac{3}{32},\qquad
 \Delta_{\rm real,pair}=\frac1{512},\qquad
 \Delta_{\rm real,total}=\frac3{512}.
\]

Dividing by \(B\) gives \(1/48\) per unordered pair and \(1/16\) after all
three pairs are summed.  Every axis-compatible virtual daughter mass-ratio
response is zero.  The completed \(R_t\) pushforward and its covariant squeeze
also have zero response, but those Eq. (19) objects are not physical S-matrix
summands.  Therefore the typed physical ledger is

\[
 \Delta_{\rm available}
 =\Delta_{\rm real}+\Delta_{\rm virtual}
 =\frac3{512}+0=\frac3{512}\ne0.
\]

A separately constructed physical hard or dressed endpoint object with response
\(-3/512\) is required for cancellation.  The Callan--Symanzik hard scale log
has zero daughter mass-ratio response and is not that object.

This certificate supersedes the object identification in
`REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1`.  It retains that
certificate's exact orthogonal-block lemma, signed \(R_t\) trace calculation,
squeeze similarity, and finite detector/cylinder limits.  It rejects only the
step that called the \(R_t\) kernel the physical S-matrix transition kernel.
Consequently the physical real response is nonzero, the available cancellation
is obstructed, and a regulator-independent complete NLO probability remains
`NOT_ESTABLISHED`.

Verification is by an exact rational producer, an independent verifier that
reads the source certificates as typed objects, and mutation tests that alter
the real coefficient, normalization, \(R_t\) response, operator identity,
correction status, and claim boundary.  Commands were run sequentially under
`ulimit -v 500000` except Git itself.  Certificate generation and the 16/16
producer passed in 0.04 s and 0.03 s (20,392 KB and 20,424 KB peak RSS); the
independent verifier passed 11/11 in 0.09 s (30,712 KB), and eight tests with
six mutations passed in 0.74 s (30,684 KB).  Python compilation and JSON
parsing passed in 0.18 s (15,632 KB), the event FNV-1a reproduced
`9c7bbb5d0aabc2ee`, and uncapped `git diff --check` passed in 0.01 s
(10,932 KB).  Two capped Git invocations failed with “unable to create
threaded lstat”; they are recorded as failures, not passes, and Git was rerun
uncapped because the memory ceiling is for Python and TeX workloads.  Papers V
and VI compiled twice; final passes each took 0.44 s with at most 50,824 KB
peak RSS.  Tier 2 was not required because no shared mathematical
input or transitive certificate interface changed.  Tier 3 was not run
because no freeze, all-order theorem, complete NLO probability, or release is
promoted.
