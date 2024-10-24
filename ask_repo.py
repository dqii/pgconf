import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# OpenAI Settings
# PROVIDER = 'openai'
# COMPLETION_MODEL = "gpt-4o-mini"
# EMBEDDING_MODEL = "openai/text-embedding-3-small"

# Ubicloud Settings
PROVIDER = 'ubicloud'
COMPLETION_MODEL = "llama-3-2-3b-it"
EMBEDDING_MODEL = "e5-mistral-7b-it"
EMBEDDING_URL = "https://e5-mistral-7b-it.ai.ubicloud.com"
COMPLETION_URL = "https://llama-3-2-3b-it.ai.ubicloud.com"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


def query_files(repo, question, top_k=10):
    if PROVIDER == 'openai':
        query = """
            SELECT "name", "description" 
            FROM files 
            WHERE repo = %s
            ORDER BY vector <-> openai_embedding(%s, %s)
            LIMIT %s
        """
        cur.execute(query, (repo, EMBEDDING_MODEL, question, top_k))
    else:
        query = """
            SELECT "name", "description" 
            FROM files 
            WHERE repo = %s
            ORDER BY vector <-> openai_embedding(%s, %s, %s)
            LIMIT %s
        """
        cur.execute(query, (repo, EMBEDDING_MODEL,
                    question, EMBEDDING_URL, top_k))
    files = cur.fetchall()
    return files


def ask_question(repo, question):
    files = query_files(repo, question)

    system_prompt = f"You are a helpful agent who answers questions about the {repo} codebase. You will be given context about the codebase and asked questions about it. Please provide detailed answers to the best of your ability."

    context = ""
    file_count = len(files)
    for i in range(file_count):
        name, description = files[i]
        context += f"FILE {i+1} / {file_count}: {name}\n{description}\n\n"
    if not context:
        return "No relevant information found to answer your question."
    user_prompt = '\n'.join([
        f"Answer the question about the {repo} repo using the provided context. Cite specific portions of the given context if they were relevant to answering the question.",
        '-------------------------------',
        f"QUESTION: {question}",
        '-------------------------------',
        f"CONTEXT: {context}"
    ])

    if PROVIDER == 'openai':
        query = "SELECT llm_completion(%s, %s, %s)"
        cur.execute(query, (user_prompt, COMPLETION_MODEL, system_prompt))
    else:
        query = "SELECT llm_completion(%s, %s, %s, %s)"
        cur.execute(query, (user_prompt, COMPLETION_MODEL,
                    system_prompt, COMPLETION_URL))
    answer = cur.fetchone()[0]
    return answer


if __name__ == "__main__":
    if len(sys.argv) == 3:
        repo_name = sys.argv[1]
        question = sys.argv[2]
        answer = ask_question(repo_name, question)
        print(answer)
    repo_name = sys.argv[1]
    question = sys.argv[2]
    answer = ask_question(repo_name, question)
    print(answer)

    # Close database connection
    cur.close()
    conn.close()
