# Projective Evans panel 292 subdivision repair

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The fixed `1/1024` panel `292/1024` failed its endpoint export. Without changing the stable-root or acceptance thresholds, its two exact dyadic children were evaluated:

- `584/2048`: Delta lower `[3.4178784076151502076169390252775261489e-5 +/- 9.05e-43]`, row SHA-256 `580e45557153791e19975deb4dd77371644de63586a4d06736472046f2391673`.
- `585/2048`: Delta lower `[3.4271181472083778248612335666745056349e-5 +/- 7.23e-43]`, row SHA-256 `ab2cb377f0ad77d5a0fa262cc1d0950a4e388da4b5b7ab3adb6403ec2e831cf6`.

Both typed mismatch enclosures exclude zero. The contiguous boundary prefix therefore ends at `293/1024`; the next honest gap starts there. Full-contour, winding, root-count, QNM, Smith and EP2 claims remain false.
