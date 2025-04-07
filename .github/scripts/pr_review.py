import os
import requests
import json

# Get PR Diff from environment variable
pr_diff = os.getenv("PR_DIFF", "")
pr_diff = pr_diff.replace("\\n", "\n")  # Convert escaped \n back to newlines

# Skip if empty
if not pr_diff.strip():
    print("No PR diff available.")
    exit(1)

# Prompt
prompt = f"""
You are a code review assistant. You are given:

1. A list of PR changes (diffs)
2. A checklist of important review questions

Your task is:
- Evaluate the PR changes against the checklist.
- Only include checklist items that are relevant to the provided PR changes.
- For each included item, provide a verdict as either ✅ or ❌.

Format the output like this:
Checklist Evaluation:
- [true|false] <checklist item>

PR Changes:
{pr_diff}

Checklist:
- Is the code properly formatted?
- Are there any hardcoded secrets or credentials?
- Are the function and variable names meaningful?
- Does the code have adequate comments and documentation?
- Is there any unused or dead code?
- Are there tests added or updated for the changes?
- Are performance-sensitive areas optimized?
"""

# LLM API endpoint
llm_url = "http://10.24.45.56/v1/chat/completions"

# API Payload
payload = {
    "model": "fk-gpt-large-v3",
    "temperature": 0,
    "max_tokens": 1000,
    "messages": [
        {
            "role": "system",
            "content": "You are a senior code reviewer AI. Your job is to evaluate pull request (PR) changes using a checklist. Be objective, concise, and use ✅ or ❌."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
}

# Call LLM
print("Sending PR diff to LLM...")
res = requests.post(llm_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))

if res.status_code != 200:
    print("Failed to contact LLM:", res.status_code, res.text)
    exit(1)

review_output = res.json()["choices"][0]["message"]["content"]
print("LLM Review:\n", review_output)

# === Post comment on PR ===
repo = os.getenv("GITHUB_REPOSITORY")  # e.g. owner/repo
pr_number = os.getenv("GITHUB_REF").split("/")[-1]  # Pull request number
token = os.getenv("GITHUB_TOKEN")

comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comment_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}
comment_data = {"body": f"### 🤖 LLM PR Review Checklist\n\n{review_output}"}

resp = requests.post(comment_url, headers=comment_headers, data=json.dumps(comment_data))

if resp.status_code == 201:
    print("✅ Comment posted to PR.")
else:
    print("❌ Failed to post comment:", resp.status_code, resp.text)
