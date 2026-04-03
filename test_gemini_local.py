import os
import sys
from dotenv import load_dotenv

os.chdir('d:/python/company-chatbot-rbac/backend')
load_dotenv('../frontend/.env')
sys.path.append('.')

from rag_system import generate_rag_response
import traceback

dummy_docs = [
    {
        "content": "The company's new remote work policy states that employees can work from home 3 days a week.",
        "filename": "remote_policy.pdf",
        "department": "hr",
        "similarity": 0.8
    }
]

with open('output_gemini.txt', 'w', encoding='utf-8') as f:
    f.write("Starting Local RAG Test...\n")
    try:
        res = generate_rag_response("What is the remote work policy?", "Admin", "General", dummy_docs)
        f.write("RESPONSE:\n")
        f.write(res["response"])
    except Exception as e:
        f.write("CRASH TRACEBACK:\n")
        f.write(traceback.format_exc())

