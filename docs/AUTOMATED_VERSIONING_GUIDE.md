# Enterprise Automated Semantic Versioning (SemVer) Guide

## 🎯 Purpose & Overview

This repository uses **Automated Enterprise Semantic Versioning (SemVer)** powered by [github-tag-action](https://github.com/mathieudutour/github-tag-action) in GitHub Actions CI/CD pipelines.

Instead of developers manually creating git tags or arbitrary run numbers, the CI/CD pipeline inspects existing Git release tags and automatically calculates, increments, and pushes the next semantic version tag (`vX.Y.Z`) upon successful deployment to production.

---

## 🏷️ How Version Incrementing Works

The pipeline evaluates the current highest tag in the repository and applies increments based on Conventional Commit standards:

| Commit Prefix / Pattern | Version Bump Type | Example Current Tag | New Incremented Tag | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `fix: <message>` or default | **Patch (`+0.0.1`)** | `v1.0.29` | **`v1.0.30`** | Bug fixes, minor patches, security updates |
| `feat: <message>` | **Minor (`+0.1.0`)** | `v1.0.29` | **`v1.1.0`** | New features added without breaking existing APIs |
| `BREAKING CHANGE: <msg>` | **Major (`+1.0.0`)** | `v1.0.29` | **`v2.0.0`** | Major architectural changes or breaking API updates |

---

## 🚀 Conventional Commit Examples

To trigger specific version bumps automatically, structure your Git commit messages or Pull Request titles using conventional commits:

### 1. Patch Version Bump (`v1.0.29` ➔ `v1.0.30`)
```bash
git commit -m "fix: update CORS headers for Static Web App"
```

### 2. Minor Feature Version Bump (`v1.0.29` ➔ `v1.1.0`)
```bash
git commit -m "feat: add PDF document parser for TaxBot RAG pipeline"
```

### 3. Major Breaking Change Bump (`v1.0.29` ➔ `v2.0.0`)
```bash
git commit -m "feat: migrate API to v2 schema

BREAKING CHANGE: updated request payload structure"
```

---

## ⚙️ CI/CD Implementation

In [.github/workflows/app-tax-advisor.yml](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/.github/workflows/app-tax-advisor.yml), the automated tagging step executes at the end of successful deployments:

```yaml
      # ── Enterprise Semantic Versioning (SemVer) Tagging ──────────────────────
      # Automatically calculates & creates the next incremental release tag on GitHub.
      # Increment Rules:
      #   • default / fix: ... ➔ Bumps patch version (e.g., v1.0.29 ➔ v1.0.30)
      #   • feat: ...        ➔ Bumps minor version (e.g., v1.0.29 ➔ v1.1.0)
      #   • BREAKING CHANGE  ➔ Bumps major version (e.g., v1.0.29 ➔ v2.0.0)
      # Triggered on manual dispatch OR push to main/release/* branches.
      # ─────────────────────────────────────────────────────────────────────────
      - name: Auto-Create Enterprise Git Release Tag (SemVer)
        if: github.event_name == 'workflow_dispatch' || ((github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/')) && github.event_name == 'push')
        uses: mathieudutour/github-tag-action@v6.2
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          default_bump: patch
```

---

## 📊 Where to View Release Tags

All generated tags are immediately published to GitHub and can be inspected live at:
* **[GitHub Repository Releases & Tags](https://github.com/RepoCodeGanesh/terraform-azure-iac/tags)**
