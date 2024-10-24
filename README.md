# Lantern + Ubicloud Demo for PGConf EU

In this demo, we'll be using Lantern and Ubicloud to build a simple chatbot that can answer questions about the Ubicloud codebase. Feel free to substitute the Ubicloud repository with your own codebase to build your own codebase expert.

Below, we'll show how to build this using open-source embedding models hosted on Ubicloud, and with OpenAI embedding + LLM models.

## Step 0: Create a Lantern database

To get started with Lantern, sign up at [Lantern Cloud](https://lantern.dev) and [Ubicloud](https://ubicloud.com).

Lantern is also [open-source](https://github.com/lanterndata/lantern), so you can self-host it. The `docker-compose.yml` file in this repository can be used to run Lantern locally.

## Step 1: Setup

Set the following environment variables in your `.env` file:

- `DATABASE_URL`
- `UBICLOUD_API_KEY`
- `OPENAI_API_KEY`

Next, load the environment variables

```bash
export $(cat .env | xargs)
```

Then, connect to the database

```bash
psql "$DATABASE_URL"
```

Next, configure the Lantern environment

```sql
ALTER SYSTEM SET lantern_extras.enable_daemon=true;
SELECT pg_reload_conf();
```

Finally, set the database environment variables.

OpenAI:

```bash
psql "$DATABASE_URL" -c "ALTER DATABASE postgres SET lantern_extras.openai_token='$OPENAI_API_KEY'"
```

Ubicloud:

```bash
psql "$DATABASE_URL" -c "ALTER DATABASE postgres SET lantern_extras.openai_token='$UBICLOUD_API_KEY'"
```

## Step 2: Database schema

Run the following command to create the database schema:

```sql
create table files (
    id serial primary key,
    repo text,
    name text,
    code text
);
```

## Step 3: Load the data

First, we'll clone the repo that we want to ask questions about:

```bash
mkdir -p repos
gh repo clone ubicloud/ubicloud repos/ubicloud
```

Then, we'll run the following command to load the files into the database:

```bash
python process_repo.py ubicloud
```

## Step 4: Initialize the LLM completion job

Initialize the LLM completion job:

OpenAI

```sql
SELECT add_completion_job(
    'files',               -- table
    'code',                -- source column
    'description',         -- output column
                           -- system prompt
    'You are a helpful code assistant. You will receive code from a file, and you will summarize what that the code does, including specific interfaces where helpful.',
    'TEXT',                -- output type
    'gpt-4o',              -- model
    50                     -- batch size
);
```

Ubicloud

```bash
psql "$DATABASE_URL" -c "SELECT add_completion_job('files', 'code', 'description', '', 'TEXT', 'llama-3-2-3b-it', 50, 'openai', runtime_params=>'{\"base_url\": \"https://llama-3-2-3b-it.ai.ubicloud.com\", \"api_token\": \"$UBICLOUD_API_KEY\", \"context\": \"You are a helpful code assistant. You will receive code from a file, and you will summarize what that the code does, including specific interfaces where helpful.\" }')"
```

## Step 5: Initialize the embedding generation job

OpenAI

```sql
SELECT add_embedding_job(
    'files',                         -- table
    'description',                   -- source column
    'vector',                        -- output column
    'openai/text-embedding-3-small', -- model
    50                               -- batch size
);
```

Ubicloud

```bash
psql "$DATABASE_URL" -c "SELECT add_embedding_job('files', 'description', 'vector', 'e5-mistral-7b-it', 50, 'openai', runtime_params=>'{\"base_url\": \"https://e5-mistral-7b-it.ai.ubicloud.com\", \"api_token\": \"$UBICLOUD_API_KEY\"}')"
```

## Step 6: Sanity checks

```bash
psql "$DATABASE_URL" -c "SELECT get_completion_jobs()"
psql "$DATABASE_URL" -c "SELECT get_embedding_jobs()"
psql "$DATABASE_URL" -c "SELECT name, description FROM files WHERE description IS NOT NULL LIMIT 1"
psql "$DATABASE_URL" -c "SELECT name, vector FROM files WHERE vector IS NOT NULL LIMIT 1"
```

## Step 7: Run the chatbot to ask questions

```bash
python app.py ubicloud
```

Some sample questions you can ask:

- What embedding models does Ubicloud support?
- How do I enable TLS with the Ubicloud load balancer?
