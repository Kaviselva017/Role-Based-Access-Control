"""
Re-index all existing documents in the database to the new doc_chunks collection.
Run this script once after migrating to the FastEmbed architecture.
"""
import os
import sys
from bson import ObjectId

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from models import documents_collection, doc_chunks_collection, Document
from rag_system import process_document_for_rag

def reindex_all():
    print("Starting full re-indexing of all documents...")
    
    # 1. Clear existing chunks
    count = doc_chunks_collection.count_documents({})
    print(f"Clearing {count} existing chunks from 'doc_chunks'...")
    doc_chunks_collection.delete_many({})
    
    # 2. Get all documents
    docs = list(documents_collection.find({}))
    print(f"Found {len(docs)} documents to re-index.")
    
    success_count = 0
    for doc in docs:
        doc_id = str(doc['_id'])
        content = doc.get('content', '')
        filename = doc.get('filename', 'unknown.txt')
        department = doc.get('department', '')
        
        print(f"Processing '{filename}' (ID: {doc_id})...")
        
        if not content:
            print(f"  ! Skipping: Document has no content.")
            continue
            
        success = process_document_for_rag(doc_id, content, filename, department)
        if success:
            success_count += 1
            print(f"  ✓ Success: Created chunks for '{filename}'")
        else:
            print(f"  ✗ Failed: Error processing '{filename}'")
            
    print("-" * 30)
    print(f"Re-indexing complete!")
    print(f"Successfully processed {success_count}/{len(docs)} documents.")
    print(f"Total chunks in 'doc_chunks': {doc_chunks_collection.count_documents({})}")

if __name__ == "__main__":
    reindex_all()
