# Coupled 36-row transfer replay

The quantum-side consumer now imports the committed portable 64/36 carrier
without executing a classical producer.  It independently recomputes

```text
ell2_mixed = pi64 q2_Maxwell-overlay(iota36,iota36)
```

and matches every one of the classical payload's 1,522 exact coefficients.
The full and retained arity-two `q1/q2` identities also vanish exactly.

The cyclicity claim does not replay.  Lowering with the exported odd pairing
and reducing by the established PBW/integration-by-parts backend leaves 1,234
nonzero coefficients on the 64-row overlay and 953 after transfer to 36 rows.
The first retained normalized witness is

```text
(row 0, row 26, row 35; left word []; right word [e1]) -> 3.
```

The certificate records complete defect hashes.  This blocks promotion of
the mixed vertex and mixed `q3`: the classical coupled tensor or its pairing
and sign convention must be repaired first.  The causal Green theorem is
only hash-pinned here, and no quantum claim is made.

Machine-readable result:
`quantum-weyl/transfer/certificates/BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY.json`.
