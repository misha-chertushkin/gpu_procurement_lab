# GPU Procurement Lab - Task Flow

Welcome to the GPU Procurement Lab! This guide will walk you through the tasks you need to complete to build a sophisticated, multi-agent system for procuring GPUs. The lab is divided into three phases, each introducing new concepts and challenges.

Good luck!

---

## Phase 1: The Monolithic Agent

In this phase, you'll work with a single, monolithic agent that uses multiple tools to accomplish its goal.

### 📌 Task 1.1: Implement Tool Selection in the Prompt
*   **File:** `labs/phase1/src/agent.py`
*   **Your Mission:** The agent's prompt has been redacted to remove explicit tool names. You need to edit the `PROMPT` variable to ensure the agent calls the correct tool for each step. Analyze the available tools and the agent's instructions to make the right choice.

### 📌 Task 1.2: Design the Executive Report
*   **File:** `labs/phase1/src/agent.py`
*   **Your Mission:** The formatting instructions for the `Executive_Report.md` have been removed from the prompt. Your task is to design a clear and effective report structure within the `PROMPT` that meets the procurement goal.

### 📌 Task 1.3: Provide Tools to the Agent
*   **File:** `labs/phase1/src/agent.py`
*   **Your Mission:** The list of tools passed to the agent's `generate_content` function has been cleared. You must inspect the imported tool classes and pass the complete list of tool functions to the agent.

### 📌 Task 1.4: Implement Tool Dispatch
*   **File:** `labs/phase1/src/agent.py`
*   **Your Mission:** The `match/case` block for dispatching function calls to the correct Python tool functions has been removed. Implement the logic to correctly route the model's function calls to the corresponding tool methods.

### 📌 Task 1.5: Format Tool Output
*   **File:** `labs/phase1/src/agent.py`
*   **Your Mission:** The line that wraps the tool's output into the required `types.Part.from_function_response` object has been replaced with a placeholder. Fix this line to ensure the tool's output is correctly formatted and returned to the model.

---

## Phase 2: The Multi-Agent System

In this phase, you'll refactor the monolithic agent into a hierarchical, multi-agent system.

### 📌 Task 2.1: Compose the Agent Hierarchy
*   **File:** `labs/phase2/src/agents/commander/agent.py`
*   **Your Mission:** The `sub_agents` list for the `root_agent` has been cleared. You need to connect the `source_gpus_agent` as a sub-agent to the commander agent to establish the hierarchy.

### 📌 Task 2.2: Delegate to Sub-Agents
*   **File:** `labs/phase2/src/agents/commander/agent.py`
*   **Your Mission:** The explicit delegation instruction in the `COMMANDER_SYSTEM_PROMPT` has been redacted. Modify the prompt to correctly delegate the task of finding GPUs to the appropriate sub-agent.

### 📌 Task 2.3: Implement Parallel Execution
*   **File:** `labs/phase2/src/agents/source_gpus/agent.py`
*   **Your Mission:** The `ParallelAgent` definition has been replaced with `None`. Implement the `ParallelAgent` to run the `inventory_agent`, `legal_agent`, and `logistics_agent` in parallel for efficient data gathering.

### 📌 Task 2.4: Implement Sequential Execution
*   **File:** `labs/phase2/src/agents/source_gpus/agent.py`
*   **Your Mission:** The `SequentialAgent` definition at the end of the `create_agent` function has been replaced with `None`. Implement the `SequentialAgent` to chain the parallel agent and the merge agent together, creating a complete workflow.

### 📌 Task 2.5: Pass Data Between Agents
*   **File:** `labs/phase2/src/agents/source_gpus/agent.py`
*   **Your Mission:** The `DATA INPUTS` section in the `source_gpus_merge_agent`'s prompt has been redacted. You need to add the correct placeholders (e.g., `{agent_name_result}`) to pass the output from the parallel agents to the merge agent.

---

## Phase 3: Agent-to-Agent (A2A) Communication

In this final phase, you'll enable dynamic agent discovery and communication using the Agent-to-Agent (A2A) protocol.

### 📌 Task 3.1: Expose an Agent as a Service
*   **File:** `labs/phase3/src/agents/commander/app.py`
*   **Your Mission:** The code that creates and runs the Flask app for the commander agent has been removed. Implement the necessary code to expose the agent as a web service, making it discoverable by other agents.

