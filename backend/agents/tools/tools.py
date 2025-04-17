from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
from utils.pinecone_query import query_pinecone_chunks 

# Define input schema for the tool
class FetchRelevantChunksInput(BaseModel):
    query: str = Field(..., description="Query to search relevant Reddit chunks")
    role: str = Field(None, description="Optional job role filter")
    company: str = Field(None, description="Optional company filter")

# Tool definition
class FetchRelevantChunksFromPineconeTool(BaseTool):
    name: str = "fetch_relevant_chunks"
    description: str = "Fetch relevant Reddit discussion chunks from Pinecone using semantic search and optional filters"
    args_schema: type = FetchRelevantChunksInput

    def _run(self, query: str, role: str = None, company: str = None) -> str:
        try:
            results = query_pinecone_chunks(
                query=query,
                role=role,
                company=company,
                api_key=os.getenv("PINECONE_API_KEY"),
                index_name=os.getenv("INDEX_NAME"),
                top_k=5
            )

            if results.get("status") == "error" or not results.get("matches"):
                return results.get("message", f"No relevant chunks found for query '{query}'.")
                #return f"No relevant chunks found for query '{query}'."

            response = ""
            for match in results["matches"]:
                metadata = match.get("metadata", {})
                response += (
                    f"🔹 Title: {metadata.get('title')}\n"
                    f"📌 Subreddit: {metadata.get('subreddit')}\n"
                    f"🧠 Chunk: {metadata.get('text')[:300]}...\n"
                    f"🔗 Link: {metadata.get('permalink')}\n\n"
                )

            return response.strip()

        except Exception as e:
            return f"Error fetching chunks from Pinecone: {str(e)}"
