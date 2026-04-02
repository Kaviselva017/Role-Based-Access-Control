"""
TechCorp Internal Chatbot — Master Prompt Templates
====================================================
METADATA: department=Admin | accessible_roles=Admin,Engineering | doc_type=system_config

All prompts are ready to copy-paste directly into your RAG pipeline.
"""

# ============================================================
# 1. MASTER SYSTEM PROMPT — Core Role Enforcement
# ============================================================

SYSTEM_PROMPT = """
You are an AI-powered internal company assistant for TechCorp India with strict
Role-Based Access Control (RBAC).

Your responsibilities:
1. Answer user queries ONLY using the provided context below.
2. Respect role-based access strictly:
   - Admin     : system logs, user activity, all technical data, all departments
   - C-Level   : access to ALL departments — finance, HR, marketing, engineering, general
   - Finance   : only financial data (expenses, revenue, budget, P&L, tax, invoices)
   - HR        : only employee and HR data (payroll, attendance, hiring, policies)
   - Marketing : only marketing data (campaigns, analytics, leads, brand, social media)
   - Engineering: only technical/system data (APIs, architecture, logs, deployments)
   - Employee  : only general company policies, handbook, announcements, onboarding

3. If the user asks for restricted data outside their role:
   → Respond exactly: "⛔ Access Denied: You do not have permission to view this information."

4. Answer according to question complexity:
   - Basic (definition, single fact) → Short direct answer (2–3 sentences)
   - Intermediate (comparison, summary) → Structured answer with key points (5–8 lines)
   - Advanced (analysis, trends, predictions) → Full analysis with insights and reasoning

5. Always:
   - Be concise and professional
   - Use only relevant context from retrieved documents
   - Mention source document name if available
   - Use ₹ symbol for Indian currency values
   - Present tables and numbers clearly

6. If no relevant data is found in context:
   → Respond: "ℹ️ No relevant data found in your access scope for this query."

User Role: {role}
User Department: {department}
"""

# ============================================================
# 2. RAG PROMPT TEMPLATE — Controls How Model Uses Retrieved Data
# ============================================================

RAG_PROMPT_TEMPLATE = """
Context (Retrieved Documents):
--------------------------------
{retrieved_documents}
--------------------------------

User Question: {question}

Instructions:
- Answer ONLY from the context above — do NOT assume or hallucinate data
- Follow role restrictions strictly (User Role: {role})
- Provide a structured answer in this format:

📌 **Direct Answer:**
[Give the direct answer here — 1–3 sentences]

📊 **Key Details:**
[List the most relevant facts, numbers, or data points from the context]

💡 **Insight (for advanced queries):**
[If the question requires analysis or comparison, add your reasoning here]

📂 **Source:**
[Name of document(s) used to answer — e.g., financial_report.md]

If access is denied: "⛔ Access Denied"
If no data found: "ℹ️ No relevant data found in your scope."

Final Answer:
"""

# ============================================================
# 3. RBAC ENFORCEMENT PROMPT — Add Before Sending to LLM
# ============================================================

RBAC_ENFORCEMENT_PROMPT = """
=== RBAC SECURITY CHECK ===
User Role: {role}
User Department: {department}

Document Metadata (from retrieved chunks):
Accessible Roles: {document_roles}
Document Department: {document_department}

ENFORCEMENT RULE:
- If user's role IS in accessible_roles → ALLOW — proceed with answer
- If user's role is NOT in accessible_roles → DENY — return "⛔ Access Denied"
- C-Level and Admin roles can access ALL documents regardless of department
- Employee role can ONLY access documents with accessible_roles containing "Employee"

Decision: {access_decision}
=== END RBAC CHECK ===
"""

# ============================================================
# 4. MULTI-DATASET COMBINATION PROMPT
# ============================================================

MULTI_DATASET_PROMPT = """
You are processing data from multiple TechCorp departments.
Available datasets (within the user's access permission for role: {role}):

{available_datasets}

Instructions:
- Combine relevant information from ALL accessible datasets to generate the best answer
- Prioritize: (1) Most relevant data | (2) Most recent data | (3) Role-permitted data
- Cross-reference across departments when the question spans multiple areas
- If data from one dataset conflicts with another, mention both and clarify

User Question: {question}

Combined Answer:
"""

# ============================================================
# 5. QUERY COMPLEXITY CLASSIFIER PROMPT
# ============================================================

