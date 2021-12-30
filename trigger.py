#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import json
import ssl
import urllib.request
from pathlib import Path
from datetime import datetime

def env(key: str, default="") -> str:
    return os.getenv(key) or default 

def err(msg, **kwargs):
    print(f"ERROR: {msg}", file=sys.stderr, **kwargs)

def info(msg, **kwargs):
    print(f"INFO: {msg}", file=sys.stdout, **kwargs)

def request(url: str, method: str = "GET", data=None, headers: dict = {}, insecure=False) -> dict:
    try:
        req = urllib.request.Request(
            url, data=data, method=method, headers=headers)
        res = urllib.request.urlopen(
            req, context=ssl._create_unverified_context() if insecure else None)

        content = res.read().decode("utf-8") or "{}"
        return { "code": res.getcode(), "response": content }
    except urllib.error.HTTPError as e:
        err(f"URL: {url}")
        err(f"Respone code: {e.code} - Message: {e.msg}")
        return None

def cat(path: str) -> str:
    f = Path(path)
    if not f.is_file():
        err(f"{path}: No such file or directory")
    return f.read_text()

def required(key: str) -> str: 
  value = env(key, None) 
  if value is None: 
    err(f"${key} is required")
    exit(1)
  return value 
  
BRIDGE_REPO = "the-bridge"
BRIDGE_OWNER = "vietanhduong"

REPO_NAME = required("CI_PROJECT_NAME")
GH_PAT = required("GH_PAT")
BRANCH = env("CI_COMMIT_BRANCH", "master")
COMMIT_HASH = env("CI_COMMIT_SHA")
GITLAB_SERVER = env("CI_SERVER_HOST")

payload = {
  "event_type": REPO_NAME,
  "client_payload": {
    "git_url": f"{GITLAB_SERVER}/{env('CI_PROJECT_NAMESPACE')}/{REPO_NAME}.git",
    "repo_name": REPO_NAME,
    "branch": BRANCH,
    "sha": COMMIT_HASH,
    "depth": env("GIT_DEPTH")
  }
}

headers = {
  "Accept": "application/vnd.github.v3+json",
  "Authorization": f"token {GH_PAT}"
}

info(f"Payload: {payload}")
resp = request(f"https://api.github.com/repos/{BRIDGE_OWNER}/{BRIDGE_REPO}/dispatches",
               method="POST", 
               data=json.dumps(payload).encode("utf-8"), 
               headers=headers)

if resp is None:
  exit(1)

info("Trigger to brigde successful!")
