# 18. AI-300: Azure Machine Learning & MLOps for DevOps Engineers

* **Space:** `HappyTechies Cloud & AI Platform`
* **Target Audience:** Azure DevOps Engineers, Cloud Platform Architects, MLOps Practitioners, AI-300 / DP-100 Exam Candidates
* **Owner:** `ai-platform-team@happytechies.com`
* **Status:** `ACTIVE / CERTIFICATION GUIDE`

---

## 1. Executive Summary & Paradigm Shift

As an **Azure DevOps (ADO) Engineer**, you already understand 90% of the principles governing **Machine Learning Operations (MLOps)**. Both disciplines solve the identical operational problem: **taking an artifact developed locally and delivering it reliably, repeatably, securely, and automatically into production cloud infrastructure.**

The only fundamental difference is the artifact being compiled:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TRADITIONAL SOFTWARE CI/CD (Azure DevOps)                                              │
│                                                                                        │
│     [ Source Code ]  ───( Compile & Build )───►  [ Binary / Docker Image / NuGet ]     │
│       (C# / TS)          (azure-pipelines.yml)         (Deployed to AKS / App Service) │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ENTERPRISE MLOps (Azure Machine Learning)                                              │
│                                                                                        │
│     [ Code + Versioned Data ] ───( Train & Evaluate )───►  [ Model Weights Artifact ]  │
│        (Python + Parquet)            (AML Pipeline DAG)          (model.pkl / ONNX)    │
│                                                                  (Deployed to Endpoint)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

In software engineering, code is deterministic: compiling `commit abc123` always generates the exact same binary. In machine learning, running `train.py` on Monday produces a **completely different model** if the database received 50,000 new rows on Tuesday. MLOps is simply DevOps extended to version **Data**, track **Experiments**, and monitor **Model Accuracy & Drift**.

---

## 2. Master Rosetta Stone: Azure DevOps vs. Azure Machine Learning

The following table provides an exhaustive 1-to-1 mapping between familiar Azure DevOps constructs and Azure Machine Learning Studio components:

| Category | Azure DevOps (ADO) Construct | Azure Machine Learning (AML) Equivalent | Architectural Purpose & Exact Parallel |
| :--- | :--- | :--- | :--- |
| **Governance** | **ADO Project** (`dev.azure.com/org/proj`) | **AML Workspace** (`ml-ai300-workspace`) | Central security boundary, RBAC container, and root hub for all assets, history, and compute. |
| **Identity & Auth** | **Service Connection** (ARM / SPN / OIDC) | **Connections & Datastores** | Centralized, secure storage for service principals, SAS tokens, and credentials; eliminates hardcoded API keys. |
| **Workstation** | **Dev VM / Jumpbox / Cloud Workstation** | **Compute Instance** | Dedicated single-user VM for interactive development, debugging, and running Jupyter Notebooks. |
| **Agent Pool** | **VMSS Self-Hosted Agent Pool** (Min=0) | **Compute Cluster** | Scalable multi-node VM pool. Sits at `0` nodes when idle (\$0 cost) and scales up to `N` nodes on job arrival. |
| **Base Image** | **Agent Container** (`container: image:v1`) | **Environment** (Docker + Conda) | Immutable container image + `requirements.txt` defining runtime dependencies (Python, CUDA, PyTorch). |
| **Reusable Tasks** | **YAML Step Template** (`template: step.yml`) | **Component** (`component.yaml`) | Modular, parameterized, reusable pipeline building block with strict typed inputs and outputs. |
| **Source Control** | **Git Repo Commit SHA** (`git checkout`) | **Code + Data Asset** (Versioned Data) | Snapshot pointer (`azureml:sales:v2`) ensuring exact data reproducibility across historical training runs. |
| **Visual Authoring** | **Classic Pipeline Editor** (Visual GUI) | **Designer** | Drag-and-drop canvas for building ML pipelines without writing Python code. |
| **Code Authoring** | **VS Code / Local Git Repository** | **Notebooks** (JupyterLab) | Code-first editor for writing training scripts using the Azure ML Python SDK v2 (`azure-ai-ml`). |
| **Orchestration** | **Multi-stage Pipeline** (`azure-pipelines.yml`) | **Azure ML Pipeline** (DAG) | Declarative workflow chaining data cleaning, feature engineering, model training, and evaluation. |
| **Design State** | **Unsaved / Unexecuted YAML in Editor** | **Pipeline Draft** | Editable pipeline canvas. Costs \$0, consumes no compute, and is fully mutable. |
| **Execution Run** | **Pipeline Build Run** (`#20261115.1`) | **Job** (Pipeline Run) | Immutable execution record on compute. Holds run duration, console logs, accuracy metrics, and artifacts. |
| **Optimization** | **Matrix Build Strategy** (`strategy: matrix`) | **Automated ML (AutoML)** | Parallel evaluation sweep testing 50+ algorithms and hyperparameters simultaneously to find the best model. |
| **Generative AI** | **Release Gates & Pre-deployment Checks** | **Prompt Flow** | Directed graph orchestrating LLM prompts, Python code, vector search, and evaluation metrics before serving. |
| **Artifact Feed** | **Azure Artifacts / Universal Packages / ACR** | **Models (Model Registry)** | Catalog storing packaged model files (`model.pkl`, MLflow folder) tagged with semantic versions (`v1.0.0`). |
| **Production Serving** | **App Service with Deployment Slots** | **Online Endpoint** (Managed) | Low-latency REST API serving real-time predictions; supports blue/green traffic splitting (e.g., 90/10). |
| **Bulk Processing** | **Scheduled Cron Release / Background Agent** | **Batch Endpoint** | Asynchronous batch job scoring millions of records from Azure Blob Storage and saving results to Blob. |
| **Observability** | **App Insights Telemetry & Release Gates** | **Monitoring (Data & Model Drift)** | Continuous telemetry comparing production inference requests against baseline training data to detect drift. |

---

## 3. End-to-End Architectural Lifecycle Comparison

### Software Delivery (Azure DevOps)
```text
┌──────────────┐     ┌───────────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  Developer   │ ──► │  azure-pipelines.yml  │ ──► │   Azure Artifacts   │ ──► │  AKS / App Svc  │
│  Git Commit  │     │  (VMSS Agent Pool)    │     │  (NuGet / Container)│     │  (Blue / Green) │
└──────────────┘     └───────────────────────┘     └─────────────────────┘     └─────────────────┘
```

### Machine Learning Delivery (Azure Machine Learning)
```text
┌──────────────┐     ┌───────────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│ Code + Data  │ ──► │    AML Pipeline       │ ──► │   Model Registry    │ ──► │ Online Endpoint │
│ (SDK / Draft)│     │   (Compute Cluster)   │     │ (model.pkl v1.0.0)  │     │ (Traffic Split) │
└──────────────┘     └───────────────────────┘     └─────────────────────┘     └─────────────────┘
```

---

## 4. High-Yield Exam Distinctions (AI-300 / DP-100)

### A. Pipeline Draft vs. Pipeline Job

| Attribute | Pipeline Draft | Pipeline Job |
| :--- | :--- | :--- |
| **Location** | *Designer $\rightarrow$ Pipeline Drafts* | *Assets $\rightarrow$ Jobs* |
| **State** | **Mutable** (Editable canvas) | **Immutable** (Frozen historical execution) |
| **Compute Cost** | **\$0.00** (Metadata only) | **Billed per second/minute** while compute runs |
| **Outputs** | None (Blueprint only) | Logs (`70_driver_log.txt`), metrics, and trained model files |
| **Analogy** | **Unsent email in Drafts** | **Sent email in Outbox with delivery timestamp** |

### B. Compute Instance vs. Compute Cluster

| Feature | Compute Instance | Compute Cluster |
| :--- | :--- | :--- |
| **Target Workload** | Interactive development (Jupyter, VS Code) | Automated training jobs, hyperparameter sweeps |
| **Scaling** | Fixed 1 VM (Single-node only) | **Auto-scaling (Min Nodes = 0, Max Nodes = N)** |
| **Cost Optimization** | **Manual shutdown required** (or scheduled auto-stop) | **Automatically scales to 0 nodes** when queue is empty |
| **User Scope** | Assigned to a single named identity | Shared across team members and automated pipelines |

> [!IMPORTANT]
> **FinOps Exam Rule:** Always set `min_instances = 0` on AML Compute Clusters. This ensures the cluster drains and deallocates completely when no pipelines are executing, maintaining \$0.00 idle cost.

### C. Managed Online Endpoint vs. Batch Endpoint

| Feature | Managed Online Endpoint | Batch Endpoint |
| :--- | :--- | :--- |
| **Latency** | **Milliseconds** (Real-time REST API) | **Minutes to Hours** (Asynchronous bulk processing) |
| **Invocation** | Synchronous HTTP `POST` from web/mobile app | Triggered via CLI, REST API, or Azure Data Factory |
| **Input Source** | Single JSON payload in request body | Large CSV/Parquet files stored in Azure Blob / ADLS Gen2 |
| **Traffic Splitting**| Native Blue/Green (e.g., 90% traffic to `v1`, 10% to `v2`) | Not applicable (Batch runs to completion) |
| **Billing Model** | Dedicated compute allocated 24/7 (or autoscaling) | Compute spins up only for the duration of the batch job |

---

## 5. Enterprise MLOps CI/CD: Wiring Azure DevOps to Azure ML

In production, data scientists should never click "Submit" manually in Azure ML Studio. Changes in Git repositories automatically trigger Azure DevOps pipelines that communicate with Azure ML via the Azure CLI (`az ml`) using Workload Identity Federation (OIDC):

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ENTERPRISE CI/CD AUTOMATION ARCHITECTURE                                               │
│                                                                                        │
│   1. Git Commit (feature branch)                                                       │
│          │                                                                             │
│          ▼                                                                             │
│   2. Azure DevOps Pipeline Triggered                                                   │
│      ├── Step A: Lint & Unit Tests (`flake8`, `pytest`)                                │
│      ├── Step B: Validate AML Component YAML (`az ml component validate`)             │
│      └── Step C: Authenticate via Workload Identity Federation (OIDC)                  │
│          │                                                                             │
│          ▼                                                                             │
│   3. Dispatch Training Job to Azure ML                                                 │
│      └── Command: `az ml job create --file pipeline.yml --workspace-name ml-workspace` │
│          │                                                                             │
│          ▼                                                                             │
│   4. AML Compute Cluster Executes DAG                                                  │
│      └── Data Ingest ──► Train ──► Evaluate Accuracy                                   │
│          │                                                                             │
│          ▼ [Accuracy > 92% Threshold]                                                  │
│   5. Register Model & Promote                                                          │
│      └── Command: `az ml model create --name car-price --version 2.0.0`                │
│          │                                                                             │
│          ▼                                                                             │
│   6. Blue/Green Canary Deployment to Online Endpoint                                   │
│      ├── Deploy `v2` with `traffic: 10%`                                               │
│      ├── Monitor Error Rates via Azure Monitor (App Insights)                          │
│      └── Promote `v2` to `traffic: 100%`                                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Production Azure DevOps Task Example: Submitting AML Job
```yaml
- task: AzureCLI@2
  displayName: 'Submit Azure ML Training Pipeline'
  inputs:
    azureSubscription: 'sc-azure-mlops-prod'  # Service Connection (WIF OIDC)
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az extension add -n ml -y
      
      echo "Submitting Azure ML Pipeline Job..."
      RUN_ID=$(az ml job create \
        --file ./mlops/training-pipeline.yml \
        --resource-group rg-ht-ai300-p-cin-01 \
        --workspace-name ml-ai300-workspace \
        --query name -o tsv)
      
      echo "Submitted AML Job ID: $RUN_ID"
      echo "Streaming job logs to Azure DevOps console..."
      az ml job stream --name $RUN_ID --resource-group rg-ht-ai300-p-cin-01 --workspace-name ml-ai300-workspace
```

---

## 6. Pocket Revision Formula (Indian Exam Guide Style)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AI-300 / DP-100 60-SECOND REVISION CHEAT SHEET                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Compute Instance   = Dedicated Dev Machine (Runs Jupyter Notebooks).                │
│ 2. Compute Cluster    = VMSS Agent Pool (Auto-scales 0 -> N; set Min=0 for $0 idle).   │
│ 3. Connections        = Service Connections (Central secrets, zero hardcoded keys).    │
│ 4. Environment        = Docker Image + Conda (Runtime dependencies).                   │
│ 5. Component          = Reusable YAML Step Template (Parameterized task).              │
│ 6. Data Asset         = Git Commit SHA for Data (Immutable data versioning).           │
│ 7. Designer           = Classic Visual GUI Pipeline Editor.                            │
│ 8. Notebooks          = VS Code Code-First Scripting (Python SDK v2).                  │
│ 9. Pipeline           = Multi-Stage YAML Build (DAG with step caching).                │
│ 10. Draft vs Job      = Unsent Draft ($0) vs Immutable Build Run (Billed).             │
│ 11. Model Registry    = Azure Artifacts / Container Registry (Tagged model.pkl).       │
│ 12. Online Endpoint   = App Service Slot (Real-time REST API, Blue/Green traffic).     │
│ 13. Batch Endpoint    = Scheduled Release Job (Asynchronous bulk file scoring).        │
│ 14. Monitoring        = App Insights + Gate (Data Drift detection & retraining alerts).│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

$$\text{Data Asset} + \text{Environment} \xrightarrow{\text{Component DAG}} \text{Pipeline Draft} \xrightarrow{\text{Submit}} \text{Job (Compute)} \xrightarrow{\text{Register}} \text{Model} \xrightarrow{\text{Deploy}} \text{Endpoint}$$
