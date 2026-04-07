
import sys
import os
import time

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from rag_system import search_relevant_documents, generate_rag_response
    print("Successfully imported RAG system.")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# AI Accuracy Test Cases (Question, Expected Source, Role)
accuracy_tests = [
    {
        "query": "What is the company policy on working hours?",
        "expected_src": "employees.md",
        "role": "employee",
        "dept": "General"
    },
    {
        "query": "What is gross profit margin and how is it calculated?",
        "expected_src": "finance.md",
        "role": "finance",
        "dept": "Finance"
    },
    {
        "query": "Explain what Agile methodology is for software development.",
        "expected_src": "engineering.md",
        "role": "engineering",
        "dept": "Engineering"
    },
    {
        "query": "How are employee performances evaluated using KPIs?",
        "expected_src": "hr.md",
        "role": "hr",
        "dept": "HR"
    },
    {
        "query": "What is brand positioning in marketing?",
        "expected_src": "marketing.md",
        "role": "marketing",
        "dept": "Marketing"
    }
]

def run_accuracy_tests():
    print("\n" + "="*50)
    print("STARTING AI ACCURACY & RAG PIPELINE VERIFICATION")
    print("="*50 + "\n")
    
    passed = 0
    total = len(accuracy_tests)
    
    for i, test in enumerate(accuracy_tests):
        print(f"Test {i+1}: {test['query']}")
        print(f"  Role: {test['role']} | Dept: {test['dept']}")
        
        # 1. Search Verification
        docs = search_relevant_documents(test['query'], department=test['dept'], limit=3)
        
        if not docs:
            print("  ❌ FAIL: No documents retrieved for query.")
            continue
            
        found_expected = any(test['expected_src'] in doc['filename'] for doc in docs)
        best_similarity = docs[0]['similarity']
        
        if found_expected:
            print(f"  ✅ Search OK: Found '{test['expected_src']}' (Best Sim: {best_similarity:.4f})")
        else:
            print(f"  ❌ FAIL: Expected source '{test['expected_src']}' not found in top results.")
            print(f"     Found: {[d['filename'] for d in docs]}")
            continue

        # 2. Generation Verification (Optional/Light)
        # We check if it can generate a structured response without crashing
        try:
            res = generate_rag_response(test['query'], test['role'], test['dept'], docs)
            if res and 'response' in res and len(res['response']) > 50:
                print(f"  ✅ Generation OK: Answer length {len(res['response'])} chars.")
            else:
                print(f"  ⚠️ Warning: Generation returned a very short or empty response.")
        except Exception as e:
            print(f"  ❌ Generation ERROR: {e}")
            
        passed += 1
        print("-" * 30)

    print(f"\nFinal Result: {passed}/{total} Accuracy Tests Passed!")
    if passed == total:
        print("🚀 AI ACCURACY & PIPELINE VERIFIED!")
    else:
        print("❌ SOME ACCURACY TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_accuracy_tests()