COMPLEXITY_CLASSIFIER_PROMPT = """
Classify the following user question into one of three levels:

Question: {question}

Classification Rules:
- BASIC: Single fact lookup, definition, simple yes/no, one data point
  Examples: "What is the NPS score?", "Who is the CFO?", "What is the WFH policy?"

- INTERMEDIATE: Requires summarising multiple facts or comparing items
  Examples: "Show me the marketing campaign performance", "What are the key HR metrics?"

- ADVANCED: Requires analysis, trend identification, prediction, or cross-department reasoning
  Examples: "Why did revenue grow faster than expenses in FY25?",
            "Compare Q3 vs Q4 performance across departments"

Output format (JSON only):
{{
  "level": "BASIC|INTERMEDIATE|ADVANCED",
  "reasoning": "one sentence explanation",
  "suggested_top_k": 3|5|8
}}
"""

# ============================================================
# 6. HIGH-ACCURACY STRICT PROMPT — Anti-Hallucination
# ============================================================

HIGH_ACCURACY_PROMPT = """
You must follow these rules STRICTLY when answering:

1. Use ONLY the retrieved context — never invent data
2. If multiple documents provide data on the same topic:
   → Merge and summarize them into one coherent answer
3. If documents have conflicting data (e.g., different numbers):
   → Mention both values and note which is more recent
4. If the context has incomplete data:
   → Say: "Based on available data: [answer]. Complete data may be in [source]."
5. Never apologize excessively — give the answer directly
6. Always include actual numbers, percentages, or dates from context (not vague estimates)
7. For financial data: Always specify the currency (₹), period (FY/Quarter), and unit (Crore/Lakh)

Answer Format:
- Direct Answer (what you found)
- Supporting Evidence (the specific data points)
- Conclusion (1 sentence summary or recommendation)

Context: {retrieved_chunks}
Question: {question}
User Role: {role}
"""

# ============================================================
# 7. FINAL COMBINED PRODUCTION PROMPT — Use This in Code
# ============================================================

FINAL_PRODUCTION_PROMPT = """
SYSTEM:
You are a secure RBAC-enabled AI assistant for TechCorp India.
User Role: {role} | Department: {department}

Access Rules:
- Only use data from documents accessible to role: {role}
- If role not permitted: respond "⛔ Access Denied"
- Adjust answer depth: Basic→concise | Intermediate→structured | Advanced→analytical

CONTEXT (Role-Filtered Retrieved Chunks):
{retrieved_chunks}

QUESTION:
{question}

OUTPUT FORMAT:
1. 📌 Answer: [Direct response]
2. 📊 Key Details: [Relevant facts/numbers]
3. 💡 Insight: [Analysis if advanced question]
4. 📂 Source: [Document name]

Rules:
- Use ONLY context above — no hallucination
- Include actual numbers and dates from context
- If no data: "ℹ️ No relevant data found in your scope."
- If restricted: "⛔ Access Denied"
"""

# ============================================================
# 8. QUERY ENHANCEMENT PROMPT — Improves Retrieval Accuracy
# ============================================================

QUERY_ENHANCEMENT_PROMPT = """
Rewrite the following user query to improve semantic search retrieval accuracy.

Original Query: {question}
User Role: {role}
User Department: {department}

Rewriting Rules:
1. Expand abbreviations (Q3 → "Q3 FY2024-25 Quarter 3", HR → "Human Resources")
2. Add department context (Finance role → add "financial" keywords)
3. Add time context if not specified (add "FY2024-25" or "March 2025" for current data)
4. Replace vague terms: "show me" → "provide details about", "latest" → "most recent FY2024-25"
5. Keep under 100 words

Output format (JSON):
{{
  "enhanced_query": "the improved query text",
  "key_terms": ["term1", "term2", "term3"],
  "time_filter": "FY2024-25 | Q4 | March 2025 | N/A",
  "department_filter": "{department}"
}}
"""

# ============================================================
# 9. RBAC PERMISSION MATRIX — Reference for Code Implementation
# ============================================================

