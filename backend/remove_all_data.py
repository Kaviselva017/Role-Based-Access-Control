import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Connection
MONGODB_URL = os.getenv('MONGO_URI') or os.getenv('MONGODB_URL') or 'mongodb://localhost:27017'
client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client.get_database('company_chatbot_rbac')

def clear_all_role_data():
    """
    Removes all documents, document chunks, chat history, and query metrics from the database.
    This effectively clears all data associated with roles in the RAG system.
    """
    print("--- RBAC System Data Purge ---")
    
    # Collections to clear
    collections = {
        'documents': 'Uploaded documents',
        'doc_chunks': 'Document embeddings/chunks',
        'chat_history': 'User chat conversations',
        'queries': 'Analytical query metrics'
    }
    
    for collection_name, description in collections.items():
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            if count > 0:
                result = collection.delete_many({})
                print(f"✅ Cleared {result.deleted_count} {description} from collection: {collection_name}")
            else:
                print(f"ℹ️ Collection {collection_name} ({description}) is already empty.")
        except Exception as e:
            print(f"❌ Error clearing collection {collection_name}: {e}")

    print("\n--- Purge Complete ---")
    print("All role-specific knowledge and interaction history has been removed.")
    print("Users, roles, and access keys remain intact.")

if __name__ == '__main__':
    # Non-interactive mode for direct execution
    clear_all_role_data()
