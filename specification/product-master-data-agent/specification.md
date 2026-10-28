# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md` at the solution root)
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using instructions from the sap-agent-bootstrap section (invoke from inside `assets/product-master-data-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> **Before proceeding**, read [guidelines-agent-skills.md](../guidelines-agent-skills.md) and decide whether the agent needs runtime skills.

- [x] Assess whether a runtime skill is needed for product data query handling (multi-entity queries, disambiguation of product identifiers, UoM/packaging lookup steps)
- [x] If a runtime skill is beneficial, create `assets/product-master-data-agent/app/skills/product-query/SKILL.md` with step-by-step instructions for handling product queries including clarification flow for ambiguous inputs

---

## Project-Specific Tasks

### REQ-01: Natural Language Product Description & Specification Lookup

- [x] Add system prompt instruction: the agent answers questions about product descriptions and technical specifications using only data retrieved from MCP tools — never fabricate product data
- [x] Add system prompt instruction: when a product identifier is ambiguous, ask the user to clarify before calling any tool
- [x] Implement agent logic to extract product ID or name from user query and call the product master MCP tool
- [x] Format the returned product description and specification fields into a clear, readable natural language response
- [x] Handle the case where no product is found: inform the user clearly without fabricating data

### REQ-02: Unit of Measure & Packaging Details Lookup

- [x] Implement agent logic to retrieve unit of measure and packaging details from the product master MCP tool (target entities: `A_ProductUOM`, `A_ProductUOMText`)
- [x] Format UoM and packaging results clearly, listing all available units for a given product
- [x] Handle products with multiple UoMs: present all variants, not just the base unit
- [x] Handle missing UoM data: communicate clearly that this information is not available in the system

### REQ-03: Product Classification & Category Queries

- [x] Implement agent logic to query product classification data via the product classification MCP tool (`API_CLFN_PRODUCT_SRV`)
- [x] Format classification and category results into a clear, readable response
- [x] Handle products with no classification data: inform the user explicitly

### REQ-04 & REQ-05: System Prompt — Scope Guardrails

- [x] Add system prompt guardrail: if the user asks about pricing, discounts, stock availability, or any data outside product master, respond that this is outside the agent's scope and suggest where they might find that information
- [x] Add system prompt instruction: the agent is read-only — it never writes, updates, or deletes any data in SAP S/4HANA
- [x] Add system prompt instruction: always set page size (`top`) to a maximum of 100 on any paginated tool call

### REQ-06: Graceful Handling of Missing or Incomplete Data

- [x] Implement response logic: when a tool returns partial data (some fields empty/null), the agent states what was found and what fields are missing — it does not fill gaps with assumptions
- [x] Add system prompt instruction: relay tool errors verbatim without suggestions or workarounds unless asked

---

## Data Dependencies

MCP API: `sap.s4:apiResource:API_PRODUCT_SRV:v1`
MCP tool scope: read-only
Resources in scope: `A_Product`, `A_ProductDescription`, `A_ProductUOM`, `A_ProductUOMText`, `A_ProductPlant`

MCP API: `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1`
MCP tool scope: read-only
Resources in scope: `A_ClfnProduct`, `A_ClfnProductClassAssignment`, `A_ClfnProductCharc`

---

## Business Instrumentation

- [x] Implement business step instrumentation for all four milestones from the PRD using structured logging and OpenTelemetry spans:
  - `M1.achieved: product description and specification query answered successfully`
  - `M1.missed: product description or specification query did not return a result`
  - `M2.achieved: unit of measure and packaging query answered successfully`
  - `M2.missed: unit of measure or packaging query did not return a result`
  - `M3.achieved: agent accessible via Joule and standalone web chat`
  - `M3.missed: one or both access channels are not operational`
  - `M4.achieved: agent successfully adopted — first live query logged for sales rep`
  - `M4.missed: no queries recorded for sales rep within one week of go-live`
- [x] Extract all business logic from `stream()` into a plain async helper (`_run_agent()`) and instrument that method — do NOT use `with tracer.start_as_current_span(...)` inside async generators
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) for complete MCP integration patterns.

- [x] Verify `specification/product-master-data-agent/api-specs/` contains both:
  - `API_PRODUCT_SRV.edmx`
  - `API_CLFN_PRODUCT_SRV.edmx`
- [x] Invoke `mcp-translation-file` skill for `API_PRODUCT_SRV.edmx` — outputs to `specification/product-master-data-agent/mcps/API_PRODUCT_SRV/`
- [x] Invoke `mcp-translation-file` skill for `API_CLFN_PRODUCT_SRV.edmx` — outputs to `specification/product-master-data-agent/mcps/API_CLFN_PRODUCT_SRV/`
- [x] Invoke `setup-solution` skill to create MCP server assets for both translation files
- [x] Extract the generated ORD IDs from each MCP server's `asset.yaml` — use exact values, never invent them
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — never import directly from `sap_cloud_sdk.agentgateway`
- [x] Add both MCP server dependencies to the agent's `asset.yaml` under `requires` (one entry per MCP server, using exact ORD IDs from generated assets)
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after translation files and MCP assets are created

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit tests in `assets/product-master-data-agent/tests/`:
  - One test for the product description & spec lookup tool
  - One test for the UoM & packaging lookup tool
  - One test for the product classification lookup tool
  - One test for the out-of-scope guardrail (pricing/stock query rejection)
  - One test for the missing data response (empty tool result)
- [x] Write one integration test executing the full agent flow: user asks a product spec question → agent calls MCP tool → agent formats and returns the answer (all with mocked LLM and mocked MCP tools)
- [x] Run `pytest` from `assets/product-master-data-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/product-master-data-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/product-master-data-agent/`
