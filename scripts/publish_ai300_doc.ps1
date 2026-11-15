param (
    [string]$email = "richtextforganesh@outlook.com",
    [string]$token = "ATATT3xFfGF0VUq_G0ygfsFliV_vLGDj6XTE7eNy4J4xE7wf31zRpzg138Gw3T68pnhaiQDL5XjBNVkjc7nhPldRhj_kRh65jWdCn6GFu6YZPAr1nMoOa1LogcaUK-GOh3PV7SN9PKDbT371CfZYpfL8bpVtRw7Z4Jex1-7E_x7yWEyMMmLq8Ao=FEFBEB92"
)

$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${email}:${token}"))
$headers = @{
    "Authorization" = "Basic $base64Auth"
    "Content-Type"  = "application/json; charset=utf-8"
    "Accept"        = "application/json"
}

$spaceKey = "HT"

# 1. Check or Create Parent Page: "AI 300 Training & Certification Hub"
$searchUrl = "https://happytechies.atlassian.net/wiki/rest/api/content?spaceKey=$spaceKey&title=AI+300+Training+%26+Certification+Hub&expand=version"
$existingParent = Invoke-RestMethod -Uri $searchUrl -Headers $headers -Method Get

$parentContent = @'
<ac:structured-macro ac:name="info">
    <ac:parameter ac:name="title">AI-300 Azure Machine Learning Operations Engineer Exam Track</ac:parameter>
    <ac:rich-text-body>
        <p>This root folder contains comprehensive training modules, architecture deep-dives, cheat sheets, and hands-on operational runbooks for passing the <strong>AI-300 / DP-100 Azure Machine Learning Operations Engineer</strong> certification and operating enterprise MLOps platforms.</p>
    </ac:rich-text-body>
</ac:structured-macro>

<h2>Certification Modules &amp; Study Runbooks</h2>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Module #</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Specification Document</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Focus Area</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>18</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">
                <ac:link><ri:page ri:content-title="18. AI-300: Azure Machine Learning &amp; MLOps for DevOps Engineers" /><ac:plain-text-link-body><![CDATA[18. AI-300: Azure Machine Learning & MLOps for DevOps Engineers]]></ac:plain-text-link-body></ac:link>
            </td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Rosetta Stone (ADO vs AML), Pipeline Caching, Draft vs Job, Blue/Green Endpoints, Exam Cheat Sheet</td>
        </tr>
    </tbody>
</table>

<hr />
<h3>Key Certification Pillars</h3>
<ul>
    <li><strong>Pillar 1:</strong> Azure ML Workspaces, Compute Clusters (Min=0), Environments, and Data Assets</li>
    <li><strong>Pillar 2:</strong> Pipeline Architecture, Step Caching, and MLflow Experiment Tracking</li>
    <li><strong>Pillar 3:</strong> Model Registry, Lineage, and Version Governance</li>
    <li><strong>Pillar 4:</strong> Managed Online Endpoints (Real-Time + Canary Traffic Splitting) &amp; Batch Endpoints</li>
    <li><strong>Pillar 5:</strong> Enterprise MLOps CI/CD via Azure DevOps &amp; Data Drift Observability</li>
</ul>
'@

if ($existingParent.results.Count -gt 0) {
    $parentId = $existingParent.results[0].id
    $parentVer = $existingParent.results[0].version.number
    Write-Host "Updating existing Parent Root page: $parentId (Version $($parentVer + 1))..."
    $updateBody = @{
        version = @{ number = $parentVer + 1 }
        title   = "AI 300 Training & Certification Hub"
        type    = "page"
        space   = @{ key = $spaceKey }
        body    = @{
            storage = @{
                value          = $parentContent
                representation = "storage"
            }
        }
    } | ConvertTo-Json -Depth 10

    $parentResp = Invoke-RestMethod -Uri "https://happytechies.atlassian.net/wiki/rest/api/content/$parentId" -Headers $headers -Method Put -Body ([System.Text.Encoding]::UTF8.GetBytes($updateBody))
} else {
    Write-Host "Creating Parent Root page: AI 300 Training & Certification Hub..."
    $createBody = @{
        title     = "AI 300 Training & Certification Hub"
        type      = "page"
        space     = @{ key = $spaceKey }
        ancestors = @(@{ id = "98562" })
        body      = @{
            storage = @{
                value          = $parentContent
                representation = "storage"
            }
        }
    } | ConvertTo-Json -Depth 10

    $parentResp = Invoke-RestMethod -Uri "https://happytechies.atlassian.net/wiki/rest/api/content" -Headers $headers -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($createBody))
    $parentId = $parentResp.id
}

