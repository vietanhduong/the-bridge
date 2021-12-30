#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: @vietanhduong
#
import argparse
import os
import sys
import json 
import urllib.request

def env(key: str, default="") -> str:
    return os.getenv(key) or default

def err(msg, **kwargs):
    print(f"ERROR: {msg}", file=sys.stderr, **kwargs)
    exit_code = kwargs.get('exit_code')
    if exit_code is not None:
      exit(exit_code)

def request(url: str, method: str = "GET", data=None, headers: dict = {}, insecure=False) -> dict:
    try:
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        res = urllib.request.urlopen(req, context=ssl._create_unverified_context() if insecure else None)
        content = res.read().decode("utf-8") or "{}"
        return { "code": res.getcode(), "response": content }
    except urllib.error.HTTPError as e:
        err(f"URL: {url}")
        err(f"Respone code: {e.code} - Message: {e.msg}")
        return None

def parse_payload(key: str) -> dict:
    raw = env(key, None)
    if not raw: 
      return None
    return json.loads(raw)

def handle_needs_context(key: str, repo_name: str) -> str:
  """
    needs_context format:
      {
        "test": {
          "result": "success",
          "outputs": {}
        },
        "docker": {
          "result": "failure",
          "outputs": {}
        }
      }
  """ 
  needs_context = parse_payload(key) 
  icons = {
    "success": "✅",
    "failure": "❌",
    "cancelled": "❗️",
    "skipped": "🚫",
    "unknown": "⚠️"
  }  
  messages = []
  for key, value in needs_context.items():
    result = value.get("result", "unknown")
    messages.append(f"*{key}*: {icons.get(result, 'unknown')} {result}") 
  
  return '\n'.join(messages)

def format_gitlab_url(git_url: str) -> str:
  if git_url.endswith('.git'):
   git_url = git_url[:-len('.git')] 
 
  if git_url.startswith("https://"):
   git_url = git_url[:-len('https://')] 
  
  return f"https://{git_url}"
  
def format_commit_hash(commit_hash: str) -> str:
  if len(commit_hash) < 7:
    return commit_hash
  return commit_hash[:7]

TOKEN = env("TELEGRAM_TOKEN")
GROUP_ID = env("TELEGRAM_GROUP_ID")

RUN_ID = env("GITHUB_RUN_ID")
GITHUB_REPOSITORY = env("GITHUB_REPOSITORY")

len(TOKEN) or err("$TELEGRAM_TOKEN is required", exit_code=1)
len(GROUP_ID) or err("$TELEGRAM_GROUP_ID is required", exit_code=1)

TELEGRAM_URI = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
WORKFLOW_URL = f"https://github.com/{GITHUB_REPOSITORY}/actions/runs/{RUN_ID}"

client_payload = parse_payload("CLIENT_PAYLOAD")
repo_name = client_payload.get("repo_name")
git_url = client_payload.get("git_url")
commit_message = client_payload.get("commit_message")
commit_hash = client_payload.get("sha")

template = f"""**[Bridge CI]** {repo_name}
*Commit message*: {commit_message}
*Commit hash*: [{format_commit_hash(commit_hash)}]({format_gitlab_url(git_url)}/-/commit/{commit_hash})
---
{handle_needs_context("NEEDS_CONTEXT", repo_name)}
---
*Workflow:* [View Workflow]({WORKFLOW_URL})
"""

payload = {
  "chat_id": GROUP_ID,
  "text": template,
  "parse_mode": "Markdown"
}

request(TELEGRAM_URI, method="POST", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
