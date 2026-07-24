# Exact all-\(\ell\) threshold structure

This package certifies the horizon-normalized zero-frequency spin-one and
spin-two Regge--Wheeler solutions for every integer \(\ell\ge2\), and proves
that neither scalar factor has a zero-energy resonance.

The terminating hypergeometric solution is regular and nonzero at the
horizon but grows as \(r^{\ell+1}\).  Its reduction-of-order partner can be
chosen to decay as \(r^{-\ell}\) at infinity, but is logarithmically singular
at the horizon.

The low-frequency Jost coefficients are recorded only as formal matching
predictions.  A uniform two-region Volterra estimate remains required before
claiming a punctured zero-free scattering interval.

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_threshold.py
```
