import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


def insert_file(file_name, file_content, repo_name):
    cur.execute("""INSERT INTO files ("name", "code", "repo") VALUES (%s, %s, %s);""",
                (file_name, file_content, repo_name))
    conn.commit()


def process_file(file_path, repo_name):
    cur.execute(
        """SELECT 1 FROM files WHERE "name" = %s AND "repo" = %s;""", (file_path, repo_name))
    row = cur.fetchone()
    if row:
        return

    print(file_path)
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_content = f.read()
        insert_file(file_path, file_content, repo_name)


def main(repo_name):
    valid_endings = ['.rb', '.c', '.cpp', '.rs', '.cc', '.h', '.js']

    # Walk through the directory tree
    repo_path = os.path.join('repos', repo_name)
    for root, dirs, files in os.walk(repo_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path) and os.path.splitext(file_name)[-1] in valid_endings:
                process_file(file_path, repo_name)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        repo_name = sys.argv[1]
        main(repo_name)
        cur.close()
        conn.close()
    else:
        print("Usage: python process_repo.py <repo_name>")
