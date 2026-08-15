# Nonlinear Weyl/boost ghost manifest v1

**Result:** `CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1`

**Dependency:** `LOCAL-ALGEBRAIC`

Metsaev's full nonlinear transformation (6.6), absent from the older local
summary, contains the three `b-kappa` terms.  In the repository convention it
is

```text
delta_kappa phi_mu_nu = nabla_mu kappa_nu + nabla_nu kappa_mu
                      + b_mu kappa_nu + b_nu kappa_mu
                      - g_mu_nu b^rho kappa_rho.
```

Exact coefficient collection proves `delta_kappa G^b=A_g(delta_kappa phi)`
and `delta_sigma G^b=0`.  Hence `f_hat=phi-A_g^-1 G^b` is invariant under
both internal symmetries.  The Weyl--boost and boost--boost commutators also
vanish off shell.  After `eta=kappa-d sigma`, the only nonzero ghost brackets
are the Diff semidirect actions.

The exhaustive manifest in this scope therefore has
**3** nonzero families: two
already in the minimal master action and the already serialized
`DIFF_C_ETA_ETA_STAR` auxiliary family.  It requires
**0**
additional Weyl/boost ghost-antifield families.

This closes the manifest question, not the full source import.  The separate
386-row assembly and its `q1/q2`, cyclicity and `D` replays remain open.

Primary source: [Metsaev, arXiv:0707.4437v3](https://arxiv.org/abs/0707.4437),
equations (6.2)--(6.7); the retrieved 58-page PDF hash is
`80bbe298159e4fdfc35c0f4dd4e33f01e5da51227184a0bed870e5fa3e6b2676`.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_nonlinear_weyl_boost_ghost_manifest_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_nonlinear_weyl_boost_ghost_manifest_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_nonlinear_weyl_boost_ghost_manifest_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_nonlinear_weyl_boost_ghost_manifest_v1
```
