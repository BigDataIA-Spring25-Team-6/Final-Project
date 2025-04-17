from crewai import Crew, Task
from agents.faq_agent import faq_agent
#from backend.agents.summary_generator import generate_summary_from_tasks  # optional
# If you want summarization of the fetched chunks

def run_faq_pipeline(faq_query: str, job_role: str = None, company: str = None):
    try:
        # Step 1: Define the agent's task using the user's query
        task = Task(
            description=(
                f"You are an interview assistant. Your task is to search Reddit discussion data "
                f"for helpful answers to the following question:\n\n"
                f"'{faq_query}'\n\n"
                f"Use the semantic search tool to find community advice from Reddit chunks stored in Pinecone."
                + (f"\nFilter your results by job role: {job_role}." if job_role else "")
                + (f"\nFilter your results by company: {company}." if company else "")
                + "\nFormat your output as an answer followed by 2–5 relevant Reddit links."
            ),
            expected_output="Helpful response to the user's question with links to relevant Reddit discussions.",
            agent=faq_agent
        )

        # Step 2: Assemble the crew and run the task
        crew = Crew(
            agents=[faq_agent],
            tasks=[task],
            verbose=True
        )

        final_output = crew.kickoff()

        # Step 3 (Optional): Summarize if needed
        #summary = generate_summary_from_tasks(final_output.tasks_output)

        return {
            "faq_query": faq_query,
            "job_role": job_role,
            "company": company,
            "faq_response": final_output,
            #"summary": summary
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

