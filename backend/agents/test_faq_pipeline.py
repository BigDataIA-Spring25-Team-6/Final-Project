import sys
import os

# Allow importing from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.agents.crew_config import run_faq_pipeline

# Sample FAQ query
faq_query = "What are common software engineer interview questions asked at Google?"

# Optional filters
job_role = "Software Engineer"
company = "Google"

# Run the FAQ pipeline
result = run_faq_pipeline(
    faq_query=faq_query,
    job_role=job_role,
    company=company
)

print("\n--- FAQ Agent Response ---\n")
if result.get("status") == "error":
    print(f"❌ Error: {result['message']}")
else:
    print(f"📌 Query: {result['faq_query']}")
    print(f"🔍 Role: {result['job_role']}")
    print(f"🏢 Company: {result['company']}\n")
    print("🧠 FAQ Answer:\n")
    print(result["faq_response"].tasks_output[0].raw)  # LLM's full answer
    print("\n✅ Done.")
    
    # If summary is included
    if result.get("summary"):
        print("\n📋 Summary:")
        print(result["summary"])
