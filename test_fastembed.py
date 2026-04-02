import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    print("Testing FastEmbed integration...")
    from fastembed import TextEmbedding
    
    # Initialize model
    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("✓ Model initialized successfully")

    # Test embedding
    texts = ["How do I access HR documents?", "Company policy on remote work"]
    embeddings = list(model.embed(texts))
    
    print(f"✓ Generated {len(embeddings)} embeddings")
    print(f"✓ Vector dimension: {len(embeddings[0])}")
    
    # Test similarity logic
    import numpy as np
    def cosine_similarity_np(a, b):
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)

    sim = cosine_similarity_np(embeddings[0], embeddings[1])
    print(f"✓ Similarity between test sentences: {sim:.4f}")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    if "fastembed" in str(e):
        print("Tip: Run 'pip install fastembed' first.")
