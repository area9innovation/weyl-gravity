# Retained C26 bikernel support-profile disposition

## Result

The current retained Hadamard candidate defines the Ward remainder only by

\[
C_{26}=[H_{26,+},q_{26}],
\]

and certifies that it is smooth. The endpoint inputs do not export one fixed,
content-addressed representative of \(H_{26,+}\): they provide global
existence theorems and symbolic pullback formulas. Therefore the exact support
and pairing-null properties of \(C_{26}\) are undefined from the current
artifacts.

This is not a failed support test. No serialized kernel exists on which such a
test could run. Encoding the requested support booleans as `false` would
incorrectly turn missing representative data into a support no-go theorem.

## First obstruction

The first missing carrier is:

```text
MISSING_NORMALIZED_SERIALIZED_H26_REPRESENTATIVE
```

A sufficient next producer payload is:

- one fixed content-addressed \(H_{26,+}\);
- per-block mode/frequency/coefficient data or an executable distribution
  evaluator and convergence topology;
- the \(q_{26}\) action in both variables;
- the smooth remainder relative to the pinned local parametrix;
- the serialized commutator \(C_{26}\);
- exact x/y support results and a pairing-null witness or counterexample.

The representative issue is material. Under an allowed smooth exact
bisolution change \(H_{26,+}\mapsto H_{26,+}+K\),

\[
C_{26}\mapsto C_{26}+[K,q_{26}].
\]

This states why a representative must be fixed; it does not claim that every
allowed \(K\) changes the support or that no equivariant choice exists.

## Classical consumer

The classical support theorem supplies continuous homotopies on the
x-past-compact, x-future-compact and x-time-compact LF domains. It also proves
that the certified factorization has no continuous extension to the full
smooth compact-open Fréchet class. Because membership of \(C_{26}\) in the
positive one-sided domains cannot yet be decided, no smooth Ward correction
is constructed.

## Claim boundary

Dependency tag: `LORENTZIAN-CAUSAL`.

This result does not establish retained BRST Hadamard data, positivity,
particles, renormalized Lorentzian products, a Lorentzian QME, scattering or
unitarity.

## Verification

```text
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_c26_bikernel_support_profile_nondefinition
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_c26_bikernel_support_profile_nondefinition_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_c26_bikernel_support_profile_nondefinition
PYTHONPATH=quantum-weyl python3 -m unittest lorentzian.tests.test_berger_c26_bikernel_support_profile_nondefinition
```

CLOSE-OUT: OBSTRUCTED — the first missing content-addressed Hadamard representative is certified
EVIDENCE: quantum-weyl/lorentzian/certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json
