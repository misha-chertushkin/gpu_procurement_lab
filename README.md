# 🛠️ Environment Setup

## Step 1: Login to Google Cloud with Adequate Scopes

See [FIX_GDRIVE_AUTH.md](/docs/FIX_GDRIVE_AUTH.md) for justification around scopes.

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform
```

## Step 2: Deploy Cloud Resources

Deploy Resources via Makefile:
```bash
make deploy project=YOUR_PROJECT_ID
```

## Step 3a: Run a Live Demo for a given Phase

To run a specific demo phase, use the **make run** target with the lab sub-folder sub-folder/phase input.

```bash
make run lab=YOUR_LAB_PHASE_FOLDER
```

For example, for labs/phase1:

```bash
make run lab=phase1
```

## Step 3b: Run a Headless Test for a given Phase

To run a headless test for a specific demo phase, use the **make test** target with the lab sub-folder/phase input.

```bash
make test lab=YOUR_LAB_PHASE_FOLDER
```

For example, for labs/phase1:

```bash
make test lab=phase1
```

## Step 3c: Run a Headless Batch Test for all Phases

To run a headless test for all phases, use the **make batch-test** target with the specific count.

```bash
make batch-test count=YOUR_LAB_PHASE_FOLDER
```

For example, for 10 test runs for each lab:

```bash
make batch-test count=10
```

## Step 4: Destroy Cloud Resources

Destroy Resources via Makefile:
```bash
make destroy
```

# 🛠️ Environment Phase Overview

## Common Cloud Infrastructure Resources

![Terraform Resources](/docs/terraform-graph.png)


## Phase 1 Agents and Tools

```mermaid
graph TD
    subgraph "Phase 1"
        root_agent_P1("root_agent");

        subgraph "Sub-Agents"
            inventory_agent_P1("inventory_agent");
            legal_agent_P1("legal_agent");
            logistics_agent_P1("logistics_agent");
            purchase_order_agent_P1("purchase_order_agent");
        end

        subgraph "Tools"
            CommanderTools_P1["fs.read_file, fs.write_file, fs.append_to_log, fs.list_files, gdrive.upload_file"];
            InventoryTools_P1["db.explore_schema, db.run_query"];
            LegalTools_P1["rag.analyze_contract_clause"];
            LogisticsTools_P1["api.fetch_spot_prices, api.estimate_shipping"];
            PurchaseOrderTools_P1["fs.read_file, fs.write_file, gdrive.upload_file"];
        end

        root_agent_P1 --> inventory_agent_P1;
        root_agent_P1 --> legal_agent_P1;
        root_agent_P1 --> logistics_agent_P1;
        root_agent_P1 --> purchase_order_agent_P1;

        root_agent_P1 --> CommanderTools_P1;
        inventory_agent_P1 --> InventoryTools_P1;
        legal_agent_P1 --> LegalTools_P1;
        logistics_agent_P1 --> LogisticsTools_P1;
        purchase_order_agent_P1 --> PurchaseOrderTools_P1;
    end
```

## Phase 2 Agents and Tools

```mermaid
graph TD
    subgraph "Phase 2"
        root_agent_P2("root_agent");

        subgraph "Orchestrators"
            source_gpus_agent("source_gpus_agent");
            source_gpus_parallel_agent("source_gpus_parallel_agent");
            source_gpus_merge_agent("source_gpus_merge_agent");
        end

        subgraph "Sub-Agents"
            inventory_agent_P2("inventory_agent");
            legal_agent_P2("legal_agent");
            logistics_agent_P2("logistics_agent");
        end

        subgraph "Tools"
            MergeTools_P2["fs.read_file, fs.write_file, fs.append_to_log, fs.list_files, gdrive.upload_file"];
            InventoryTools_P2["db.explore_schema, db.run_query"];
            LegalTools_P2["rag.analyze_contract_clause"];
            LogisticsTools_P2["api.fetch_spot_prices, api.estimate_shipping"];
        end

        root_agent_P2 --> source_gpus_agent;
        source_gpus_agent --> source_gpus_parallel_agent;
        source_gpus_agent --> source_gpus_merge_agent;

        source_gpus_parallel_agent --> inventory_agent_P2;
        source_gpus_parallel_agent --> legal_agent_P2;
        source_gpus_parallel_agent --> logistics_agent_P2;

        source_gpus_merge_agent --> MergeTools_P2;
        inventory_agent_P2 --> InventoryTools_P2;
        legal_agent_P2 --> LegalTools_P2;
        logistics_agent_P2 --> LogisticsTools_P2;
    end
```

## Phase 3 Agents and Tools

```mermaid
graph TD
    subgraph "Phase 3"
        a2a_root_agent_P3("a2a_root_agent (entry point)");
        
        subgraph "Discovered Agents"
            commander_agent_P3("commander_agent");
        end
        
        a2a_root_agent_P3 -- "Discovers & Invokes" --> commander_agent_P3;

        subgraph "Orchestrators"
            source_gpus_agent_P3("source_gpus_agent");
            source_gpus_parallel_agent_P3("source_gpus_parallel_agent");
            source_gpus_merge_agent_P3("source_gpus_sum_and_report_agent");
        end

        subgraph "Sub-Agents"
            inventory_agent_P3("inventory_agent");
            legal_agent_P3("legal_agent");
            logistics_agent_P3("logistics_agent");
        end

        subgraph "Tools"
            MergeTools_P3["fs.read_file, fs.write_file, fs.append_to_log, fs.list_files, gdrive.upload_file"];
            InventoryTools_P3["db.explore_schema, db.run_query"];
            LegalTools_P3["rag.analyze_contract_clause"];
            LogisticsTools_P3["api.fetch_spot_prices, api.estimate_shipping"];
        end

        commander_agent_P3 --> source_gpus_agent_P3;

        source_gpus_agent_P3 --> source_gpus_parallel_agent_P3;
        source_gpus_agent_P3 --> source_gpus_merge_agent_P3;

        source_gpus_parallel_agent_P3 --> inventory_agent_P3;
        source_gpus_parallel_agent_P3 --> legal_agent_P3;
        source_gpus_parallel_agent_P3 --> logistics_agent_P3;

        source_gpus_merge_agent_P3 --> MergeTools_P3;
        inventory_agent_P3 --> InventoryTools_P3;
        legal_agent_P3 --> LegalTools_P3;
        logistics_agent_P3 --> LogisticsTools_P3;
    end
```