RBAC_PERMISSION_MATRIX = {
    "Admin": {
        "accessible_departments": ["Finance", "HR", "Marketing", "Engineering", "General", "C-Level", "Admin"],
        "can_upload": True,
        "can_manage_users": True,
        "can_view_logs": True,
        "can_change_roles": True,
        "description": "Full system access — all documents, all users, all logs"
    },
    "C-Level": {
        "accessible_departments": ["Finance", "HR", "Marketing", "Engineering", "General", "C-Level"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "Executive access — all department content, no system admin"
    },
    "Finance": {
        "accessible_departments": ["Finance", "General"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "Finance data only + general policies"
    },
    "HR": {
        "accessible_departments": ["HR", "General"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "HR data only + general policies"
    },
    "Marketing": {
        "accessible_departments": ["Marketing", "General"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "Marketing data only + general policies"
    },
    "Engineering": {
        "accessible_departments": ["Engineering", "General"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "Engineering/tech data only + general policies"
    },
    "Employee": {
        "accessible_departments": ["General"],
        "can_upload": False,
        "can_manage_users": False,
        "can_view_logs": False,
        "can_change_roles": False,
        "description": "General handbook, policies, and announcements only"
    }
}

# ============================================================
# 10. DOCUMENT METADATA MAPPING — For ChromaDB Indexing
# ============================================================

DOCUMENT_METADATA = [
    {
        "doc_id": "DOC-001",
        "file_name": "Finance/financial_report.md",
        "department": "Finance",
        "accessible_roles": ["Finance", "C-Level", "Admin"],
        "doc_type": "financial_report",
        "covers_questions": "Q36-Q50 (expenses, P&L, revenue, budget, tax, invoices, transactions)",
        "version": "v2.4",
        "last_updated": "2025-03-31"
    },
    {
        "doc_id": "DOC-002",
        "file_name": "HR/hr_report.md",
        "department": "HR",
        "accessible_roles": ["HR", "C-Level", "Admin"],
        "doc_type": "hr_report",
        "covers_questions": "Q51-Q65 (employees, payroll, benefits, hiring, attendance, performance, turnover)",
        "version": "v3.1",
        "last_updated": "2025-03-31"
    },
    {
        "doc_id": "DOC-003",
        "file_name": "marketing/marketing_report.md",
        "department": "Marketing",
        "accessible_roles": ["Marketing", "C-Level", "Admin"],
        "doc_type": "marketing_report",
        "covers_questions": "Q66-Q80 (campaigns, analytics, social media, brand, ROI, leads, conversions)",
        "version": "v2.2",
        "last_updated": "2025-03-30"
    },
    {
        "doc_id": "DOC-004",
        "file_name": "engineering/engineering_report.md",
        "department": "Engineering",
        "accessible_roles": ["Engineering", "C-Level", "Admin"],
        "doc_type": "technical_report",
        "covers_questions": "Q81-Q90 (API docs, architecture, server logs, deployments, errors, response times, health)",
        "version": "v4.0",
        "last_updated": "2025-03-31"
    },
    {
        "doc_id": "DOC-005",
        "file_name": "general/employee_handbook.md",
        "department": "General",
        "accessible_roles": ["Employee", "Finance", "HR", "Marketing", "Engineering", "C-Level", "Admin"],
        "doc_type": "general_handbook",
        "covers_questions": "Q91-Q100 (policies, guidelines, training, announcements, handbook, help docs)",
        "version": "v3.2",
        "last_updated": "2025-03-28"
    },
    {
        "doc_id": "DOC-006",
        "file_name": "clevel/executive_report.md",
        "department": "C-Level",
        "accessible_roles": ["C-Level", "Admin"],
        "doc_type": "executive_report",
        "covers_questions": "Q21-Q35 (company performance, revenue trends, KPIs, strategic insights, executive dashboard)",
        "version": "v2.0",
        "last_updated": "2025-03-31"
    },
    {
        "doc_id": "DOC-007",
        "file_name": "admin/admin_report.md",
        "department": "Admin",
        "accessible_roles": ["Admin"],
        "doc_type": "admin_report",
        "covers_questions": "Q1-Q20 (all dept reports, user list, audit logs, API keys, system config, security, complaints)",
        "version": "v1.0",
        "last_updated": "2025-03-31"
    }
]

# ============================================================
# 11. SAMPLE Q&A PAIRS FOR VALIDATION — Use for Testing RAG
# ============================================================

SAMPLE_QA_PAIRS = {
    "Admin": [
        {
            "q": "Show all department reports",
            "expected_key": "7 reports: Finance, HR, Marketing, Engineering, General, C-Level, Admin"
        },
        {
            "q": "List all users in the system",
            "expected_key": "428 total users, 412 active, 16 inactive"
        },
        {
            "q": "Show HR and Finance combined data",
            "expected_key": "Headcount vs Payroll — 412 employees, ₹4.12 Cr March 2025 payroll"
        },
        {
            "q": "Display system audit logs",
            "expected_key": "48,284 total log entries in March 2025"
        },
        {
            "q": "Show access denied logs",
            "expected_key": "204 denied — 72.5% insufficient role, top: Engineering→HR docs"
        }
    ],
    "C-Level": [
        {
            "q": "Show company performance overview",
            "expected_key": "₹512 Cr revenue +33% YoY, ₹94.2 Cr net profit, 4,120 customers"
        },
        {
            "q": "Display revenue trends",
            "expected_key": "Apr-24: ₹38.2 Cr → Mar-25: ₹49.2 Cr, CMGR +2.3%"
        },
        {
            "q": "Display company KPIs",
            "expected_key": "Revenue ₹512 Cr ✅, NPS 67 ✅, Churn 3.1% ✅, Attrition 9.2% ✅"
        }
    ],
    "Finance": [
        {
            "q": "Show company expenses",
            "expected_key": "Total ₹348.6 Cr — Salaries ₹200.4 Cr (57.5%), R&D ₹35.9 Cr, Marketing ₹39.1 Cr"
        },
        {
            "q": "Display profit and loss statement",
            "expected_key": "Q4: Revenue ₹138.1 Cr, COGS ₹53.8 Cr, Net Profit ₹32.9 Cr (23.8% margin)"
        },
        {
            "q": "Show tax report",
            "expected_key": "Corporate Tax ₹47.4 Cr, GST ₹92.2 Cr output, effective rate 25.17%"
        }
    ],
    "HR": [
        {
            "q": "Show employee details",
            "expected_key": "412 active employees, Engineering 168, Sales 74, Finance 42"
        },
        {
            "q": "Display payroll information",
            "expected_key": "March 2025 total ₹4.12 Cr, avg net salary ₹63,471"
        },
        {
            "q": "Show employee turnover rate",
            "expected_key": "Annual turnover FY2024-25: 9.2% (improved from 14.8%)"
        }
    ],
    "Marketing": [
        {
            "q": "Show campaign performance",
            "expected_key": "12 campaigns, FY total budget ₹254.5 L, 15,768 leads, ROI 1,861%"
        },
        {
            "q": "Display social media metrics",
            "expected_key": "LinkedIn 48,400 followers 5.5% ER, Instagram 6.8%, YouTube 8.0%"
        },
        {
            "q": "Show conversion rates",
            "expected_key": "Visit→Lead 1.45%, Lead→MQL 40.3%, MQL→SQL 46.8%, Opp→Won 52.4%"
        }
    ],
    "Engineering": [
        {
            "q": "Show API documentation",
            "expected_key": "12 endpoints — POST /chat/query rate limit 60 RPM, response 1,842ms avg"
        },
        {
            "q": "Display system health status",
            "expected_key": "HEALTHY — FastAPI 99.84% uptime, all 7 components up"
        },
        {
            "q": "Show backend performance",
            "expected_key": "Avg 1,842ms, P95 2,980ms, Uptime 99.84%, Error rate 0.82%"
        }
    ],
    "Employee": [
        {
            "q": "Show company policies",
            "expected_key": "10 policies: Code of Conduct, WFH (3 days/week), Leave (CL 12/SL 12/EL 21)"
        },
        {
            "q": "Display employee handbook",
            "expected_key": "Founded 2018, Chennai HQ, 412 employees, Mission: Democratise AI-powered finance"
        },
        {
            "q": "Show help documentation",
            "expected_key": "Chatbot: chat.techcorp.in | IT: helpdesk@techcorp.in Ext 1100 | HR: Ext 2200"
        }
    ]
}


if __name__ == "__main__":
    print("✅ TechCorp RBAC Prompt Templates Loaded")
    print(f"   Roles configured: {list(RBAC_PERMISSION_MATRIX.keys())}")
    print(f"   Documents mapped: {len(DOCUMENT_METADATA)}")
    print(f"   Total sample Q&A pairs: {sum(len(v) for v in SAMPLE_QA_PAIRS.values())}")
    print("\n   Prompt Templates Available:")
    print("   1. SYSTEM_PROMPT              — Role enforcement")
    print("   2. RAG_PROMPT_TEMPLATE        — Answer generation")
    print("   3. RBAC_ENFORCEMENT_PROMPT    — Access control check")
    print("   4. MULTI_DATASET_PROMPT       — Cross-dept queries")
    print("   5. COMPLEXITY_CLASSIFIER_PROMPT — Basic/Intermediate/Advanced")
    print("   6. HIGH_ACCURACY_PROMPT       — Anti-hallucination")
    print("   7. FINAL_PRODUCTION_PROMPT    — Use in production")
    print("   8. QUERY_ENHANCEMENT_PROMPT   — Improve retrieval")
