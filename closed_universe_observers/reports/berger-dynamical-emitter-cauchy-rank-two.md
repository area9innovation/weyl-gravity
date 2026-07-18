# Dynamical-emitter Cauchy rank two

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

For each detector, compose the selected free-emitter Cauchy solution map with
the switched current, retarded Maxwell field, and detector functional:

```text
ell_a(u) = Q_a[d G_A,ret g_a delta(h_a U_E u)].
```

Green adjunction identifies `ell_a` with Cauchy pairing against the advanced
detector solution.  The detector phase functionals are nonzero.  Their
advanced solutions meet receiver-adjacent past patches, and the exact local
massive polarization

```text
p = (sqrt(k^2+m^2),0,0,k),
K_01 = k,  K_31 = -sqrt(k^2+m^2)
```

satisfies `p^mu K_mu nu=0` while its clock contraction is nonzero.  Thus the
switched current sees a physical massive polarization.  Using
`H1(S3)=H2(S3)=0`, constraint potentials can be localized in the nonzero
patch.  A fixed first-nonzero local-basis rule selects compact Cauchy data
`u_0,u_1` before forward evaluation.  With `g_0,g_1` declared nonzero, this
gives `kappa_a=ell_a(u_a) != 0`.

Place the second switch after `D0` and before `D1`.  Retarded support gives

```text
M^(K) = [[kappa_0, 0], [mu, kappa_1]],
det M^(K) = kappa_0 kappa_1 != 0.
```

Hence two actual massive-emitter preparations produce two distinguishable,
causally acquired persistent records at leading coupling order.  The stronger
common-Hopf preparation, detector-level `g^2` recoil integral, emitter stress,
finite-parameter Green theorem, full Dirac algebra, and quantum theory remain
open.
