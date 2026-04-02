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
from prompt_templates import FINAL_PRODUCTION_PROMPT, RBAC_PERMISSION_MATRIX

def cosine_similarity_np(a, b):
    """Pure numpy implementation of cosine similarity to avoid importing heavy sklearn/scipy"""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

# Load embedding model (FastEmbed uses ONNX for low memory/CPU-only performance)
# We set threads=1 to heavily reduce memory usage and prevent Render OOM crashes
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5", threads=1)

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
    """Generate response based on retrieved documents using the FINAL_PRODUCTION_PROMPT template.
    Uses ALL retrieved chunks for richer, more comprehensive answers."""
    
    if not retrieved_docs:
        return {
            'response': "ℹ️ No relevant data found in your access scope for this query.",
            'source': 'None',
            'confidence': 0.0,
            'referenced_docs': []
        }
    
    # Filter out very low similarity results
    relevant_docs = [d for d in retrieved_docs if d['similarity'] > 0.1]
    
    if not relevant_docs:
        return {
            'response': "ℹ️ No relevant data found in your access scope for this query.",
            'source': 'None',
            'confidence': 0.0,
            'referenced_docs': []
        }

    # Build combined context from ALL relevant chunks (not just top-1)
    context_parts = []
    source_files = []
    for i, doc in enumerate(relevant_docs):
        clean_chunk = doc['content'].strip()
        clean_chunk = re.sub(r'[-=]{2,}', ' ', clean_chunk)
        clean_chunk = re.sub(r'\*+', '', clean_chunk)
        clean_chunk = re.sub(r'\s+', ' ', clean_chunk).strip()
        context_parts.append(f"[Chunk {i+1} | {doc['filename']} | Relevance: {doc['similarity']:.2f}]\n{clean_chunk}")
        if doc['filename'] not in source_files:
            source_files.append(doc['filename'])

    combined_context = "\n\n".join(context_parts)
    
    # Build response using the structured production prompt format
    response_lines = []
    
    # 📌 Answer: Direct combined content from all relevant chunks
    best_chunk = relevant_docs[0]['content'].strip()
    best_chunk = re.sub(r'[-=]{2,}', ' ', best_chunk)
    best_chunk = re.sub(r'\*+', '', best_chunk)
    best_chunk = re.sub(r'\s+', ' ', best_chunk).strip()
    response_lines.append(f"📌 **Answer:**\n{best_chunk}")
    
    # 📊 Key Details: Additional data from other chunks if available
    if len(relevant_docs) > 1:
        details = []
        for doc in relevant_docs[1:]:
            detail = doc['content'].strip()
            detail = re.sub(r'[-=]{2,}', ' ', detail)
            detail = re.sub(r'\*+', '', detail)
            detail = re.sub(r'\s+', ' ', detail).strip()
            details.append(f"- {detail}")
        response_lines.append(f"\n📊 **Key Details:**\n" + "\n".join(details))
    
    # 📂 Source
    response_lines.append(f"\n📂 **Source:** {', '.join(source_files)}")
    
    response = "\n".join(response_lines)

    return {
        'response': response,
        'source': ', '.join(source_files),
        'confidence': float(relevant_docs[0]['similarity']),
        'referenced_docs': source_files
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
        # Embed in small batches to PREVENT Render Free-Tier OOM memory crashes!
        embeddings = list(embedding_model.embed(chunks, batch_size=4))
        
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
    Uses the RBAC_PERMISSION_MATRIX from prompt_templates for consistency.
    """
    
    # Normalize role for lookup
    role_key = user_role.capitalize() if user_role else 'Employee'
    # Handle special cases
    role_map = {
        'admin': 'Admin',
        'c-level': 'C-Level', 
        'finance': 'Finance',
        'hr': 'HR',
        'marketing': 'Marketing',
        'engineering': 'Engineering',
        'employee': 'Employee'
    }
    role_key = role_map.get(user_role.lower(), 'Employee') if user_role else 'Employee'
    
    # Get permitted departments from the centralized permission matrix
    role_config = RBAC_PERMISSION_MATRIX.get(role_key, RBAC_PERMISSION_MATRIX['Employee'])
    accessible_depts = [d.lower() for d in role_config['accessible_departments']]
    
    # Admin and C-Level have unrestricted access — skip keyword blocking
    if role_key in ['Admin', 'C-Level']:
        return {
            'response': "ℹ️ No relevant data found in your access scope for this query.",
            'access_denied': False,
            'role_info': {'title': role_config['description']}
        }
    
    # Check if query contains restricted cross-departmental keywords
    query_lower = query.lower()
    
    # Department keywords to block for roles that don't have access
    all_dept_keywords = {
        'finance': ['expense', 'revenue', 'budget', 'p&l', 'tax', 'invoice', 'profit', 'cost', 'financial'],
        'hr': ['employee', 'payroll', 'attendance', 'hiring', 'turnover', 'benefits', 'salary'],
        'marketing': ['campaign', 'analytics', 'leads', 'brand', 'social media', 'conversion', 'roi'],
        'engineering': ['api', 'architecture', 'deployment', 'server', 'endpoint', 'uptime'],
        'admin': ['audit log', 'system config', 'security', 'user management'],
        'c-level': ['strategic', 'executive', 'board', 'kpi']
    }
    
    # Build list of blocked keywords: any department NOT in the user's accessible list
    blocked_keywords = []
    for dept, keywords in all_dept_keywords.items():
        if dept not in accessible_depts and dept != 'general':
            blocked_keywords.extend(keywords)
    
    access_denied = False
    for keyword in blocked_keywords:
        if keyword in query_lower:
            access_denied = True
            break
    
    if access_denied:
        return {
            'response': "⛔ Access Denied: You do not have permission to view this information.",
            'access_denied': True,
            'role_info': {'title': role_config['description']}
        }
    
    return {
        'response': "ℹ️ No relevant data found in your access scope for this query.",
        'access_denied': False,
        'role_info': {'title': role_config['description']}
    }

