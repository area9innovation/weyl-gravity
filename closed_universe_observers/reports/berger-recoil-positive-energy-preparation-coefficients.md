# Berger finite positive-energy preparation coefficients

The machine certificate is
`certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json`.

The preceding finite result exported the twelve-component spacetime jet
`(K,partial_t K)`.  The recoil word instead uses six spatial Cauchy
components.  Writing `K=dt wedge alpha+beta`, this result constructs the exact
orthogonal projector `Pi_co` onto `ker(delta_Sigma)` and takes

```text
q = Pi_co beta,
p = Pi_co(partial_t beta-d_Sigma alpha) = Pi_co partial_t beta.
```

The equality is exact because `Pi_co d_Sigma=0`.  Exact block audits through
`two_j=4` also verify projector idempotence, self-adjointness and
`delta_Sigma Pi_co=0`.  The coupling-stripped positive-energy dual is then

```text
tilde_u = (-p,(Delta_2^co+m^2)q).
```

The callable returns outward rational interval coefficients for every D0/D1
passive column through `two_j=4` and any strictly positive rational
mass-squared interval.  The certificate serializes endpoint fixtures on
`m^2 in [1,2]`; that interval is validation data, not a physical parameter
choice.

This does not prove a retained coefficient nonzero, control the infinite
spatial tail, apply free emitter evolution, evaluate a retarded recoil channel
or `I_abc`, restrict the records to the second-order cone, activate Bridge 3,
or establish a quantum result.
