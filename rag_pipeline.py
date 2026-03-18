import re
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from vector_db.search_engine import secure_semantic_search

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = None
model = None


def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading LLM...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, torch_dtype=torch.float32, device_map="auto"
        )
        print("LLM loaded.")


def build_context(docs):
    return "\n\n".join(
        f"[Source: {d['metadata']['source']}]\n{d['document']}"
        for d in docs
    )


def clean_llm_output(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        if line.startswith("[Source:"):
            continue
        if line.strip().startswith("<|"):
            continue
        cleaned.append(line)
    text = " ".join(cleaned)
    text = re.sub(r"Answer:", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_response(query: str, user_role: str) -> dict:
    start_time = time.time()
    clean_query = query.lower().strip()

    def elapsed():
        return round((time.time() - start_time) * 1000, 2)

    def resp(answer, sources=None, confidence=1.0, docs=0):
        return {
            "answer": answer,
            "sources": sources or [],
            "confidence": confidence,
            "documents_used": docs,
            "response_time_ms": elapsed()
        }

    # 1. SMALL TALK
    small_talk = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hi there! Ask me about company reports or policies.",
        "hey": "Hello! Ask me about your company documents.",
        "who are you": "I am Dragon Intel, a secure RBAC assistant for internal company documents.",
        "what can you do": f"As a {user_role}, I can answer questions about your permitted company documents.",
        "help": "Try asking about revenue, HR policies, leave days, or your department reports.",
    }
    if clean_query in small_talk:
        return resp(small_talk[clean_query])

    # 2. ROLE IDENTITY
    role_triggers = ["my role", "what is my role", "say my role",
                     "who am i", "what role", "tell me my role"]
    if any(t in clean_query for t in role_triggers):
        return resp(f"Your current role is **{user_role}**.")

    # 3. OFF-TOPIC GUARD
    company_keywords = [
        "revenue", "profit", "cost", "expense", "loss", "budget", "forecast",
        "leave", "policy", "remote", "salary", "hire", "hiring", "headcount",
        "handbook", "attendance", "marketing", "engineering", "hr", "finance",
        "report", "quarter", "annual", "employee", "team", "project", "sprint",
        "campaign", "nps", "kpi", "metric", "insurance", "allowance", "bonus",
        "department", "company", "document", "data", "access", "role",
        "training", "onboard", "performance", "review", "holiday", "benefit",
    ]
    has_company_kw = any(kw in clean_query for kw in company_keywords)

    off_topic_patterns = [
        r"\bweather\b", r"\bjokes?\b", r"\bpoems?\b", r"\bsongs?\b",
        r"\blyrics?\b", r"\bstory\b", r"\bcook\b", r"\brecipes?\b",
        r"\bsports?\b", r"\bfootball\b", r"\bcricket\b", r"\bnews\b",
        r"\bpolitics\b", r"\bmovies?\b", r"\bgames?\b",
        r"\bwrite me a\b", r"\btell me a\b", r"\bgive me a\b",
        r"\bexplain quantum\b", r"\bmeaning of life\b",
        r"\bcapital of\b", r"\bwho invented\b",
    ]
    is_off_topic = any(re.search(p, clean_query) for p in off_topic_patterns)

    if is_off_topic and not has_company_kw:
        return resp(
            "I can only answer questions related to company documents, policies, and reports. "
            "Please ask something relevant to your role."
        )

    # 4. VAGUE QUERY GUARD
    vague_exact = [
        "do you know", "can you", "are you", "do you", "tell me", "what do you",
        "okay", "ok", "yes", "no", "maybe", "sure", "please", "thanks",
        "thank you", "cool", "nice", "great", "good", "bad", "test",
    ]
    if clean_query in vague_exact or (len(clean_query.split()) <= 2 and not has_company_kw):
        return resp(
            "Please ask a specific question — for example: "
            "'What is the Q2 revenue?' or 'What is the HR leave policy?'"
        )

    # 5. RBAC SEARCH
    docs = secure_semantic_search(query=query, user_role=user_role, top_k=3)
    doc_count = len(docs)
    confidence = round(
        sum(d["similarity_score"] or 0 for d in docs) / doc_count, 3
    ) if doc_count > 0 else 0.0
    sources = [d["metadata"]["source"] for d in docs]

    if doc_count == 0:
        return resp(
            f"As a {user_role} user, you do not have access to this information.",
            confidence=0.0
        )

    context = build_context(docs)

    # 6. DIRECT EXTRACTION
    if "revenue" in clean_query:
        m = re.search(r"[₹\$][\d,]+", context)
        if m:
            return resp(f"The reported revenue is {m.group()}.", sources, confidence, doc_count)

    if "profit" in clean_query:
        m = re.search(r"\d+(\.\d+)?%", context)
        if m:
            return resp(f"The reported profit margin is {m.group()}.", sources, confidence, doc_count)

    if "expense" in clean_query or "cost" in clean_query:
        m = re.search(r"[₹\$][\d,]+", context)
        if m:
            return resp(f"The reported operational expense is {m.group()}.", sources, confidence, doc_count)

    if "leave" in clean_query:
        m = re.search(r"\d+\s*(casual|paid|sick|annual)?\s*leave", context, re.IGNORECASE)
        if m:
            return resp(f"Leave policy: {m.group().capitalize()}.", sources, confidence, doc_count)

    if "remote" in clean_query or "work from home" in clean_query:
        return resp("Employees may work remotely up to 2 days per week as per company policy.", sources, confidence, doc_count)

    # 7. LLM FALLBACK
    load_model()

    messages = [
        {"role": "system", "content": (
            "You are a secure enterprise assistant. "
            "Answer ONLY using the context provided. "
            "Be concise. Answer in 1-3 sentences only. "
            "Do NOT repeat the context or source tags. "
            "If the question is off-topic reply: I can only answer company-related questions."
        )},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"}
    ]

    enc = tokenizer.apply_chat_template(messages, return_tensors="pt")
    enc = {k: v.to(model.device) for k, v in enc.items()}
    input_len = enc["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **enc,
            max_new_tokens=200,
            do_sample=False,
            repetition_penalty=1.15,
            eos_token_id=tokenizer.eos_token_id
        )

    new_tokens = outputs[0][input_len:]
    answer = clean_llm_output(tokenizer.decode(new_tokens, skip_special_tokens=True))

    if not answer or len(answer) < 10:
        answer = "I found relevant documents but could not generate a clear answer. Please rephrase your question."

    return resp(answer, sources, confidence, doc_count)
