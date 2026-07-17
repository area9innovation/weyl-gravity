# Berger coupled Maxwell q2 interface contract

## Outcome

The combined gravity-clock-Maxwell BV consumer is now fixed at 64 rows: the
authoritative 54 gravity-clock rows followed by `c_M`, four `A_mu`, four
`A_plus_mu`, and `c_M_plus`.  The degree ranks are `[6,26,26,6]`.

This successor contract leaves the old content-addressed preflight unchanged.
It records that the first physical mixed blocks now exist, while the complete
arbitrary-support dynamical export and its canonical completion remain
`INPUT_BLOCKED`.

## Canonical sign and cyclic normalization

For

```text
A_st=2 cos(beta t)e1 with the certified diagonal h^(2)
```

the repository gravity row is twice the direct covariant-metric derivative.
Consequently the canonical metric pairing carries the compensating one-half.
The Maxwell action and declared pairing give

```text
E_A=-d star_g dA for S_M=-1/2 integral(F wedge star_g F) and pairing integral(delta A wedge delta A_plus)
```

whereas the earlier frequency calculation used the equivalent equation-form
representative with the opposite common sign.  The exact three-way check is

```text
direct cubic action pairing       = 564428800/35920017
half metric repository pairing   = 564428800/35920017
averaged canonical Maxwell pair  = 564428800/35920017
cyclic residual                  = 0
```

The common Euler sign does not alter the zero locus or the certified nonlinear
frequency shift `-7055360*sqrt(10)/11973339`.

## Acceptance gate

The complete exporter must supply all 64 output-row ledgers, the combined
arity-two identity, cyclicity, local D derivation, action generation, all
three physical regressions, and sign/factor/row/partner mutation rejection.
Only then may `BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2` become true.

The compact Berger standing-light sector and the generic axial Weyl-Maxwell
harmonic sector remain separate background specializations.  Neither may be
substituted for the other without an explicit content-addressed adapter.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_COUPLED_MAXWELL_Q2_INTERFACE_CONTRACT.json`.
