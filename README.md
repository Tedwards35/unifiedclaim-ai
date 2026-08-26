\# UnifiedClaim AI



A local-first RAG system that helps behavioral health providers audit clinical documentation and billing codes against regulatory policy — without sending patient data to a third-party API.



\## The problem



Behavioral health providers (e.g., DBHDD-licensed facilities) must document discharge/transition planning, progress notes, and billing codes in ways that satisfy multiple overlapping policy sources (state agency rules, CDC infection control guidance, CMS/ICD-10 coding standards). Manually cross-referencing clinical notes against these policies is slow and error-prone — and the source documents themselves change over time.



\## What it does



\- \*\*Policy-grounded Q\&A\*\* — ask natural-language questions about regulatory requirements and get answers retrieved from ingested policy documents (DBHDD, CDC, CMS/ICD-10), filterable by source and jurisdiction, with retrieval traced back to the originating document.

\- \*\*Billing code analysis\*\* — extracts ICD-10/CPT codes and modifiers from clinical text and flags common compliance issues (e.g., a procedure code with no supporting diagnosis, an E/M service missing modifier -25, anomalous code repetition).

\- \*\*Documentation audits\*\* — a pluggable audit framework (`AuditModule` base class + registry) that runs domain-specific checks. The included `DBHDDDischargeAudit` retrieves the relevant policy requirements, summarizes them in plain language, and diffs them against submitted clinical text to surface concrete documentation gaps (e.g., "discharge summary not explicitly documented").

\- \*\*Local-only inference\*\* — runs entirely on a local Ollama model (Llama 3 8B by default). Remote LLM providers are explicitly disabled in code, not just left unconfigured — a deliberate design choice for handling data with HIPAA-adjacent sensitivity.



\## Architecture



app/

├── api/ # FastAPI routes: /ask, /analyze, /upload, /reindex

├── audits/ # Pluggable audit modules (base class + registry pattern)

├── services/

│ ├── rag.py # LlamaIndex + Chroma ingestion \& retrieval, per-source metadata tagging

│ ├── llm.py # Local-only Ollama config, blocks remote LLM fallback

│ └── tools.py # Rule-based ICD-10/CPT extraction \& compliance heuristics

├── models/ # Pydantic request/response schemas

└── core/ # Settings/config





\*\*Stack:\*\* FastAPI · LlamaIndex · ChromaDB · Ollama (Llama 3 8B) · HuggingFace sentence-transformers (embeddings)



\## Design decisions worth noting



\- \*\*Metadata-driven retrieval\*\*: every ingested document is tagged with `source\_name`, `jurisdiction`, `policy\_domain`, and `effective\_date`, enabling filtered retrieval (e.g., "only DBHDD, behavioral health policy") rather than flat vector search over everything.

\- \*\*Extensible audits, not a single hardcoded check\*\*: adding a new compliance audit means implementing `AuditModule.run()` and registering it — the API and retrieval logic don't change.

\- \*\*Admin-gated write operations\*\*: `/upload` and `/reindex` require an API key in production mode.



\## Status / Roadmap



\- \[x] RAG ingestion with source-level metadata (DBHDD, CDC, CMS/ICD-10)

\- \[x] Policy-filtered Q\&A endpoint

\- \[x] Rule-based billing code compliance checks

\- \[x] Pluggable audit framework with first working audit (DBHDD discharge documentation)

\- \[ ] Additional audit modules (e.g., progress note completeness, CDC infection control)

\- \[ ] Frontend for uploading clinical text and viewing audit results

\- \[ ] Evaluation harness for retrieval quality / answer accuracy



\## Running locally



```bash

python -m venv venv \&\& source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env   # set LLM\_MODEL, DATA\_DIR, etc.

ollama pull llama3:8b

uvicorn app.main:app --reload

```



Ingest documents, then query:

```bash

python scripts/ingest.py

curl -X POST localhost:8000/ask -H "Content-Type: application/json" \\

&#x20; -d '{"question": "What must a discharge summary include?", "policy\_only": true}'

```



\## Disclaimer



This is a portfolio/research project, not a certified compliance tool. It is not a substitute for legal or regulatory review.

