# Paper 17 external-review preparation receipt

Date: 2026-07-27

Scope: documentation and replay of unchanged Paper 17 evidence

Claim lifecycle: unchanged

## Added

- a public external-review entrance;
- a focused Paper 17 review brief;
- three structured GitHub issue forms;
- a one-command scoped reproduction script;
- private outreach drafts under a Git-ignored directory.

No email was sent. No scientific certificate, theorem, claim flag, or paper
text was changed.

## Verification

Tier 0:

```text
bash -n ci/review-paper17.sh
git diff --check -- .gitignore README.md REVIEWING.md \
  docs/external-review/paper17-review-brief.md \
  ci/review-paper17.sh .github/ISSUE_TEMPLATE
```

Result: pass.

The issue forms were parsed with `yaml.safe_load`. Result: pass.

Tier 1 scoped replay:

```text
bash ci/review-paper17.sh
```

Result: pass; 40 unit and mutation tests passed in 12.687 seconds. Total
command wall time was 17.585 seconds.

Tier 2 and Tier 3 were not run because no mathematical input, shared
operator, certificate, schema, generated artifact, or publishable claim was
changed. The scoped replay was sufficient to falsify stale review links to
the selected Paper 17 certificate chain.
