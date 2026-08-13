# Complete connected BT common-Born packet

**Certificate:** `REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The actual coherent all-ten-channel, source-connected order-
\(\lambda^4\) compact BT packet has the same click operator in the public
generalized-Krein prescription and in the positive-Hilbert prescription:

\[
 A_{{\rm full},C}^{\sharp}A_{{\rm full},C}
 =A_{{\rm full},C}^{*}A_{{\rm full},C}.
\]

This extends the preceding single selected-pointer result without selecting,
decohering, or reweighting the ten public tree channels.  Every coherent cross
term remains present.

The statement is complete for the source-connected order-\(\lambda^4\) graph
column on the declared compact regular domain.  It is not the complete
order-\(\lambda^4\) evolution: disconnected spectator terms have not yet been
constructed.

## Exact total-parity calculation

The six-point species carrier has basis masks of weight three.  Three-particle
ghost parity is the complement involution

\[
 \kappa_3|x\rangle=|7-x\rangle.
\]

The ten independent channel coefficients occupy ten complementary pairs in
the \(8\)-by-\(8\) Choi matrix.  Assigning the exact rational fixture
\(1,2,\ldots,10\) tests every coefficient independently.  Direct rational
matrix multiplication gives

\[
 \kappa_3 A_6\kappa_3=A_6,
 \qquad (A_6)_{\rm odd}=0,
 \qquad A_6^\sharp=A_6^T.
\]

There are twenty nonzero entries.  Both quadratic traces are

\[
 \operatorname{Tr}(A_6^\sharp A_6)
 =\operatorname{Tr}(A_6^T A_6)
 =2\sum_{j=1}^{10}j^2=770,
\]

so the exact public-versus-Hilbert defect is zero.  The fixture is not a
special numerical choice: because all ten coefficients are algebraically
independent positions paired by complement, the matrix identity is
coefficientwise.

## Lift to the packet operator

The complete connected predecessor constructs the physical unit-weight sum

\[
 A_{{\rm full},C}=16\lambda^4
 \sum_{B=0}^{9}K_{B,T}\otimes R_B.
\]

The finite-time kernels \(K_{B,T}\) and common compact cutoff act on momentum
variables, while \(\kappa_3\) acts on the species carrier.  They commute.
The coefficientwise Choi identity therefore lifts term by term:

\[
 \alpha(A_{{\rm full},C})
 =\kappa_3A_{{\rm full},C}\kappa_3
 =A_{{\rm full},C}.
\]

The exact Born-descent theorem says that total-\(\kappa\) fixedness is precisely
the condition under which the public and positive adjoints agree.  Hence

\[
 A_{{\rm full},C}^{\sharp}=A_{{\rm full},C}^{*},
 \qquad
 E_{\rm click}^{\rm public}=E_{\rm click}^{\rm Hilbert}
 =A_{{\rm full},C}^{*}A_{{\rm full},C}.
\]

On the certified contraction domain

\[
 {12960\lambda^8T^2\mu(X)\mu(Y)\over d^2}\leq1,
\]

both \(E_{\rm click}\) and \(I-E_{\rm click}\) are positive and sum to the
identity.

For the declared dressed positive source \(F\otimes u_0\), the common
probability is

\[
 q_{\rm click}^{\rm public}=q_{\rm click}^{\rm Hilbert}
 =16\lambda^8\left\|\sum_{B=1}^{9}K_{B,T}F\right\|^2.
\]

The single norm square retains all \(B\ne B'\) interference terms.

## Meaning and boundary

This closes the channel-selection loophole for the leading connected compact
tree process: agreement of the Born rules is a symmetry theorem for the
actual coherent ten-channel operator, not an artifact of looking at one
channel at a time.

It does not establish:

- disconnected spectator completion of the full order-\(\lambda^4\) evolution;
- removal of the compact regular cutoff or control of \(q_B=0\) soft strata;
- a detector-independent integrated cross section;
- loop, \(\lambda^{10}\), higher-order, or all-time positivity;
- a M\o ller, LSZ, or scattering operator;
- the standard scalar-projector pushforward or general Eq. (19);
- gravity or metric BV--BRST transfer, QME restoration, or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Verification

All Python, TeX and repository-test processes ran sequentially.  Python and
TeX ran under the 500 MB virtual-memory ceiling; the read-only Go shadow rail
was run separately and measured after that ceiling prevented Go's virtual
arena reservation.

- Tier 0 passes.  The producer, independent verifier and mutation tests
  compile, every changed JSON file parses, the strict Draft-2020-12 schema and
  certificate validate, an injected additional property is rejected, and the
  scoped `git diff --check` is clean.  Schema validation took `0.08 s` at
  `21780 KiB` peak RSS.
- The exact rational producer passes `31/31` checks in `0.03 s` at
  `16536 KiB`.  The independent verifier reconstructs the masks, Choi matrix,
  complement involution, parity split, adjoints, both trace squares,
  predecessor bounds, probability formula and claim boundary without
  importing the producer; it passes `55/55` checks in `0.02 s` at
  `15744 KiB`.  All `47` adversarial mutation tests pass in `0.181 s`
  (`0.21 s` enclosing wall time) at `18644 KiB`.
- The affected Tier-2 chain passes for the complete connected order-
  \(\lambda^4\) packet column, six-point ghost-even history embedding,
  kappa-fixed Born descent and recorded ten-channel compact instrument.  Its
  eight producer/verifier commands took `0.87 s` at `67232 KiB` peak RSS.
- Papers V and VI compile twice with
  `pdflatex -interaction=nonstopmode -halt-on-error`.  Their PDFs have `78`
  pages and `736610` bytes, and `67` pages and `694852` bytes, with SHA-256
  `3da7ad3e8fa77a2acd9a36aeaa07bf3759efc2f2b2c0c7b7bbc7a870495e5846`
  and
  `c84a909507e2a0f1709b058a7acf3c10c561cc2564e59c57450eed950e8d4dd8`.
  The two-pass commands took `1.04 s` at `51044 KiB` and `1.16 s` at
  `50796 KiB`.  There are no undefined citations or references and no new
  overfull box; Paper V retains six known boxes and Paper VI two.
- Tier 3 is fail-closed, not a repository-wide pass: `3097` tests ran in
  `704.236 s` (`705.27 s` enclosing wall time) at `391304 KiB` peak RSS, with
  `31` failures and `9` skips.  This is the established failure/skip census
  plus the `47` passing tests introduced here.  Older certificate drift and
  `chain_imports` outside-reference findings remain unresolved.  No failed or
  skipped rail is counted as a pass.
- The append-only Science Forge fold accepts `1565` nodes with zero invalid
  items and zero malformed events in `1.49 s` at `14164 KiB` peak RSS.  The
  cached coordinator binary was used because rebuilding the moving substrate
  currently fails at the known toolchain mismatch.
- The advisory shadow wrapper exits zero by design in `1.15 s` at `32756 KiB`,
  but its bridge audit remains fail-closed with the Forge binary/standard-
  library mismatch and `E9118`.  Its census reports `1622` certificates and
  `1400` verifier files against the older baseline.  A first attempt through
  the semantic-search shell shim was terminated, and a capped attempt failed
  Go virtual-arena reservation; neither is counted as an audit pass.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` physical theorem.  No classical freeze, QME state,
shared core algebra, residual transfer or `LORENTZIAN-CAUSAL` state changed.
The final certificate SHA-256 before staging is
`6a3b5edeb28c6b50d8fbc9746436ca3d3ce53ab04426f7531ac121f121d52661`.

## Next gate

Construct the disconnected spectator contribution on the same compact
three-particle domain and test the sum of connected and disconnected
order-\(\lambda^4\) transition operators for total-\(\kappa\) fixedness.  The
parallel perturbative gate is the \(\lambda^{10}\) correction to the same
common-Born click effect.
