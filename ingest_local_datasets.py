
import os
import sys
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from models import documents_collection, doc_chunks_collection
    from rag_system import process_document_for_rag
    print("Successfully imported backend models.")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

NEW_DATASETS = [
    ("datasets/general/employees.md", "General"),
    ("datasets/finance/finance.md", "Finance"),
    ("datasets/hr/hr.md", "HR"),
    ("datasets/marketing/marketing.md", "Marketing"),
    ("datasets/engineering/engineering.md", "Engineering"),
]

def ingest_locally():
    print("Starting local ingestion of new fintech documents...")
    
    # Optional: Clear existing to prevent duplicates if this is a fresh update
    # documents_collection.delete_many({"filename": {"$in": [os.path.basename(f) for f, d in NEW_DATASETS]}})
    
    success_count = 0
    for filepath, department in NEW_DATASETS:
        if not os.path.exists(filepath):
            print(f"  [Skip] {filepath} not found.")
            continue
            
        filename = os.path.basename(filepath)
        print(f"  Ingesting '{filename}' into {department} department...", end=" ", flush=True)
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        if not content:
            print("❌ Empty file")
            continue
            
        # 1. Create document entry
        doc_entry = {
            "filename": filename,
            "content": content,
            "file_type": "md",
            "department": department,
            "uploaded_at": datetime.utcnow(),
            "is_indexed": False
        }
        
        # Check if exists to update or insert
        existing = documents_collection.find_one({"filename": filename})
        if existing:
            doc_id = str(existing['_id'])
            documents_collection.update_one({"_id": existing['_id']}, {"$set": doc_entry})
            # Clear old chunks for this doc
            doc_chunks_collection.delete_many({"doc_id": doc_id})
        else:
            result = documents_collection.insert_one(doc_entry)
            doc_id = str(result.inserted_id)
            
        # 2. Process for RAG
        try:
            success = process_document_for_rag(doc_id, content, filename, department)
            if success:
                print("✅ Done")
                success_count += 1
            else:
                print("⚠️ Ingested but indexing failed")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("-" * 30)
    print(f"Ingestion complete! {success_count}/{len(NEW_DATASETS)} datasets added to local AI knowledge.")

if __name__ == "__main__":
    ingest_locally()
