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

## ⚙️ Dual CI/CD Implementation (Azure DevOps + GitHub Actions)

Industry standard practice requires that every production deployment creates **both** a Git Tag and an official **GitHub Release** with auto-generated release notes:

### 1. Azure DevOps Pipeline ([azure-cicd-app-tax-advisor.yml](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/pipelines/azure-cicd-app-tax-advisor.yml))
```yaml
    - task: AzureCLI@2
      displayName: 'Auto-Create Enterprise Git Release Tag & GitHub Release (SemVer)'
      inputs:
        azureSubscription: '$(azureServiceConnection)'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          # 1. Fetch highest tag and calculate next SemVer
          # 2. Push Git Tag to repository: git push origin "${TAG_NAME}"
          # 3. Call GitHub API to publish official GitHub Release with auto-generated notes:
          curl -s -X POST \
            -H "Authorization: token ${GITHUB_TOKEN}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/RepoCodeGanesh/terraform-azure-iac/releases \
            -d "{\"tag_name\":\"${TAG_NAME}\",\"name\":\"Release ${TAG_NAME}\",\"body\":\"Automated Enterprise Production Deployment ${TAG_NAME}\",\"draft\":false,\"prerelease\":false,\"generate_release_notes\":true}"
      env:
        GITHUB_TOKEN: $(GITHUB_TOKEN)
```

### 2. GitHub Actions Workflow ([.github/workflows/app-tax-advisor.yml](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/.github/workflows/app-tax-advisor.yml))
```yaml
      - name: Download Backend Package Artifact for Release
        uses: actions/download-artifact@v4
        with:
          name: taxbot-backend-package
          path: .
        continue-on-error: true

      - name: Auto-Create Enterprise Git Tag (SemVer)
        id: tag_version
        uses: mathieudutour/github-tag-action@v6.2
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          default_bump: patch
          tag_prefix: v

      - name: Create Official GitHub Release with Attached Build Artifacts
        uses: ncipollo/release-action@v1
        with:
          tag: ${{ steps.tag_version.outputs.new_tag }}
          name: Release ${{ steps.tag_version.outputs.new_tag }}
          body: ${{ steps.tag_version.outputs.changelog }}
          artifacts: "functionapp.zip"
          token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🏗️ Application vs. Infrastructure (IaC) Versioning Strategy

This repository enforces a clear architectural distinction between Application software releases and Infrastructure as Code state:

| Layer | Component | Versioning Mechanism | Rationale |
| :--- | :--- | :--- | :--- |
| **Application CI/CD** | `app-tax-advisor` | **Automated SemVer Git Tags (`v1.0.X`) + GitHub Releases** | Application code compiles into React bundles and Function App packages. Release versioning is required for deployment gates, QA, and rollbacks. |
| **Infrastructure (IaC)** | `platform/*` & `workloads/*` | **Terraform Remote State Versioning + Git SHAs** | Infrastructure is declarative. Terraform natively versions its remote state (`sthtbootpcin01`) in Azure Blob Storage on every `terraform apply`. Git release tags are not created per IaC push. |

---

## 📊 Where to View Releases & Tags

All generated releases and tags are immediately published to GitHub and can be inspected live at:
* **[GitHub Repository Releases](https://github.com/RepoCodeGanesh/terraform-azure-iac/releases)**
* **[GitHub Repository Tags](https://github.com/RepoCodeGanesh/terraform-azure-iac/tags)**