### 📌 Task 3.2: Discover Remote Agents
*   **File:** `labs/phase3/src/agents/a2a_root/agent.py`
*   **Your Mission:** The call to the `get_remote_agents` function has been replaced with an empty list. Implement the logic to retrieve agent "cards" from GCS and use them to create remote agent proxy objects.

### 📌 Task 3.3: Dynamically Build the Prompt
*   **File:** `labs/phase3/src/agents/a2a_root/agent.py`
*   **Your Mission:** The `for` loop that dynamically builds the agent's prompt from the discovered agents has been removed. Implement this loop to create an adaptive prompt that reflects the agent's runtime capabilities.

### 📌 Task 3.4: Register Discovered Agents
*   **File:** `labs/phase3/src/agents/a2a_root/agent.py`
*   **Your Mission:** The `sub_agents` parameter in the `root_agent`'s definition is empty. Dynamically register the discovered remote agent proxies with the `root_agent` to make them available for orchestration.

### 📌 Task 3.5: Implement Dynamic Delegation
*   **File:** `labs/phase3/src/agents/commander/agent.py`
*   **Your Mission:** The `COMMANDER_SYSTEM_PROMPT` for the Phase 3 commander is a copy of the Phase 2 prompt. Modify it to give a general instruction to use its sub-agents without mentioning any specific agent names, relying on the A2A discovery mechanism.

---

## 🤫 Facilitator's Guide

This section provides hints for each task.

### Phase 1 Hints
*   **Task 1.1:** The student needs to look at the imported tool modules (`LogisticsTools`, `DatabaseTools`, etc.) to see the available function names and match them to the instructions in the prompt.
*   **Task 1.2:** Encourage the student to think about what information is critical for an executive summary. Key elements are the number of GPUs requested, found, and needing to be ordered, and the total cost.
*   **Task 1.3:** The student should gather all the public methods from the instantiated tool objects (`logistics`, `database`, `filesystem`, `contract`, `google_drive`) and put them in the `tools` list.
*   **Task 1.4:** The student should replicate the `match/case` structure, mapping the function call name from the model's response to the correct Python function in the tool instances.
*   **Task 1.5:** Remind the student to check the `google-genai` documentation or the surrounding code for the correct way to wrap a function response. The solution is `types.Part.from_function_response(name=fc_part.function_call.name, response={'result': result})`.

### Phase 2 Hints
*   **Task 2.1:** The student needs to import `create_agent as create_agent_source_gpus_agent` and then add `create_agent_source_gpus_agent()` to the `sub_agents` list of the `root_agent`.
*   **Task 2.2:** The student should change the prompt to be more generic, like "Use your sub-agents to find H100 GPUs." The key is to remove the hardcoded "Ask Source GPUs Agent".
*   **Task 2.3:** The student should instantiate `ParallelAgent` and pass the `inventory_agent`, `legal_agent`, and `logistics_agent` to its `sub_agents` parameter.
*   **Task 2.4:** The student needs to return a `SequentialAgent` instance, passing the `source_gpus_parallel_agent` and `source_gpus_merge_agent` in the correct order to the `sub_agents` parameter.
*   **Task 2.5:** The student needs to add the `DATA INPUTS` section back to the prompt, using the correct placeholders: `{inventory_agent_result}`, `{legal_agent_result}`, and `{logistics_agent_result}`.

### Phase 3 Hints
*   **Task 3.1:** The student needs to use the `to_a2a` function to create the app and then use `uvicorn` to run it, similar to the other agent `app.py` files in the project. They will also need to implement the `startup` event to publish the agent card.
*   **Task 3.2:** The student should call `retrieve_agent_cards()` with the `agent_card_bucket_name` and then pass the result to `get_remote_agents()`.
*   **Task 3.3:** The student needs to write a `for` loop that iterates over the `remote_agents` list and appends a formatted string containing the agent's name and description to the `instructions` list.
*   **Task 3.4:** The student should pass `sub_agents=[*remote_agents]` to the `Agent` constructor.
*   **Task 3.5:** The student should remove the specific instruction "Ask Source GPUs Agent..." and replace it with a more general instruction to delegate to sub-agents based on their descriptions. This demonstrates the power of dynamic discovery.