# Berger cutoff companion microlocal-response preflight

The smooth cutoff companion now has the first nonstationary microlocal
certificate on the direct Hadamard route.  The all-Sobolev causal Green
family implies Schwartz kernels.  Its causal difference

\[
E_\chi=G_{\chi}^{\rm adv}-G_{\chi}^{\rm ret}
\]

is a two-sided bisolution.  Kernel mapping and elliptic regularity give

\[
\operatorname{WF}(E_\chi)\subset
(N_+\cup N_-)\times(N_+\cup N_-),
\]

with no one-sided zero covectors.

For a smooth time-slice cutoff \(\eta\), with \(d\eta\) supported in a
compact Cauchy slab, the source representative

\[
S_{\chi,\eta}=[C_\chi,\eta]E_\chi
\]

is a regular linear map in the sense of Fewster's Definition 5.13:
continuity, continuous formal transpose, compact support control and absence
of one-sided zero covectors all hold.  Compact support follows because the
causal output is spatially compact and the commutator is temporally compact;
their intersection is compact.  Compactness of the Berger \(S^3\) slices is
therefore sufficient but not required by the proof.

This is deliberately not called the free-to-full response morphism.  The two
same-orientation sectors \(N_+\times N_+\) and \(N_-\times N_-\) remain open,
and the raw companion has not yet been installed as a formally Hermitian
graded GreenHyp object.  Those are the exact next hypotheses needed before a
regular GreenHyp morphism and seed-covariance transport can be claimed.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_cutoff_companion_microlocal_response_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m lorentzian.verify_berger_cutoff_companion_microlocal_response_preflight
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_cutoff_companion_microlocal_response_preflight.py -v
```

Tier receipt:
[`BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT_V1_TIER_RECEIPT.json`](../lorentzian/receipts/BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT_V1_TIER_RECEIPT.json).
