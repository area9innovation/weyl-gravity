# Berger graded causal state-space contract

The twenty-row companion is the analytic realization of the retained metric
sector, but it is not the full quantum state space. The imported gauge-fixed
BV complex has 54 rows with displayed-degree ranks

\[
(5,22,22,5).
\]

The independent replay gives 27 even rows, 27 odd rows, 27 odd Darboux dual
pairs, and an antisymmetric pairing of exact rank 54. Every nonzero paired
entry has total displayed degree one.

Subtracting the advanced and retarded causal chain identities gives

\[
q_{54}\Delta_{54}+\Delta_{54}q_{54}=0,
\qquad
\Delta_{54}=\Lambda_{54}^{\mathrm{ret}}-
\Lambda_{54}^{\mathrm{adv}}.
\]

Together with cyclic advanced/retarded adjointness, this defines the even
graded causal form

\[
\sigma_{54}(f,h)=\langle f,\Delta_{54}h\rangle_{\mathrm{BV}}.
\]

The frozen algebraic relation is therefore

\[
[\Phi(f),\Phi(h)]_{\mathrm{gr}}
=i\sigma_{54}(f,h)\mathbf 1.
\]

It specializes to a commutator on even rows and an anticommutator on odd
rows. The BRST Ward identity makes this form descend algebraically to
cohomology. Weak nondegeneracy of the completed distributional quotient is
not yet proved.

The state target is now precise: construct a complete 54-row graded kernel
whose graded antisymmetric part is \(i\Delta_{54}\), which obeys both BRST
Ward identities and has positive-frequency null wavefront set on every
propagating block. Contractible algebraic rows must remain smooth.

The zero-mode ledgers remain separate. Spatial zero modes are retained by
global causal evolution but still need a covariance choice. The fifteen
residual conformal generators and their BFV suspension with \(\lambda=1\)
are algebraic boundary data, not that covariance.

No positive state on the full BV space is asserted. The eventual physical
claim must instead prove positivity on the ghost-number-zero BRST observable
quotient, or state a weaker Krein result explicitly. Existing polarized and
Krein ledgers remain `REDUCED-MODE` evidence and are not distributional.

Thus this certificate closes the algebraic state-space specification before
Hadamard construction. It does not construct a two-point function, prove
Hadamard form or positivity, define renormalized products, restore the QME,
or make a quantum claim.

```text
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_graded_causal_state_space_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_graded_causal_state_space_contract
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_graded_causal_state_space_contract.py -v
```
