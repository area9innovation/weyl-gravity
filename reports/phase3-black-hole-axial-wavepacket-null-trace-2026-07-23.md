# Phase 3 axial wave-packet null-trace audit

Date: 23 July 2026

## Outcome

The formal axial infinity classes now lift to exact bounded wave-packet
radiation traces on the declared compact frequency interval:

\[
\boxed{
\mathscr I^-:(XI0,XI1,EI0),\qquad
\mathscr I^+:(XI2,XI3,EI2),
}
\]

each with a three-dimensional positive-frequency trace in
\(L^2([1/2,3/4];\mathbb C^3)\).  This closes the first Phase-3 bridge from
formal Bach modes to exact solutions near null infinity.

It does **not** yet define a finite Lee--Wald flux Gram.  That requires an
action-current continuity and asymptotic pullback theorem, including a
justified interchange of the radial limit with the frequency integrals.
No horizon-to-infinity connection, scattering channel, stability, or CPT
claim is made.

## Exact recurrence repair

The four additional columns were extended with carrier data through inverse
order eight, metric heads \(H_0,H_1\) through inverse order five, and the
derivative-forced \(F\) term through order six where required.  The apparent
depth-seven solution is rejected: the \(z^{-2}\) metric source makes the
\(H_1\) coefficient \(A_5\) depend on carrier coefficient eight.

Both Einstein-kernel heads were independently extended by one order.  No
new recurrence pivot vanishes on \([1/2,3/4]\), and every forced logarithmic
coefficient is zero.  Exact lower residual valuations are

\[
R_c:(10,10,10,10),\qquad
R_m:(8,7,5,4),\qquad
R_k:(6,6).
\]

The resulting cross-rate decay table has minimum \(p=5\), including the
formerly obstructing \(EI0\to EI2\) entry.

## Differentiated Volterra theorem

Exact rational rectangle arithmetic on four frequency cells, combined with
Neumann inverse gates and differentiated inverse/Volterra recursion, gives
uniform bounds through \(\partial_\omega^3\).  The contraction bounds are

\[
q_0<2^{-16356},\quad q_1<2^{-12252},\quad
q_2<2^{-8148},\quad q_3<2^{-4042},
\]

and the correction-jet ceilings are \((2,1,2,4)\).  Since each frequency
derivative of the cross-rate phase loses at most one radial power,
\(p-k>1\) holds for every \(k\le3\).

## Exact endpoint traces

For \(b\in C_c^3((1/2,3/4))\), three integrations by parts give

\[
\left|\int e^{i\omega L}b(\omega)\,d\omega\right|
\le |L|^{-3}\|\partial_\omega^3 b\|_{L^1}.
\]

The largest metric head grows as \(r^2\), while the wrong-endpoint phase has
\(|L|\gtrsim r\).  The exact corrected contribution therefore vanishes at
the wrong endpoint.  At the matching endpoint, dominated convergence gives
the radiation trace.  Plancherel makes the trace bounded on the smooth
compactly supported core and extends it to the declared \(L^2\) completion.
This extension concerns the matching trace.  The three-fold integration-by-
parts statement at the wrong endpoint remains a theorem on the
\(C_c^\infty\) core (or its \(H^3\) closure), not on arbitrary \(L^2\)
profiles.

Negative frequencies are supplied by the real-field involution

\[
a_{\ell,-m}(-\omega)=(-1)^m\overline{a_{\ell m}(\omega)}.
\]

## Exact remaining boundary

The trace theorem alone does not prove finite action-derived flux.  The next
successor must pull the pure-Weyl Lee--Wald current back to these exact trace
coordinates and prove that its radial limit is a continuous Hermitian form
on the wave-packet space.  Only then can its Gram, radical, quotient and
inertia be reported.  Global horizon matching comes after that local-at-
infinity flux gate.

## Verification

```text
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.depth5_recurrence --check
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.produce --check
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.verify
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.verify --deep  # expensive Tier 2 rail
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.mutations
python3 -m pytest -q black_hole_programme/phase3/axial_wavepacket_null_trace/tests
python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-axial-wavepacket-null-trace-fragment-v1.json
```

CLOSE-OUT: SHORTFALL — exact three-dimensional axial wave-packet radiation
traces are constructed separately at \(\mathscr I^-\) and \(\mathscr I^+\)
on the declared compact positive-frequency interval.  The action-derived
endpoint flux Gram remains open pending a current-pullback and continuity
theorem.

EVIDENCE: `black_hole_programme/phase3/axial_wavepacket_null_trace/certificate.json`;
`black_hole_programme/phase3/axial_wavepacket_null_trace/verify.py`;
`black_hole_programme/phase3/axial_wavepacket_null_trace/differentiated-envelope.json`.

MISSING-DEP: certify the asymptotic Lee--Wald current pullback, its radial
limit/interchange theorem, and the resulting continuous endpoint flux Gram.
