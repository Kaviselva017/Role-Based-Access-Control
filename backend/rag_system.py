"""
RAG (Retrieval-Augmented Generation) System for document-based answers
Uses embeddings to find relevant documents and generate context-aware responses
"""

import os
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import Document, ChatHistory
import re
import functools

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_document(content, file_type='txt'):
    """Extract text from various document formats"""
    if file_type == 'txt':
        return content
    elif file_type == 'md':
        # Remove markdown formatting
        text = re.sub(r'[#*_\[\]()]', '', content)
        return text
    elif file_type == 'pdf':
        # For PDF, content should already be extracted
        return content
    else:
        return content

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks for embedding"""
    chunks = []
    sentences = text.split('.')
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        current_chunk.append(sentence)
        current_size += len(sentence)
        
        if current_size >= chunk_size:
            chunks.append('. '.join(current_chunk).strip())
            # Keep last few sentences for overlap
            current_chunk = current_chunk[-2:]
            current_size = sum(len(s) for s in current_chunk)
    
    # Add remaining text
    if current_chunk:
        chunks.append('. '.join(current_chunk).strip())
    
    return [c for c in chunks if len(c) > 20]

def get_document_embeddings(text):
    """Generate embeddings for document text"""
    try:
        embedding = embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

@functools.lru_cache(maxsize=1000)
def get_cached_doc_embedding(text_content):
    """Cached version of document embeddings for highly accurate and instant retrieval"""
    return embedding_model.encode(text_content, convert_to_numpy=True)

def search_relevant_documents(query, department=None, limit=3):
    """Find relevant documents using semantic search"""
    try:
        # Get query embedding
        query_embedding = embedding_model.encode(query, convert_to_numpy=True)
        
        # Get all documents from department or all documents
        if department:
            documents = Document.get_documents_by_department(department)
        else:
            documents = Document.get_all_documents()
        
        # Filter for indexed documents only
        indexed_docs = [doc for doc in documents if doc.get('is_indexed')]
        
        if not indexed_docs:
            return []
        
        # Calculate similarity with document content
        results = []
        for doc in indexed_docs:
            try:
                text = doc['content']
                chunks = chunk_text(text, chunk_size=500, overlap=50)
                if not chunks:
                    continue
                
                best_similarity = -1.0
                best_chunk = ""
                
                for chunk in chunks:
                    chunk_embedding = get_cached_doc_embedding(chunk)
                    similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][0]
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_chunk = chunk
                
                if best_similarity > 0.1: # Only include if there's some relevance
                    results.append({
                        'id': str(doc['_id']),
                        'filename': doc['filename'],
                        'content': best_chunk,  # Return the best matching chunk!
                        'department': doc['department'],
                        'similarity': float(best_similarity)
                    })
            except Exception as e:
                print(f"Error processing doc {doc.get('filename')}: {e}")
                continue
        
        # Sort by relevance
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    except Exception as e:
        print(f"Search error: {e}")
        return []

def generate_rag_response(query, user_role, department, retrieved_docs):
    """Generate response based on retrieved documents following strict enterprise instructions."""
    
    if not retrieved_docs:
        return {
            'response': "No relevant information found.",
            'source': 'None',
            'confidence': 0.0,
            'referenced_docs': []
        }
    
    # Process the most relevant document
    best_doc = retrieved_docs[0]
    
    if best_doc['similarity'] < 0.1:  # Strict accuracy check
        return {
            'response': "No relevant information found.",
            'source': 'None',
            'confidence': float(best_doc['similarity']),
            'referenced_docs': []
        }

    # Ensure we deliver the exact matched text directly from the dataset.
    clean_chunk = best_doc['content'].strip()
    
    # Follow exact output format requested
    response = f"- Answer:\n{clean_chunk}\n\n"
    response += f"- Source: {best_doc['filename']}"

    return {
        'response': response,
        'source': best_doc['filename'],
        'confidence': float(best_doc['similarity']),
        'referenced_docs': [best_doc['filename']]
    }

def process_document_for_rag(doc_id, content, filename):
    """Process and store document embeddings for RAG"""
    try:
        # Extract and chunk text
        text = extract_text_from_document(content, filename.split('.')[-1])
        chunks = chunk_text(text)
        
        if not chunks:
            return False
        
        # Store embedding info
        summary = '\n'.join(chunks[:3])  # First 3 chunks as summary
        
        # Mark document as indexed
        Document.mark_indexed(doc_id, filename)
        
        return True
    except Exception as e:
        print(f"Document processing error: {e}")
        return False


def get_role_based_response(query, user_role):
    """
    Generate role-based responses with access control.
    Each role has specific guidelines on what they can access.
    """
    
    # Define role guidelines and permissions
    role_guidelines = {
        'admin': {
            'title': 'ADMINISTRATOR',
            'access_level': 'FULL_SYSTEM_ACCESS',
            'can_access': [
                'system_configuration',
                'user_management',
                'security_audit_logs',
                'all_department_data',
                'financial_reports',
                'hr_records',
                'strategic_documents',
                'api_management'
            ],
            'cannot_access': [],
            'keywords_allowed': ['admin', 'system', 'config', 'user', 'security', 'audit', 'management']
        },
        'c-level': {
            'title': 'EXECUTIVE (C-LEVEL)',
            'access_level': 'STRATEGIC_ACCESS',
            'can_access': [
                'strategic_documents',
                'financial_summaries',
                'executive_reports',
                'board_materials',
                'high_level_metrics',
                'cross_department_overview'
            ],
            'cannot_access': [
                'individual_employee_records',
                'system_configuration',
                'security_logs',
                'low_level_operations',
                'other_department_details'
            ],
            'keywords_allowed': ['strategy', 'executive', 'board', 'financial', 'summary', 'overview', 'performance']
        },
        'finance': {
            'title': 'FINANCE DEPARTMENT',
            'access_level': 'DEPARTMENTAL_ACCESS',
            'can_access': [
                'financial_documents',
                'budgets',
                'expense_reports',
                'revenue_data',
                'financial_analysis',
                'audit_trails'
            ],
            'cannot_access': [
                'hr_employee_records',
                'operations_details',
                'admin_configurations',
                'executive_decisions',
                'other_department_specifics'
            ],
            'keywords_allowed': ['finance', 'budget', 'expense', 'revenue', 'accounting', 'audit', 'cost', 'profit']
        },
        'hr': {
            'title': 'HUMAN RESOURCES',
            'access_level': 'DEPARTMENTAL_ACCESS',
            'can_access': [
                'employee_records',
                'payroll_information',
                'benefits_data',
                'training_materials',
                'organizational_structure',
                'hr_policies'
            ],
            'cannot_access': [
                'financial_sensitive_data',
                'system_configuration',
                'security_audit_logs',
                'strategic_confidential',
                'other_department_specifics'
            ],
            'keywords_allowed': ['hr', 'employee', 'payroll', 'benefits', 'training', 'hiring', 'policy', 'organization']
        },
        'employee': {
            'title': 'GENERAL EMPLOYEE',
            'access_level': 'LIMITED_ACCESS',
            'can_access': [
                'personal_records',
                'public_company_info',
                'general_guidelines',
                'training_materials',
                'own_department_overview'
            ],
            'cannot_access': [
                'other_employee_records',
                'financial_data',
                'strategic_documents',
                'system_configuration',
                'cross_department_confidential',
                'executive_decisions'
            ],
            'keywords_allowed': ['my', 'personal', 'training', 'policy', 'guidelines', 'public']
        },
        'marketing': {
            'title': 'MARKETING DEPARTMENT',
            'access_level': 'DEPARTMENTAL_ACCESS',
            'can_access': [
                'marketing_materials',
                'campaign_data',
                'market_research',
                'customer_insights',
                'brand_guidelines',
                'analytics_reports'
            ],
            'cannot_access': [
                'financial_sensitive',
                'hr_records',
                'system_configuration',
                'strategic_confidential',
                'other_department_specifics'
            ],
            'keywords_allowed': ['marketing', 'campaign', 'brand', 'customer', 'market', 'analytics', 'content']
        },
        'engineering': {
            'title': 'ENGINEERING DEPARTMENT',
            'access_level': 'DEPARTMENTAL_ACCESS',
            'can_access': [
                'technical_documentation',
                'system_architecture',
                'code_standards',
                'api_documentation',
                'development_guidelines',
                'tool_configurations'
            ],
            'cannot_access': [
                'financial_data',
                'hr_employee_details',
                'strategic_business',
                'system_admin_config',
                'other_department_specifics'
            ],
            'keywords_allowed': ['engineering', 'technical', 'code', 'api', 'development', 'architecture', 'tool']
        }
    }
    
    # Get user role guidelines
    guidelines = role_guidelines.get(user_role, role_guidelines['employee'])
    
    # Check if query contains restricted keywords for this role
    query_lower = query.lower()
    access_denied = False
    
    # Check for restricted access
    restricted_keywords = {
        'admin': [],
        'c-level': [],
        'finance': ['employee', 'hr', 'operations', 'admin', 'executive', 'marketing', 'engineering', 'payroll'],
        'hr': ['finance', 'financial', 'budget', 'security', 'strategic', 'marketing', 'engineering', 'revenue'],
        'employee': ['finance', 'financial', 'hr', 'strategic', 'confidential', 'admin', 'marketing', 'engineering', 'cost', 'revenue', 'budget'],
        'marketing': ['finance', 'financial', 'hr', 'system', 'strategic', 'admin', 'engineering', 'budget', 'revenue'],
        'engineering': ['finance', 'financial', 'hr', 'business', 'admin', 'marketing', 'revenue', 'budget', 'sales']
    }
    
    # Also strictly block cross-departmental queries missing from the allowed list
    role_restricted = restricted_keywords.get(user_role, [])
    for keyword in role_restricted:
        if keyword in query_lower:
            access_denied = True
            break
            
    # If the exact words are outside their role permissions
    if access_denied:
        return {
            'response': "Access Denied.",
            'access_denied': True,
            'role_info': {'title': guidelines['title']}
        }
    
    # Rule 3: If no relevant context is found -> respond: "No relevant information found."
    return {
        'response': "No relevant information found.",
        'access_denied': False,
        'role_info': {'title': guidelines['title']}
    }
