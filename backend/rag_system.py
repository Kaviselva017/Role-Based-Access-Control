"""
RAG (Retrieval-Augmented Generation) System for document-based answers
Uses embeddings to find relevant documents and generate context-aware responses
"""

import os
from fastembed import TextEmbedding
import numpy as np
from models import Document, ChatHistory
import re
import functools

def cosine_similarity_np(a, b):
    """Pure numpy implementation of cosine similarity to avoid importing heavy sklearn/scipy"""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

# Load embedding model (FastEmbed uses ONNX for low memory/CPU-only performance)
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

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

def chunk_text(text, chunk_size=200, overlap=20):
    """Split text into precise, smaller chunks (1-2 sentences) for more exact, laser-focused answers."""
    # Aggressive pre-cleaning to remove messy markdown lines like ---------------
    text = re.sub(r'[-=]{3,}', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    chunks = []
    # Split by common sentence terminators but keep reasonable formatting
    raw_sentences = re.split(r'(?<=[.!?]) +|\n', text)
    
    current_chunk = []
    current_size = 0
    
    for sentence in raw_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        current_chunk.append(sentence)
        current_size += len(sentence)
        
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk).strip())
            # Keep only the last sentence for context overlap to stay precise
            current_chunk = current_chunk[-1:]
            current_size = sum(len(s) for s in current_chunk)
    
    # Add remaining text
    if current_chunk:
        chunks.append(' '.join(current_chunk).strip())
    
    return [c for c in chunks if len(c) > 20]

def get_document_embeddings(text):
    """Generate embeddings for document text"""
    try:
        # TextEmbedding.embed returns a generator, so we take the first item
        embedding_gen = embedding_model.embed([text])
        return next(embedding_gen).tolist()
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

@functools.lru_cache(maxsize=1000)
def get_cached_doc_embedding(text_content):
    """Cached version of document embeddings using FastEmbed"""
    # TextEmbedding.embed returns a generator, so we take the first item
    return next(embedding_model.embed([text_content]))

from models import doc_chunks_collection
from bson import ObjectId

def search_relevant_documents(query, department=None, limit=3):
    """Find relevant documents using pre-calculated embeddings in MongoDB"""
    try:
        # Get query embedding
        query_vec = next(embedding_model.embed([query]))
        
        # Build query filter
        filter_q = {}
        if department:
            # Match role or 'General'
            filter_q['$or'] = [
                {'department': department.lower()},
                {'department': 'general'},
                {'department': ''}
            ]
        
        # Get all chunks matching department
        all_chunks = list(doc_chunks_collection.find(filter_q))
        
        if not all_chunks:
            return []
            
        results = []
        for chunk in all_chunks:
            chunk_vec = np.array(chunk['embedding'])
            similarity = cosine_similarity_np(query_vec, chunk_vec)
            
            if similarity > 0.1: # Minimum relevance threshold
                results.append({
                    'id': str(chunk['doc_id']),
                    'filename': chunk['filename'],
                    'content': chunk['content'],
                    'department': chunk['department'],
                    'similarity': float(similarity)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Deduplicate results by content to avoid returning exact same chunk
        seen_content = set()
        unique_results = []
        for r in results:
            if r['content'] not in seen_content:
                unique_results.append(r)
                seen_content.add(r['content'])
            if len(unique_results) >= limit:
                break
                
        return unique_results
    
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
    
    # Further aggressive cleaning of any remaining dashed lines or formatting artifacts
    clean_chunk = re.sub(r'[-=]{2,}', ' ', clean_chunk)
    clean_chunk = re.sub(r'\*+', '', clean_chunk)
    clean_chunk = re.sub(r'\s+', ' ', clean_chunk).strip()
    
    # Follow exact output format requested, but clean
    response = f"- Answer: {clean_chunk}\n\n"
    response += f"- Source: {best_doc['filename']}"

    return {
        'response': response,
        'source': best_doc['filename'],
        'confidence': float(best_doc['similarity']),
        'referenced_docs': [best_doc['filename']]
    }

def process_document_for_rag(doc_id, content, filename, department=''):
    """Process and store document embeddings for RAG by creating pre-computed chunks"""
    try:
        # Extract and chunk text
        text = extract_text_from_document(content, filename.split('.')[-1])
        chunks = chunk_text(text, chunk_size=250, overlap=30)
        
        if not chunks:
            return False
            
        # Clean department
        dept = department.lower() if department else ''
        
        # Clear existing chunks for this document if any
        doc_chunks_collection.delete_many({'doc_id': ObjectId(doc_id)})
        
        # Store embeddings for each chunk
        chunk_docs = []
        # Embed all chunks in a batch for speed!
        embeddings = list(embedding_model.embed(chunks))
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_docs.append({
                'doc_id': ObjectId(doc_id),
                'filename': filename,
                'content': chunk,
                'embedding': embedding.tolist(),
                'department': dept,
                'chunk_index': i
            })
            
        if chunk_docs:
            doc_chunks_collection.insert_many(chunk_docs)
            
        # Mark document as indexed
        Document.mark_indexed(doc_id, True)
        
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
