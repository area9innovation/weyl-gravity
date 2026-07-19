# Berger finite positive-energy preparation coefficients

The machine certificate is
`certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json`.

The preceding finite result exported the twelve-component spacetime jet
`(K,partial_t K)`.  The recoil word instead uses six canonical spatial Cauchy
components.  Writing `K=dt wedge alpha+beta`, they are

```text
q = beta,
p = partial_t beta-d_Sigma alpha.
```

Eliminating the temporal component gives

```text
alpha = m^-2 delta_Sigma p,
A = I+m^-2 d_Sigma delta_Sigma,
L = delta_Sigma d_Sigma+m^2.
```

The coupling-stripped positive-energy dual is therefore
`tilde_u=(-A p,Lq)`, with energy `<p,A p>+<q,Lq>>0` for nonzero exact data.

This also corrects the earlier co-closed restriction.  Exact block audits
through `two_j=4` verify the co-closed projector identities, but
`delta_Sigma q=delta_Sigma p=0` forces `alpha=0`.  For the selected clock-only
switch this makes `delta(hK)=0`, so that restricted rail is an observer-source
zero mode and is not used for the operational preparation.

The callable returns outward rational interval coefficients for every D0/D1
passive column through `two_j=4` and any strictly positive rational
mass-squared interval.  The certificate serializes endpoint fixtures on
`m^2 in [1,2]`; that interval is validation data, not a physical parameter
choice.

This does not prove a retained unrestricted coefficient nonzero, control the infinite
spatial tail, apply free emitter evolution, evaluate a retarded recoil channel
or `I_abc`, restrict the records to the second-order cone, activate Bridge 3,
or establish a quantum result.
