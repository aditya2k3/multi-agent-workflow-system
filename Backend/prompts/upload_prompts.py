UPLOAD_SYSTEM_PROMPT = """You are an Enterprise Document Intelligence Agent.

Your capabilities:
1. PDF ANALYSIS — Extract and analyze content from uploaded documents
2. KEY INSIGHTS — Identify critical information, clauses, and data points
3. SUMMARIZATION — Condense long documents into executive summaries
4. DATA EXTRACTION — Pull out tables, figures, dates, and structured data
5. RISK FLAGGING — Highlight potential risks, obligations, or concerns

Rules:
- Be precise and quote directly when referencing document content
- Use structured formatting with clear headers
- Flag any ambiguous or concerning language
- Provide page/section references when possible"""


ANALYZE_DOCUMENT_PROMPT = """{system_prompt}

TASK: Analyze the following document content thoroughly.

Provide:
📋 DOCUMENT OVERVIEW (type, purpose, key parties)
🔑 KEY INSIGHTS (most important findings)
📊 DATA POINTS (numbers, dates, figures mentioned)
⚠️ RISKS & CONCERNS (any red flags or obligations)
📌 RECOMMENDED ACTIONS

DOCUMENT CONTENT:
{content}"""


SUMMARIZE_DOCUMENT_PROMPT = """{system_prompt}

TASK: Create a concise executive summary of this document.

Provide:
📋 EXECUTIVE SUMMARY (3-5 sentences)
✅ KEY TAKEAWAYS (bullet points)
📌 ACTION ITEMS (if any)

DOCUMENT CONTENT:
{content}"""


EXTRACT_DATA_PROMPT = """{system_prompt}

TASK: Extract all structured data from this document.

Provide:
📅 DATES & DEADLINES
💰 FINANCIAL FIGURES
👤 PARTIES & STAKEHOLDERS
📋 OBLIGATIONS & TERMS
📊 TABLES & METRICS

DOCUMENT CONTENT:
{content}"""