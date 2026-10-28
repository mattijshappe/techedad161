# Product Master Data AI Agent for Sales Representatives

AI agent that enables Sales Representatives to ask natural language questions about product master data from SAP S/4HANA Public Cloud Edition and receive instant, accurate answers.

## Business challenge

Sales Representatives waste time switching between multiple SAP screens to find product master data. There is no single, conversational interface to quickly retrieve product descriptions, specifications, units of measure, and packaging details — resulting in lost time and slower customer interactions.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to find product information | 5 minutes | Under 10 seconds | 3 months | Lead to Cash – Product Data Access | user |

## Key Milestones

1. **Product Q&A (descriptions & specs):** Agent can accurately answer questions about product descriptions and technical specifications from S/4HANA.
2. **UoM & Packaging Q&A:** Agent can accurately answer questions about units of measure and packaging details.
3. **Channel availability:** Agent is accessible via SAP Joule (embedded) and a standalone web chat interface.
4. **Go-live & adoption:** Agent is live and actively used by Sales Representatives in daily workflows.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash (E2E)

### Process Hierarchy

```
Lead to Cash (E2E)
└── Plan to Optimize Marketing and Sales (generic)
    └── Plan sales and manage performance (generic) [BPS-369]
        └── Develop sales forecast
        └── Access product master data for sales enablement
```

### Summary

Sales Reps querying product master data maps to the Lead to Cash end-to-end process under "Plan to Optimize Marketing and Sales". The core gap is a conversational AI interface over SAP S/4HANA product master data, which is not covered by standard sales planning capabilities.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
| ---------------------- | ----------------------- | ---------- | ----------------- | ------------------ | ------------------ | ------------------- | ---- | ------------------- |
| Natural language Q&A over product master data | None (custom agent required) | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | Yes | No pre-built AI agent for product master Q&A; custom Python agent needed |
| Product descriptions & specifications | SAP S/4HANA Cloud Public Edition – Sales Analytics (optional) | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | Yes | Product Master (A2X) OData API available; no MCP server — MCP translation file required |
| Units of measure & packaging | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | Yes | Covered by Product Master API (UoM entities); MCP translation file required |
| Product data incl. classification | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | — | No | Product Master Data Including Classification OData API is available |
| Access via SAP Joule | SAP Joule (A2A protocol) | — | — | — | — | — | No | A2A-compliant Python agent integrates with Joule natively |
| Standalone web chat access | Custom web UI | — | — | — | — | — | Yes | Lightweight web chat frontend needed alongside agent backend |

### Key findings

- Two relevant OData APIs are available in the SAP S/4HANA Cloud Public Edition landscape: `API_PRODUCT_SRV` (Product Master) and `API_CLFN_PRODUCT_SRV` (Product Master incl. Classification).
- No pre-built MCP servers exist for these APIs — custom MCP translation files must be generated as part of the solution.
- On-premise variants (`OP_API_PRODUCT_SRV_0001`, `OP_API_CLFN_PRODUCT_SRV`) are unavailable in this Public Cloud landscape and will not be used.
- The recommended approach is a pro-code Python AI agent (A2A protocol) that wraps the S/4HANA OData APIs via MCP tools.
- The agent will be surfaced both via SAP Joule and a standalone web chat interface.
- No n8n workflow orchestration is required — the agent handles all reasoning and tool calls autonomously.

## Recommendations

### AI Agent for Product Master Data Q&A

#### Executive Summary

Pro-code Python agent (A2A) over S/4HANA product OData APIs.

#### Recommended Solution

A Python-based AI agent following the A2A (Agent-to-Agent) protocol. The agent uses MCP tools backed by SAP S/4HANA Cloud Public Edition OData APIs (`API_PRODUCT_SRV` and `API_CLFN_PRODUCT_SRV`) to answer Sales Representative questions about product descriptions, specifications, units of measure, and packaging. The agent is deployed on SAP BTP and accessible via SAP Joule and a standalone web chat UI.

#### Problem Statement

Sales Representatives spend up to 5 minutes per product lookup navigating multiple SAP screens. This slows down customer conversations and reduces overall sales productivity.

#### Affected User Roles

- Sales Representatives
- Sales Managers (secondary — may use the agent for product portfolio overviews)

#### Important factors

##### Reduces manual effort through natural language access

Conversational interface eliminates the need for Sales Reps to navigate complex SAP transaction screens, reducing lookup time from ~5 minutes to under 10 seconds.

##### Leverages existing SAP S/4HANA investment

The solution reuses standard SAP S/4HANA Cloud Public Edition OData APIs without modifying the core system, keeping the solution clean and maintainable.

#### Potential risks

##### No pre-built MCP server — custom integration required

The OData APIs do not have pre-packaged MCP servers in this landscape, requiring custom MCP translation file generation. This adds a setup step but is a well-defined pattern.

##### Data quality dependency

Answer accuracy depends on the quality and completeness of product master data maintained in SAP S/4HANA. Incomplete records will lead to partial answers.

#### Recommended solution category

AI Agent

#### Intent fit
90%
