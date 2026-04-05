# Data Processing Pipeline

<cite>
**Referenced Files in This Document**
- [build_index.py](file://build_index.py)
- [main.py](file://main.py)
- [data/master/stocks_master.json](file://data/master/stocks_master.json)
- [data/sentiment/company_mentions.json.backup](file://data/sentiment/company_mentions.json.backup)
- [trigger_deploy.sh](file://trigger_deploy.sh)
- [requirements.txt](file://requirements.txt)
- [Procfile](file://Procfile)
- [.railway.json](file://.railway.json)
- [merge_email_data.py](file://merge_email_data.py)
- [README.md](file://README.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the end-to-end data processing pipeline that transforms raw sentiment data into a compressed, searchable index for the Railway-hosted stock research application. It covers:
- Loading and merging master stock metadata with sentiment mentions
- Text cleaning and normalization while preserving multi-source content separators
- Field extraction supporting both nested llm_summary and direct field formats
- Article merging and deduplication
- Concept index generation for fast filtering
- Detail text generation for front-end display optimization
- Gzip compression and JSON serialization
- Automated Git workflow to commit and push changes to trigger Railway deployment
- Performance, memory optimization, error handling, validation, transformation rules, and quality assurance

## Project Structure
The pipeline centers around a dedicated script that builds a gzipped JSON index from two primary data sources:
- Master stock metadata: [data/master/stocks_master.json](file://data/master/stocks_master.json)
- Sentiment mentions: [data/sentiment/company_mentions.json.backup](file://data/sentiment/company_mentions.json.backup)

The Flask app consumes this index for search and display, and a separate script triggers deployments to Railway.

```mermaid
graph TB
A["Master Data<br/>data/master/stocks_master.json"]
B["Sentiment Mentions<br/>data/sentiment/company_mentions.json.backup"]
C["Index Builder<br/>build_index.py"]
D["Search Index<br/>data/sentiment/search_index_full.json.gz"]
E["Flask App<br/>main.py"]
F["Railway Deployment<br/>.railway.json + Procfile"]
G["Git Trigger Script<br/>trigger_deploy.sh"]
A --> C
B --> C
C --> D
D --> E
E --> F
G --> F
```

**Diagram sources**
- [build_index.py:77-271](file://build_index.py#L77-L271)
- [main.py:94-105](file://main.py#L94-L105)
- [.railway.json:1-15](file://.railway.json#L1-L15)
- [Procfile:1-2](file://Procfile#L1-L2)
- [trigger_deploy.sh:1-25](file://trigger_deploy.sh#L1-L25)

**Section sources**
- [build_index.py:11-14](file://build_index.py#L11-L14)
- [main.py:23-26](file://main.py#L23-L26)

## Core Components
- Index builder: Loads master and sentiment data, cleans and normalizes text, extracts fields, merges articles, generates concept index, creates detail texts, serializes to gzipped JSON, and triggers Git push to deploy.
- Flask app: Loads the gzipped index, exposes search and API endpoints, and serves the UI.
- Deployment automation: Git commit/push and Railway configuration.

Key responsibilities:
- Data ingestion and validation
- Text normalization and preservation of multi-source separators
- Field extraction with fallback logic
- Deduplication and merging
- Concept index creation
- Front-end detail text assembly
- Compression and serialization
- Git-triggered deployment

**Section sources**
- [build_index.py:77-271](file://build_index.py#L77-L271)
- [main.py:94-105](file://main.py#L94-L105)

## Architecture Overview
The pipeline follows a batch processing model:
1. Load master stock metadata and sentiment mentions
2. Normalize and clean text content
3. Extract fields from either nested llm_summary or direct fields
4. Merge sentiment articles into master records with deduplication
5. Build concept index mapping concept names to stock codes
6. Generate detail_texts for front-end presentation
7. Serialize to gzipped JSON for efficient serving
8. Commit and push changes to trigger Railway deployment

```mermaid
sequenceDiagram
participant Loader as "Index Builder"
participant Master as "Master Data"
participant Mentions as "Sentiment Mentions"
participant Cleaner as "Text Cleaner"
participant Merger as "Article Merger"
participant Concepts as "Concept Indexer"
participant Serializer as "Gzip + JSON"
participant Git as "Git Push"
participant Railway as "Railway"
Loader->>Master : Load stocks_master.json
Loader->>Mentions : Load company_mentions.json
Loader->>Cleaner : Clean titles, contexts, insights, accidents
Cleaner-->>Loader : Normalized text
Loader->>Merger : Merge and deduplicate articles
Merger-->>Loader : Merged articles
Loader->>Concepts : Build concept -> codes mapping
Concepts-->>Loader : Concepts dict
Loader->>Serializer : Compress and serialize index
Serializer-->>Loader : search_index_full.json.gz
Loader->>Git : Add, commit, push
Git->>Railway : Trigger redeploy
```

**Diagram sources**
- [build_index.py:77-271](file://build_index.py#L77-L271)

## Detailed Component Analysis

### Text Cleaning and Normalization
The cleaning function removes Markdown/HTML formatting while preserving multi-source content separators. It:
- Handles arrays by joining with commas
- Detects multi-source markers and temporarily protects them
- Removes citations, Markdown links, images, bare URLs, and HTML tags
- Restores multi-source separators after cleaning
- Normalizes whitespace otherwise

```mermaid
flowchart TD
Start(["clean_text(text)"]) --> CheckEmpty{"Is text empty?"}
CheckEmpty --> |Yes| ReturnEmpty["Return empty string"]
CheckEmpty --> |No| IsList{"Is text a list?"}
IsList --> |Yes| JoinList["Join non-empty items with commas"]
IsList --> |No| IsString{"Is text a string?"}
JoinList --> ReturnCleaned["Return cleaned string"]
IsString --> |No| ToString["Convert to string"]
ToString --> Continue["Continue cleaning"]
IsString --> |Yes| Continue
Continue --> DetectMulti{"Contains multi-source markers?"}
DetectMulti --> |Yes| ProtectSep["Temporarily replace separators"]
DetectMulti --> |No| RemoveTags["Remove citations, links, images, URLs, HTML"]
ProtectSep --> RemoveTags
RemoveTags --> RestoreSep{"Was separator protected?"}
RestoreSep --> |Yes| Restore["Restore separators"]
RestoreSep --> |No| NormalizeWS["Normalize whitespace"]
Restore --> ReturnCleaned
NormalizeWS --> ReturnCleaned
```

**Diagram sources**
- [build_index.py:16-55](file://build_index.py#L16-L55)

**Section sources**
- [build_index.py:16-55](file://build_index.py#L16-L55)

### Field Extraction: Nested llm_summary vs Direct Fields
The extraction logic prioritizes llm_summary fields and falls back to direct fields when llm_summary is absent or empty. This supports both LLM-generated summaries and direct-field uploads.

```mermaid
flowchart TD
Start(["extract_stock_fields(stock)"]) --> GetLLM["Get llm_summary dict"]
GetLLM --> HasLLM{"Is llm_summary non-empty?"}
HasLLM --> |Yes| UseLLM["Use llm_summary fields"]
HasLLM --> |No| UseDirect["Fallback to direct fields:<br/>core_business, insights, products,<br/>industry_position, chain, key_metrics,<br/>partners, accident"]
UseLLM --> ReturnFields["Return extracted fields"]
UseDirect --> ReturnFields
```

**Diagram sources**
- [build_index.py:57-75](file://build_index.py#L57-L75)

**Section sources**
- [build_index.py:57-75](file://build_index.py#L57-L75)

### Article Merging and Deduplication
Articles are merged from master and sentiment data:
- Master articles are normalized and cleaned
- Sentiment mentions are grouped by stock code and deduplicated by article_id
- Existing articles are preserved; new articles are appended only if not already present
- Mention counts are updated accordingly

```mermaid
sequenceDiagram
participant Master as "Master Articles"
participant Mentions as "Sentiment Mentions"
participant Merger as "Merge Engine"
participant Output as "Final Stocks Dict"
Master->>Merger : Normalize and clean articles
Mentions->>Merger : Group by code, clean, compute article_id
Merger->>Merger : Dedupe by article_id
Merger->>Output : Append new articles to existing ones
Output-->>Merger : Updated mention_count
```

**Diagram sources**
- [build_index.py:87-176](file://build_index.py#L87-L176)

**Section sources**
- [build_index.py:87-176](file://build_index.py#L87-L176)

### Concept Index Generation
A concept index maps each concept to the list of stock codes that include it. This enables fast filtering and concept-based navigation.

```mermaid
flowchart TD
Start(["Build Concepts"]) --> IterateStocks["Iterate stocks"]
IterateStocks --> ForEachConcept["For each concept in stock"]
ForEachConcept --> AddCode["Add code to concepts[concept]"]
AddCode --> Done{"More concepts?"}
Done --> |Yes| ForEachConcept
Done --> |No| ReturnConcepts["Return concepts dict"]
```

**Diagram sources**
- [build_index.py:178-185](file://build_index.py#L178-L185)

**Section sources**
- [build_index.py:178-185](file://build_index.py#L178-L185)

### Detail Text Generation for Front-End
Detail texts are constructed from available fields to optimize front-end display. The generator includes:
- Core business
- Industry position
- Chain
- Key metrics
- Accidents
- Insights
- Partners

These are assembled into a concise list for rendering.

```mermaid
flowchart TD
Start(["Generate detail_texts"]) --> Init["Initialize empty list"]
Init --> CheckCB{"Has core_business?"}
CheckCB --> |Yes| AddCB["Append 'Core business'"]
CheckCB --> |No| CheckIP{"Has industry_position?"}
AddCB --> CheckIP
CheckIP --> |Yes| AddIP["Append 'Industry position'"]
CheckIP --> |No| CheckChain{"Has chain?"}
AddIP --> CheckChain
CheckChain --> |Yes| AddChain["Append 'Chain'"]
CheckChain --> |No| CheckKM{"Has key_metrics?"}
AddChain --> CheckKM
CheckKM --> |Yes| AddKM["Append 'Key metrics'"]
CheckKM --> |No| CheckAcc{"Has accident?"}
AddKM --> CheckAcc
CheckAcc --> |Yes| AddAcc["Append 'Accident'"]
CheckAcc --> |No| CheckIns{"Has insights?"}
AddAcc --> CheckIns
CheckIns --> |Yes| AddIns["Append 'Insights'"]
CheckIns --> |No| CheckPart{"Has partners?"}
AddIns --> CheckPart
CheckPart --> |Yes| AddPart["Append 'Partners'"]
CheckPart --> |No| Done["Return detail_texts"]
AddPart --> Done
```

**Diagram sources**
- [build_index.py:187-219](file://build_index.py#L187-L219)

**Section sources**
- [build_index.py:187-219](file://build_index.py#L187-L219)

### Gzip Compression and JSON Serialization
The final index is serialized to a gzipped JSON file for compactness and fast transfer. The output includes:
- Version
- Update time
- Stocks dictionary
- Concepts mapping

Compression is handled via gzip with UTF-8 encoding.

**Section sources**
- [build_index.py:222-234](file://build_index.py#L222-L234)

### Automated Git Workflow and Deployment Trigger
After building the index, the pipeline commits and pushes changes to trigger Railway deployment:
- Configures Git user identity
- Checks for staged changes
- Adds all changes, commits with timestamped message, and pushes to origin/main
- A separate script can force redeploy by pushing an empty commit

```mermaid
sequenceDiagram
participant Builder as "Index Builder"
participant Git as "Git"
participant Remote as "Origin/Main"
participant Trigger as "trigger_deploy.sh"
participant Railway as "Railway"
Builder->>Git : git config, add -A, commit
Git->>Remote : push origin main
Remote-->>Railway : Webhook triggers deployment
Trigger->>Remote : Empty commit push (alternative)
Remote-->>Railway : Redeploy
```

**Diagram sources**
- [build_index.py:236-267](file://build_index.py#L236-L267)
- [trigger_deploy.sh:1-25](file://trigger_deploy.sh#L1-L25)

**Section sources**
- [build_index.py:236-267](file://build_index.py#L236-L267)
- [trigger_deploy.sh:1-25](file://trigger_deploy.sh#L1-L25)

## Dependency Analysis
External dependencies and runtime components:
- Flask app loads the gzipped index and serves endpoints
- Gunicorn runs the Flask app on Railway
- Railway configuration defines build and deploy behavior
- Requirements define Python packages

```mermaid
graph TB
App["main.py"]
GzipIdx["search_index_full.json.gz"]
Flask["Flask 3.0.0"]
Gunicorn["Gunicorn 21.2.0"]
Requests["requests 2.31.0"]
Akshare["akshare >= 1.18.40"]
App --> GzipIdx
App --> Flask
App --> Gunicorn
App --> Requests
App --> Akshare
```

**Diagram sources**
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [Procfile:1-2](file://Procfile#L1-L2)
- [main.py:6-18](file://main.py#L6-L18)

**Section sources**
- [requirements.txt:1-5](file://requirements.txt#L1-L5)
- [Procfile:1-2](file://Procfile#L1-L2)
- [main.py:6-18](file://main.py#L6-L18)

## Performance Considerations
- Memory optimization
  - Stream-like processing: load and process data incrementally; avoid loading entire datasets into memory at once
  - Deduplication uses sets for O(1) lookups
  - Iterative merging avoids deep copies where possible
- I/O efficiency
  - Use gzip for index serialization to reduce file size and network transfer
  - Prefer incremental writes and minimal intermediate structures
- CPU efficiency
  - Regex-based cleaning is straightforward; keep patterns minimal and reuse compiled patterns if reused frequently
  - Normalize whitespace after cleaning to reduce storage and improve downstream processing
- Search performance
  - Precompute concept index for O(1) concept-to-stocks lookup
  - Normalize text once during build; avoid repeated normalization at query time

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and remedies:
- Missing or invalid data files
  - Verify paths to master and sentiment files exist and are readable
  - Ensure the index builder can locate and parse both files
- Text cleaning anomalies
  - Confirm multi-source separators are preserved during cleaning
  - Validate that arrays are joined correctly and whitespace is normalized
- Field extraction failures
  - Ensure llm_summary fallback logic is triggered when nested fields are missing
  - Validate that direct fields are populated when llm_summary is empty
- Deduplication mismatches
  - Confirm article_id computation is consistent across master and mentions
  - Check that article_id uniqueness prevents duplicates
- Concept index errors
  - Validate concept names are non-empty and normalized
  - Ensure concept-to-code mapping is built after merging
- Detail text generation
  - Confirm optional fields are checked before inclusion
  - Validate that detail_texts remain concise and readable
- Serialization and deployment
  - Verify gzip and JSON serialization succeed
  - Check Git credentials and permissions for push operations
  - Confirm Railway configuration and Procfile are correct

**Section sources**
- [build_index.py:77-271](file://build_index.py#L77-L271)
- [main.py:94-105](file://main.py#L94-L105)

## Conclusion
The pipeline provides a robust, automated mechanism to transform raw sentiment data into a compressed, searchable index. It emphasizes correctness through deduplication and normalization, flexibility through dual field extraction modes, and performance via precomputed indices and compression. The Git-triggered deployment ensures timely updates to the Railway-hosted application.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Data Validation and Transformation Rules
- Input validation
  - Check for presence of required keys (e.g., code, name)
  - Validate types (strings, lists, dicts)
- Transformation rules
  - Normalize text using the cleaning function
  - Convert arrays to comma-separated strings when needed
  - Preserve multi-source separators during cleaning
  - Compute article_id consistently across sources
- Quality assurance
  - Compare mention counts before and after deduplication
  - Verify concept index completeness
  - Confirm detail_texts readability and relevance

**Section sources**
- [build_index.py:16-55](file://build_index.py#L16-L55)
- [build_index.py:87-176](file://build_index.py#L87-L176)
- [build_index.py:178-219](file://build_index.py#L178-L219)

### Related Scripts and Utilities
- Email data merger: [merge_email_data.py](file://merge_email_data.py) merges external email attachments into master stock data
- README deployment guide: [README.md](file://README.md) documents Railway deployment steps and configuration

**Section sources**
- [merge_email_data.py:1-88](file://merge_email_data.py#L1-L88)
- [README.md:1-126](file://README.md#L1-L126)