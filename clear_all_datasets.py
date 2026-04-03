import os
from pymongo import MongoClient

# Use the MONGO_URI from the environment variables, or fallback to localhost
MONGODB_URL = os.getenv('MONGO_URI') or os.getenv('MONGODB_URL') or 'mongodb://localhost:27017'

print(f"Connecting to MongoDB at: {MONGODB_URL}")
client = MongoClient(MONGODB_URL)
db = client['company_chatbot_rbac']

documents_collection = db['documents']
doc_chunks_collection = db['doc_chunks']

def clear_datasets():
    # Count before deletion
    doc_count = documents_collection.count_documents({})
    chunk_count = doc_chunks_collection.count_documents({})
    
    print(f"Found {doc_count} documents and {chunk_count} chunks.")
    
    confirm = input("Are you sure you want to delete ALL uploaded datasets? (yes/no): ")
    if confirm.lower() == 'yes':
        # Delete all documents
        documents_collection.delete_many({})
        doc_chunks_collection.delete_many({})
        print("✅ All uploaded datasets have been completely removed from the database.")
    else:
        print("Deletion canceled.")

if __name__ == "__main__":
    clear_datasets()
