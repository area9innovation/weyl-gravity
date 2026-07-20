# Observer replacement-112 mixed metric--rod Hessian interface close-out

The declared replacement action
\(S_{\mathrm{nonrod}}-S_{R,I_6}+S_{R,H}\), with
\(H=B^{-T}B^{-1}\), now has an exact row-indexed local interface.  The
payload contains the old six-rod subtraction, the H-weighted eight-rod
addition and their net replacement delta for the rod Diff action and signed
adjoint, rod wave block, mixed metric--rod Hessian and formal transpose, and
rod-induced metric Hessian.

All coefficients are normalized in the declared trigonometric-algebraic
unit-circle quotient and retain exact background-jet factors and ordered
Berger-frame PBW multiindices.  An independent implementation reconstructs
the complete coefficient-aware transpose, including PBW commutator terms,
checks the metric Hessian symmetry and gauge-adjoint sign, and recovers
\(K_{RR}=H\Box\) entrywise.  Direct action variation fixes the decisive
\(h_{00}\)-derivative coefficient to
\(-H_{00}e_0(\bar R_{0,1})/2\) and rejects its sign mutation.

The support-local rod wave block has scalar retarded and advanced parents
after multiplication by \(H^{-1}\); its compact spatial zero mode remains a
hyperbolic time sector.  No complete metric-BV Green operator or full
replacement-112 unary is claimed.

CLOSE-OUT: DONE — the normalized mixed metric--eight-rod Hessian, six-rod subtraction, Diff--BV adjoints, support matrices and zero-mode blocks are certified

EVIDENCE: closed_universe_observers/certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE.json

## Verification receipt

- Tier 0 Python compilation, JSON-schema validation and scoped diff check —
  PASS.
- Tier 1 producer — PASS (15.83 s).
- Tier 1 independent action/transpose verifier — PASS (39.67 s).
- Tier 1 focused tests — PASS, 5 tests (55.37 s process time).
- Tier 2 observer-atlas generation and independent verification — PASS
  (1.52 s and 2.98 s).
- Tier 2 direct atlas tests — PASS, 62 tests (50.41 s process time).
- Paper 09 compiled twice to a temporary output directory — PASS (0.85 s
  and 0.64 s; 19 pages).
- Tier 3 was not run: this is a scoped action-interface gate, not a freeze,
  release, shared-core change or theorem promotion.