Write-Host "Parent Root Page ID: $parentId"

# 2. Read Markdown Document 18 and convert to Confluence Storage XHTML
$mdPath = "docs/confluence/18-ai300-azure-mlops-for-devops-engineers.md"
$mdText = Get-Content -Path $mdPath -Raw -Encoding UTF8

# Extract title
$title = "18. AI-300: Azure Machine Learning & MLOps for DevOps Engineers"

# Build Storage XHTML
$xhtml = @'
<ac:structured-macro ac:name="info">
    <ac:parameter ac:name="title">AI-300 Certification Guide &amp; Operational Runbook</ac:parameter>
    <ac:rich-text-body>
        <p><strong>Space:</strong> HappyTechies Cloud &amp; AI Platform | <strong>Target Audience:</strong> Azure DevOps Engineers, Cloud Platform Architects, MLOps Practitioners, AI-300 Exam Candidates</p>
        <p><strong>Status:</strong> ACTIVE / CERTIFICATION GUIDE | <strong>Exam Track:</strong> AI-300 / DP-100</p>
    </ac:rich-text-body>
</ac:structured-macro>

<h2>1. Executive Summary &amp; Paradigm Shift</h2>
<p>As an <strong>Azure DevOps (ADO) Engineer</strong>, you already understand 90% of the principles governing <strong>Machine Learning Operations (MLOps)</strong>. Both disciplines solve the identical operational problem: <em>taking an artifact developed locally and delivering it reliably, repeatably, securely, and automatically into production cloud infrastructure.</em></p>

<p>The only fundamental difference is the artifact being compiled:</p>

<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">none</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[+----------------------------------------------------------------------------------------+
| TRADITIONAL SOFTWARE CI/CD (Azure DevOps)                                              |
|                                                                                        |
|     [ Source Code ]  ---( Compile & Build )--->  [ Binary / Docker Image / NuGet ]     |
|       (C# / TS)          (azure-pipelines.yml)         (Deployed to AKS / App Service) |
+----------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------+
| ENTERPRISE MLOps (Azure Machine Learning)                                              |
|                                                                                        |
|     [ Code + Versioned Data ] ---( Train & Evaluate )--->  [ Model Weights Artifact ]  |
|        (Python + Parquet)            (AML Pipeline DAG)          (model.pkl / ONNX)    |
|                                                                  (Deployed to Endpoint)|
+----------------------------------------------------------------------------------------+]]></ac:plain-text-body>
</ac:structured-macro>

<p>In software engineering, code is deterministic: compiling <code>commit abc123</code> always generates the exact same binary. In machine learning, running <code>train.py</code> on Monday produces a <strong>completely different model</strong> if the database received 50,000 new rows on Tuesday. MLOps is simply DevOps extended to version <strong>Data</strong>, track <strong>Experiments</strong>, and monitor <strong>Model Accuracy &amp; Drift</strong>.</p>

<hr />

<h2>2. Master Rosetta Stone: Azure DevOps vs. Azure Machine Learning</h2>
<p>Exhaustive 1-to-1 mapping between familiar Azure DevOps constructs and Azure Machine Learning Studio components:</p>

