# Tensor observable extension and projection audit

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
Status: conditional research note; no full-BV positivity or quantum lifecycle promotion.

## Outcome

The reduced reference's stale dependency can be reconciled, but the attempted
full-complex extension exposes a different, substantive projection mismatch.
We now have an explicit compact-source lift that preserves linear gauge
invariance. We do not yet have its action-normalized all-energy commutator.

The earlier [cutoff proof](tt-hadamard-cutoff-obstruction-v1.md) remains a
statement about the specified reduced spectral model. The new evidence is
[TT_OBSERVABLE_EXTENSION_V1](../results/TT_OBSERVABLE_EXTENSION_V1.json).

## Reference reconciliation

The original reduced Bridge-4 certificate is preserved. Its sole stale direct
input is the causal-pairing certificate; the changed bytes replace a
`prolonged_current` provenance hash, leaving the displayed pairing and signs
unchanged. We ran the current direct causal-pairing verifier with its guards
and the prolonged-current comparison with all 17 guards. Both pass.

The [reconciled reference](../inputs/tt-reduced-reference-reconciled-v1.json)
changes **only** `dependencies.causal_pairing_transport.sha256`. The independent
Bridge-4 checker and its mutation controls pass on that copy, including all
its direct dependency hashes and oscillator/CCR identities. This resolves
that specific reduced-reference import failure. It does not certify every
transitive classical premise or repair the global projection issue below.
The old certificate and the old failure receipt remain intact.

## The actual compact observable lift

Read `p_end_graph` from the serialized strict-386 graph SDR. Its metric block
`p0` consists of rows 5 through 14. Despite the full map having order three,
this block has **order zero and 25 nonzero rational entries**. It maps the
386 coordinates to the ten metric coordinates. The exact entries are retained
in the new result. The inclusion satisfies `p0 i0=I_10` on the relevant block.

For an ordinary metric source density f, define `F=p0^T f`. The transpose here
is the ordinary field/source transpose, not an unidentified odd-BV adjoint.
When converting a symmetric tensor to independent metric coordinates, include
the usual off-diagonal multiplicities in f. Since p0 is order zero, F has the
same compact support as f. Pullback of a two-point distribution is simply
`W_metric=p0 W_full p0^T`; smooth bundle multiplication cannot enlarge its
wavefront set. No finite harmonic cutoff or inverse frequency is used.

## A failed advertised identity and an exact replacement

A direct composition of the serialized coefficients finds

```
p0 R386 != Rmetric pghost.
```

There are 28 nonzero first-derivative coefficients in the difference. For
example, on derivative multiindex `(0,1,0,0)`, target `h_12` (index 10), source
`X_Id_sharp[7]` (index 233), the two sides are respectively

```
-1/4 and +1/4; difference -1/2.
```

Both projection blocks are order zero, so this is a principal first-order
mismatch. Curvature commutators, which lower derivative order, cannot remove
it. An independent dense rational SymPy calculation reproduces this entry.
The pre-existing graph checker still reports PASS: its formal chain-map
transport check does not directly test this particular component equality.
Thus the advertised serialized projection chain-map claim needs reconciliation;
we do not infer a refutation of the underlying classical BRST theory.

There is nevertheless an explicit factorization sufficient for gauge-invariant
metric observables. Define Gamma from the published pghost by changing its
four coefficients

```
(c0,238), (c1,232), (c2,233), (c3,234): +1/4 -> -1/4
```

and adding to its Weyl-ghost output the differential operator

```
( d0 X_Id_sharp[12] + d1 X_Id_sharp[6]
 +d2 X_Id_sharp[7] + d3 X_Id_sharp[8] ) / 16.
```

Then the exact coefficients give **`p0 R386 = Rmetric Gamma`**. No nonzero
product of two positive-order factors occurs: the derivative correction lands
in the Weyl slot, where Rmetric is algebraic. Hence the check needs no
unjustified commuting-covariant-derivative assumption.

For a transverse traceless spatial metric source with zero temporal components,
`Rmetric^T f=0` by integration by parts. Consequently

```
R386^T F = Gamma^T Rmetric^T f = 0.
```

The filtered compact-time tests of the cutoff proof therefore have an explicit
gauge-invariant source lift at this local linear level. Gamma is a new
factorization for this block, **not** a repaired global SDR or a replacement
for every degree of the published ghost projection.

## What is still needed to transfer the no-go

The missing comparison is now concrete:

```
p0 Delta386 p0^T restricted to every TT harmonic
   = the reduced action-normalized E/L commutator.
```

It must use ordinary source/field coordinates and account for the inherited
pairing and suspension signs. The failed advertised chain identity prevents
us from replacing this check by a citation to the old global projection claim.
A corrected full cyclic retract, or a direct independent TT commutator
calculation, could supply it. We have supplied neither in this extension.

If that comparison holds, positivity on physical BRST observables would pull
back to positivity on these metric tests, and the zero-order projection would
preserve the Hadamard wavefront bound. The earlier smooth-difference argument
would then yield the contradiction. A nonzero induced commutator would also
exclude treating these observable classes as equations-of-motion trivialities.
Until this comparison is established, physical nonexactness in the full
complex and the full positivity obstruction remain open.

## Publication disposition

Paper 21 includes the finite/continuum separation as a conditional case study,
with the exact filter and growing repair bound. Paper 04 gets a scope
cross-reference: changing the real structure is outside this example.
The website gives a plain-language cutoff demonstration, links to the evidence,
and explicitly retains the unresolved commutator and projection audit. The finite frequency-flipped repairs need not have positive energy and do not
establish stable interacting dynamics. This is
not a new ghost discovery or a reverse-mathematical equivalence theorem.

## Reproduction

```
python3 foundations/build_tt_observable_extension.py --check
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 foundations/verify_tt_observable_extension.py
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 -m unittest foundations.tests.test_tt_observable_extension
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 symbolic/verify_conformal_direct_causal_pairing_transport.py --guards
PYTHONPATH=/tmp/tt-hadamard-check-deps python3 symbolic/verify_conformal_prolonged_current_comparison.py
```

The first two new scripts use distinct production and verification paths.
The independent source-lift verifier reads the raw coefficient tables and uses
exact rational sparse multiplication; its tests also use a dense matrix rail
for the negative principal witness. The analytic support, gauge-invariance and
conditional positivity arguments above remain human proofs. Validation times,
publication checks and skipped-tier reasons are recorded in the companion
`foundations/receipts/tt-observable-publication-v1.json`.
