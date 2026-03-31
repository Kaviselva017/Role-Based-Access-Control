import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from rag_system import get_role_based_response

test_cases = [
    {
        "role": "admin",
        "queries": [
            "Give a complete company performance summary",
            "Show financial, HR, and marketing reports together",
            "What are current engineering and product updates?",
            "Provide overall company growth analysis",
            "Show risks across all departments"
        ],
        "restricted": []
    },
    {
        "role": "finance",
        "queries": [
            "What is the latest financial report?",
            "Show quarterly revenue and expenses",
            "What is the company budget allocation?",
            "Give profit and loss summary",
            "What are financial projections?"
        ],
        "restricted": [
            "What is HR leave policy?",
            "Show marketing campaign strategy"
        ]
    },
    {
        "role": "hr",
        "queries": [
            "What is the employee leave policy?",
            "Explain employee benefits",
            "What is the recruitment process?",
            "Show onboarding procedure",
            "What are company HR rules?"
        ],
        "restricted": [
            "Show financial report",
            "What is marketing campaign performance?"
        ]
    },
    {
        "role": "marketing",
        "queries": [
            "What are current marketing campaigns?",
            "Show campaign performance metrics",
            "What is customer acquisition strategy?",
            "Give marketing analytics report",
            "What channels are used for promotion?"
        ],
        "restricted": [
            "Show HR policies",
            "What is financial budget report?"
        ]
    },
    {
        "role": "engineering",
        "queries": [
            "What are current engineering projects?",
            "Explain system architecture",
            "What technologies are used in backend?",
            "Describe deployment pipeline",
            "Show product development roadmap"
        ],
        "restricted": [
            "What is financial revenue?",
            "Show HR policies"
        ]
    },
    {
        "role": "employee",
        "queries": [
            "What is company handbook?",
            "What are general company policies?",
            "Explain company rules",
            "What is code of conduct?",
            "What are working hours?"
        ],
        "restricted": [
            "Financial report",
            "HR detailed policies",
            "Engineering details",
            "Marketing strategy"
        ]
    }
]

failed = False
for tc in test_cases:
    role = tc["role"]
    print(f"Testing Role: {role.upper()}")
    
    # Check allowed
    for q in tc["queries"]:
        res = get_role_based_response(q, role)
        if res.get("access_denied"):
            print(f"  [ERROR] Should be allowed but denied: {q}")
            failed = True
        else:
            print(f"  [OK] Allowed: {q}")
            
    # Check restricted
    for q in tc["restricted"]:
        res = get_role_based_response(q, role)
        if not res.get("access_denied"):
            print(f"  [ERROR] Should be denied but allowed: {q}")
            failed = True
        else:
            print(f"  [OK] Denied: {q}")

if failed:
    sys.exit(1)
print("ALL TESTS PASSED!")
