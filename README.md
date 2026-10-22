# Bookstore Dashboard

Itransition Intern Data Engineer, Task 4.
Live demo: https://booksdashboard.onrender.com/
(free hosting: the first load after idle takes about a minute)

## Run locally

Install dependencies:

```
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Anthropic API key (needed only for the chat):

```
ANTHROPIC_API_KEY=your_key_here
```

Start the server and open http://127.0.0.1:8000

```
python -m uvicorn app:app --reload --env-file .env
```

The data (`Data/STORE1..STORE5`) is already in the repo. Without a key the dashboard works, only the chat does not.

## How the chat works

The model never receives the raw data. It only sees descriptions of the available functions (tools), such as `get_unique_users` or `get_revenue`. When you ask a question, the model chooses a function and its arguments; the server runs it on the already computed metrics and sends back only the result (a number, a short list, a profile). The model then phrases the answer.

## Dashboard control (optional part)

Some tools also return a UI command that the page executes:

- "Show users of STORE1 whose e-mail starts with s or p" opens the Users tab with the filter applied.
- "Show STORE1 revenue for January 2026" opens the Revenue tab with the chart limited to that range.

A plain question like "how much revenue in January?" is answered in text and does not change the page.

Not implemented: filtering books by people's names in the title.