<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Category</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Azure DevOps (ADO) Construct</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Azure Machine Learning (AML) Equivalent</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Architectural Purpose &amp; Exact Parallel</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Governance</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>ADO Project</strong> (<code>dev.azure.com/org/proj</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>AML Workspace</strong> (<code>ml-ai300-workspace</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Central security boundary, RBAC container, and root hub for all assets, history, and compute.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Identity &amp; Auth</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Service Connection</strong> (ARM / SPN / OIDC)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Connections &amp; Datastores</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Centralized storage for SPNs, SAS tokens, and credentials; eliminates hardcoded API keys in code.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Workstation</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Dev VM / Jumpbox / Cloud Workstation</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Compute Instance</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Dedicated single-user VM for interactive development, debugging, and running Jupyter Notebooks.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Agent Pool</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>VMSS Self-Hosted Agent Pool</strong> (Min=0)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Compute Cluster</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Scalable multi-node VM pool. Sits at 0 nodes when idle ($0 cost) and scales up to N nodes on job arrival.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Base Image</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Agent Container</strong> (<code>container: image:v1</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Environment</strong> (Docker + Conda)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Immutable container image + requirements.txt defining runtime dependencies (Python, CUDA, PyTorch).</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Reusable Tasks</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>YAML Step Template</strong> (<code>template: step.yml</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Component</strong> (<code>component.yaml</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Modular, parameterized, reusable pipeline building block with strict typed inputs and outputs.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Source Control</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Git Repo Commit SHA</strong> (<code>git checkout</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Code + Data Asset</strong> (Versioned Data)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Snapshot pointer (<code>azureml:sales:v2</code>) ensuring exact data reproducibility across historical runs.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Visual Authoring</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Classic Pipeline Editor</strong> (Visual GUI)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Designer</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Drag-and-drop canvas for building ML pipelines without writing Python code.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Code Authoring</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>VS Code / Local Git Repository</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Notebooks</strong> (JupyterLab)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Code-first editor for writing training scripts using the Azure ML Python SDK v2 (<code>azure-ai-ml</code>).</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Orchestration</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Multi-stage Pipeline</strong> (<code>azure-pipelines.yml</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Azure ML Pipeline</strong> (DAG)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Declarative workflow chaining data cleaning, feature engineering, model training, and evaluation.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Design State</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Unsaved / Unexecuted YAML in Editor</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Pipeline Draft</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Editable pipeline canvas. Costs $0, consumes no compute, and is fully mutable.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Execution Run</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Pipeline Build Run</strong> (<code>#20261115.1</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Job</strong> (Pipeline Run)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Immutable execution record on compute. Holds run duration, console logs, accuracy metrics, and artifacts.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Optimization</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Matrix Build Strategy</strong> (<code>strategy: matrix</code>)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Automated ML (AutoML)</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Parallel sweep testing 50+ algorithms and hyperparameters simultaneously to find the best model.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Generative AI</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Release Gates &amp; Pre-deployment Checks</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Prompt Flow</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Directed graph orchestrating LLM prompts, Python code, vector search, and evaluation metrics.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Artifact Feed</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Azure Artifacts / Universal Packages / ACR</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Models (Model Registry)</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Catalog storing packaged model files (<code>model.pkl</code>, MLflow folder) tagged with semver (<code>v1.0.0</code>).</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Production Serving</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>App Service with Deployment Slots</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Online Endpoint</strong> (Managed)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Low-latency REST API serving real-time predictions; supports blue/green traffic splitting (e.g., 90/10).</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Bulk Processing</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Scheduled Cron Release / Background Agent</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Batch Endpoint</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Asynchronous batch job scoring millions of records from Azure Blob Storage and saving results to Blob.</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Observability</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>App Insights Telemetry &amp; Release Gates</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Monitoring (Data &amp; Model Drift)</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Continuous telemetry comparing production inference requests against baseline training data to detect drift.</td>
        </tr>
    </tbody>
</table>

<hr />

<h2>3. End-to-End Architectural Lifecycle Comparison</h2>

<h3>Software Delivery (Azure DevOps)</h3>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">none</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[+--------------+     +-----------------------+     +---------------------+     +-----------------+
|  Developer   | --> |  azure-pipelines.yml  | --> |   Azure Artifacts   | --> |  AKS / App Svc  |
|  Git Commit  |     |  (VMSS Agent Pool)    |     |  (NuGet / Container)|     |  (Blue / Green) |
+--------------+     +-----------------------+     +---------------------+     +-----------------+]]></ac:plain-text-body>
</ac:structured-macro>

<h3>Machine Learning Delivery (Azure Machine Learning)</h3>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">none</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[+--------------+     +-----------------------+     +---------------------+     +-----------------+
| Code + Data  | --> |    AML Pipeline       | --> |   Model Registry    | --> | Online Endpoint |
| (SDK / Draft)|     |   (Compute Cluster)   |     | (model.pkl v1.0.0)  |     | (Traffic Split) |
+--------------+     +-----------------------+     +---------------------+     +-----------------+]]></ac:plain-text-body>
</ac:structured-macro>

<hr />

<h2>4. High-Yield Exam Distinctions (AI-300 / DP-100)</h2>

<h3>A. Pipeline Draft vs. Pipeline Job</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Attribute</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Pipeline Draft</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Pipeline Job</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Location</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><em>Designer -> Pipeline Drafts</em></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><em>Assets -> Jobs</em></td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>State</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Mutable</strong> (Editable canvas)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Immutable</strong> (Frozen historical execution)</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Compute Cost</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>$0.00</strong> (Metadata only)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Billed per second/minute</strong> while compute runs</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Outputs</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">None (Blueprint only)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Logs (<code>70_driver_log.txt</code>), metrics, and trained model files</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Analogy</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Unsent email in Drafts</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Sent email in Outbox with delivery timestamp</strong></td>
        </tr>
    </tbody>
</table>

<h3>B. Compute Instance vs. Compute Cluster</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Feature</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Compute Instance</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Compute Cluster</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Target Workload</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Interactive development (Jupyter, VS Code)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Automated training jobs, hyperparameter sweeps</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Scaling</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Fixed 1 VM (Single-node only)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Auto-scaling (Min Nodes = 0, Max Nodes = N)</strong></td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Cost Optimization</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Manual shutdown required</strong> (or scheduled auto-stop)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Automatically scales to 0 nodes</strong> when queue is empty</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>User Scope</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Assigned to a single named identity</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Shared across team members and automated pipelines</td>
        </tr>
    </tbody>
</table>

<ac:structured-macro ac:name="tip">
    <ac:parameter ac:name="title">FinOps Golden Rule for Exam</ac:parameter>
    <ac:rich-text-body>
        <p>Always set <code>min_instances = 0</code> on AML Compute Clusters. This ensures the cluster drains and deallocates completely when no pipelines are executing, maintaining $0.00 idle cost.</p>
    </ac:rich-text-body>
</ac:structured-macro>

<h3>C. Managed Online Endpoint vs. Batch Endpoint</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Feature</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Managed Online Endpoint</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Batch Endpoint</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Latency</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Milliseconds</strong> (Real-time REST API)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Minutes to Hours</strong> (Asynchronous bulk processing)</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Invocation</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Synchronous HTTP <code>POST</code> from web/mobile app</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Triggered via CLI, REST API, or Azure Data Factory</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Input Source</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Single JSON payload in request body</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Large CSV/Parquet files stored in Azure Blob / ADLS Gen2</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Traffic Splitting</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Native Blue/Green (e.g., 90% traffic to v1, 10% to v2)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Not applicable (Batch runs to completion)</td>
        </tr>
    </tbody>
</table>

<hr />

<h2>5. Enterprise MLOps CI/CD: Wiring Azure DevOps to Azure ML</h2>
<p>Production Azure DevOps YAML task running <code>az ml job create</code> using Workload Identity Federation (OIDC):</p>

<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">yaml</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[- task: AzureCLI@2
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
      az ml job stream --name $RUN_ID --resource-group rg-ht-ai300-p-cin-01 --workspace-name ml-ai300-workspace]]></ac:plain-text-body>
</ac:structured-macro>

<hr />

<h2>6. Pocket Revision Formula (Indian Exam Guide Style)</h2>
<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">none</ac:parameter>
<ac:parameter ac:name="theme">Midnight</ac:parameter>
<ac:plain-text-body><![CDATA[+----------------------------------------------------------------------------------------+
|                        AI-300 / DP-100 60-SECOND REVISION CHEAT SHEET                  |
+----------------------------------------------------------------------------------------+
| 1. Compute Instance   = Dedicated Dev Machine (Runs Jupyter Notebooks).                |
| 2. Compute Cluster    = VMSS Agent Pool (Auto-scales 0 -> N; set Min=0 for $0 idle).   |
| 3. Connections        = Service Connections (Central secrets, zero hardcoded keys).    |
| 4. Environment        = Docker Image + Conda (Runtime dependencies).                   |
| 5. Component          = Reusable YAML Step Template (Parameterized task).              |
| 6. Data Asset         = Git Commit SHA for Data (Immutable data versioning).           |
| 7. Designer           = Classic Visual GUI Pipeline Editor.                            |
| 8. Notebooks          = VS Code Code-First Scripting (Python SDK v2).                  |
| 9. Pipeline           = Multi-Stage YAML Build (DAG with step caching).                |
| 10. Draft vs Job      = Unsent Draft ($0) vs Immutable Build Run (Billed).             |
| 11. Model Registry    = Azure Artifacts / Container Registry (Tagged model.pkl).       |
| 12. Online Endpoint   = App Service Slot (Real-time REST API, Blue/Green traffic).     |
| 13. Batch Endpoint    = Scheduled Release Job (Asynchronous bulk file scoring).        |
| 14. Monitoring        = App Insights + Gate (Data Drift detection & retraining alerts).|
+----------------------------------------------------------------------------------------+]]></ac:plain-text-body>
</ac:structured-macro>
'@

# 3. Check or Create Child Document 18
$searchDocUrl = "https://happytechies.atlassian.net/wiki/rest/api/content?spaceKey=$spaceKey&title=18.+AI-300%3A+Azure+Machine+Learning+%26+MLOps+for+DevOps+Engineers&expand=version"
$existingDoc = Invoke-RestMethod -Uri $searchDocUrl -Headers $headers -Method Get

if ($existingDoc.results.Count -gt 0) {
    $docId = $existingDoc.results[0].id
    $docVer = $existingDoc.results[0].version.number
    Write-Host "Updating Document 18: $docId (Version $($docVer + 1))..."
    $updateDocBody = @{
        version   = @{ number = $docVer + 1 }
        title     = $title
        type      = "page"
        space     = @{ key = $spaceKey }
        ancestors = @(@{ id = $parentId })
        body      = @{
            storage = @{
                value          = $xhtml
                representation = "storage"
            }
        }
    } | ConvertTo-Json -Depth 10

    $docResp = Invoke-RestMethod -Uri "https://happytechies.atlassian.net/wiki/rest/api/content/$docId" -Headers $headers -Method Put -Body ([System.Text.Encoding]::UTF8.GetBytes($updateDocBody))
    Write-Host "Document 18 updated successfully!"
} else {
    Write-Host "Creating Document 18 under Parent $parentId..."
    $createDocBody = @{
        title     = $title
        type      = "page"
        space     = @{ key = $spaceKey }
        ancestors = @(@{ id = $parentId })
        body      = @{
            storage = @{
                value          = $xhtml
                representation = "storage"
            }
        }
    } | ConvertTo-Json -Depth 10

    $docResp = Invoke-RestMethod -Uri "https://happytechies.atlassian.net/wiki/rest/api/content" -Headers $headers -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($createDocBody))
    $docId = $docResp.id
    Write-Host "Document 18 created successfully with ID: $docId!"
}

Write-Host "================================================================="
Write-Host "SUCCESS! Live URLs:"
Write-Host "Parent Hub: https://happytechies.atlassian.net/wiki/spaces/$spaceKey/pages/$parentId"
Write-Host "Doc 18:     https://happytechies.atlassian.net/wiki/spaces/$spaceKey/pages/$docId"
Write-Host "================================================================="
