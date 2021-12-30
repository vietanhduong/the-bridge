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

TOKEN = env("TELEGRAM_TOKEN")
GROUP_ID = env("TELEGRAM_GROUP_ID")

RUN_ID = env("GITHUB_RUN_ID")
GITHUB_REPOSITORY = env("GITHUB_REPOSITORY")

CLIENT_PAYLOAD = parse_payload("CLIENT_PAYLOAD")
NEEDS_CONTEXT = parse_payload("NEEDS_CONTEXT")


len(TOKEN) or err("$TELEGRAM_TOKEN is required", exit_code=1)
len(GROUP_ID) or err("$TELEGRAM_GROUP_ID is required", exit_code=1)

TELEGRAM_URI = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
WORKFLOW_URL = f"https://github.com/{GITHUB_REPOSITORY}/actions/runs/{RUN_ID}"


template = f"""
---
"""

payload = {
  "chat_id": GROUP_ID,
  "text": template,
  "parse_mode": "Markdown"
}

request(TELEGRAM_URI, method="POST", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
