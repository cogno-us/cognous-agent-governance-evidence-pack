# Internal Research Assistant — Governance Evidence Pack

| Field | Value |
|---|---|
| Pack ID | ep-research-agent-2026-001 |
| Version | 0.1 |
| Generated At | 2026-07-01T10:00:00Z |
| Review Status | draft |
| Agent | InternalResearchAssistant |
| Environment | development |
| Owner | Head of Business Intelligence |
| Business Unit | Strategy and Analytics |

## 1. Executive Summary

**InternalResearchAssistant** is deployed in the **development** environment. Business purpose: Improve internal research productivity by searching and summarizing internal documents, files, and knowledge repositories on behalf of business analysts.

The agent has access to **3** tool(s) and can propose **3** action(s), of which **1** require authority or human review.

**1** replay bundle(s) are available (0 signed).
Validation summary: 1 valid bundle(s), 0 invalid, 0 error(s), 1 warning(s).

**2** open risk(s) (0 critical).

## 2. Agent Overview

**Agent Name:** InternalResearchAssistant

**Description:** Searches internal documents and file repositories, summarizes content, and prepares research summaries for business teams.

**Business Purpose:** Improve internal research productivity by searching and summarizing internal documents, files, and knowledge repositories on behalf of business analysts.

**Owner:** Head of Business Intelligence

**Business Unit:** Strategy and Analytics

**User Population:** Business analysts and strategy team members

**Lifecycle Stage:** pilot


## 3. Deployment Context

**Environment:** development

**Deployment Name:** research-agent-dev-v1

**Deployment Date:** 2026-06-01

**Systems Touched:** Internal Document Repository, File Search Service, Knowledge Base

**Data Domains:** internal-documents, strategy-materials, research-files

**Geographic Scope:** Global

**Notes:** Development deployment. Not yet approved for production use.


## 4. Tool Inventory

| Tool Name | Description | External System | Data Classification | Access Mode | Control Status |
|---|---|---|---|---|---|
| document_search | Search the internal document repository by keyword and metadata. | — | internal | read-only | implemented |
| file_read | Read the contents of individual files from the internal file system. | — | internal | read-only | implemented |
| export_summary | Export a research summary document to a shared drive or external destination. | Shared Drive | internal | write | partial |

## 5. Action Inventory

| Action Name | Tool | Type | Authority Required | Review Required | Reliance Required | Control Status |
|---|---|---|---|---|---|---|
| search_documents | document_search | read | No | No | Yes | implemented |
| read_file | file_read | read | No | No | Yes | implemented |
| export_research_summary | export_summary | export | No | Yes | No | partial |

## 6. Authority Model

No authority model recorded for this evidence pack.

## 7. Policy Controls

| Control Name | Description | Status | Evidence Reference |
|---|---|---|---|
| Human Review Gate for Export | All research summary exports require review and approval by the requesting analyst before delivery. | partial | — |
| Document Access Scoping | Document search is scoped to repositories accessible to the requesting user. | implemented | access-control-log-ep-research-001 |

## 8. Blocked-Action Summary

No blocked actions recorded.

## 9. Reliance Summary

A total of **146** reliance record(s) are recorded in this evidence pack.

| Source Name | Source Type | Count | Scope Summary | Evidence Reference |
|---|---|---|---|---|
| Internal Document Repository | document_store | 112 | 112 document searches conducted during development testing period. Content used for summary generation. | reliance-log-ep-research-001 |
| File Search Service | file_system | 34 | 34 file reads conducted for content summarization. | reliance-log-ep-research-002 |

## 10. Replay Bundle Inventory

| Bundle ID | Run ID | Status | Generated At | Signed | Redacted | Validation Status | Evidence Reference |
|---|---|---|---|---|---|---|---|
| rb-research-agent-2026-001-a | run-research-001 | available | 2026-06-30T12:00:00Z | No | No | valid | replay-store/rb-research-agent-2026-001-a |

## 11. Validation Summary

**Valid Bundles:** 1 | **Invalid Bundles:** 0 | **Errors:** 0 | **Warnings:** 1

One replay bundle validated. One warning regarding stale document sources.


## 12. Redaction and Export Summary

No redaction or export records recorded.

## 13. Risk Register

| Risk ID | Title | Severity | Status | Mitigation | Owner | Evidence Reference |
|---|---|---|---|---|---|---|
| risk-research-001 | Stale Source Material | medium | open | Document freshness metadata included in summaries where available. Analysts instructed to verify currency of key sources. | Head of Business Intelligence | — |
| risk-research-002 | Overbroad File Access | medium | open | Access scoping review planned. Requesting user access controls applied. | IT Security | — |

## 14. Review Records

No review records recorded.

## 15. Known Limitations

This evidence pack summarizes available runtime and governance records. It does not prove that model outputs are correct, that policies are sufficient, or that external compliance obligations have been satisfied.
