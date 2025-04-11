import os
import asyncio
import asyncpraw
import time
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from scripts.chunking import embedding_model, cluster_based_chunking


# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("INDEX_NAME")
REDDIT_CLIENT_ID = os.getenv("PRAW_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("PRAW_CLIENT_SECRET")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Embed text using the sentence transformer model
def embed_texts(texts):
    return embedding_model.encode(texts, convert_to_numpy=True)

# Ensure Pinecone index exists
def get_or_create_index():
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        )
    return pc.Index(INDEX_NAME)


def add_chunks_to_pinecone(chunks, post, role=None, company=None):
    index = get_or_create_index()
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    ids = [f"{post['id']}_chunk_{i}" for i in range(len(chunks))]

    metadatas = [{
        "source": post["id"],
        "chunk_index": i,
        "text": chunks[i],
        "title": post["title"],
        "subreddit": post["subreddit"],
        "permalink": f"https://reddit.com/r/{post['subreddit']}/comments/{post['id']}",
        "role": role,
        "company": company
    } for i in range(len(chunks))]

    index.upsert(vectors=[(ids[i], embeddings[i].tolist(), metadatas[i]) for i in range(len(chunks))])
    return len(chunks)

# Reddit async scraper
def init_reddit():
    return asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent='reddit-maang-agent'
    )

async def fetch_interview_tips(subreddits, roles, companies, limit=100, min_upvotes=10):
    reddit = init_reddit()
    posts = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 3, 31)
    start_timestamp = time.mktime(start_date.timetuple())
    end_timestamp = time.mktime(end_date.timetuple())

    search_queries = [f"{role} interview tips {company}" for role in roles for company in companies]

    try:
        for role in roles:
            for company in companies:
                query = f"{role} interview tips {company}"
                for subreddit_name in subreddits:
                    subreddit = await reddit.subreddit(subreddit_name)
                    async for post in subreddit.search(query, limit=limit, sort='relevance'):
                        if (
                            post.score >= min_upvotes and
                            not post.stickied and
                            start_timestamp <= post.created_utc < end_timestamp
                        ):
                            posts.append({
                                'id': post.id,
                                'title': post.title,
                                'text': post.selftext,
                                'subreddit': subreddit_name,
                                'role': role,
                                'company': company  # ✅ Include these here
                            })

        # for subreddit_name in subreddits:
        #     subreddit = await reddit.subreddit(subreddit_name)
        #     for query in search_queries:
        #         async for post in subreddit.search(query, limit=limit, sort='relevance'):
        #             if post.score >= min_upvotes and not post.stickied and start_timestamp <= post.created_utc < end_timestamp:
        #                 posts.append({
        #                     'id': post.id,
        #                     'title': post.title,
        #                     'text': post.selftext,
        #                     'subreddit': subreddit_name
        #                 })
    finally:
        await reddit.close()  # ✅ This cleans up the client session

    return posts


async def pinecone_rag_from_reddit():
    subreddits = [
        'cscareerquestions', 'datascience', 'dataengineering', 'MachineLearning',
        'learnprogramming', 'leetcode', 'programming', 'softwareengineering',
        'dataanalysis', 'bigdata', 'artificial', 'computerscience', 'careeradvice',
        'jobs', 'engineering', 'technology', 'developer', 'coding', 'ITCareerQuestions', 'interviews'
    ]
    roles = [
        'Software Engineer', 'Data Engineer', 'Data Scientist',
        'Data Analyst', 'Machine Learning Engineer', 'AI Engineer'
    ]
    companies = ['Meta', 'Amazon', 'Apple', 'Netflix', 'Google']

    for role in roles:
        for company in companies:
            posts = await fetch_interview_tips(subreddits, [role], [company], limit=1)
            for post in posts:
                document_text = post['title'] + "\n\n" + post['text']
                chunks = cluster_based_chunking(document_text, max_chunk_size=500)
                add_chunks_to_pinecone(chunks, post, role=role, company=company)

    print(f"Uploaded all posts using cluster-based chunking with role and company metadata.")

# # Entry point
# if __name__ == "__main__":
#     asyncio.run(pinecone_rag_from_reddit())

def pinecone_rag_airflow(subreddits, roles, companies, limit=1, max_chunk_size=500):
    """
    Airflow-compatible wrapper that fetches Reddit data and uploads to Pinecone.
    All inputs are passed as arguments (no hardcoded config).
    """

    # Run the async Reddit fetcher
    posts = asyncio.run(fetch_interview_tips(subreddits, roles, companies, limit=limit))

    for role in roles:
        for company in companies:
            for post in posts:
                document_text = post["title"] + "\n\n" + post["text"]
                chunks = cluster_based_chunking(document_text, max_chunk_size=max_chunk_size)
                add_chunks_to_pinecone(chunks, post, role=role, company=company)

    print(f"✅ Uploaded Reddit posts using cluster-based chunking.")
