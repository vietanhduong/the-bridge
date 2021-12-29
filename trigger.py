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
    # Get environment variable, return default vaule (empty string) 
    # if the key does not exist else return value of the key. 
    return os.getenv(key) or default 


def err(msg, **kwargs):
    # Print error message in Stderr
    print(f"ERROR: {msg}", file=sys.stderr, **kwargs)


def info(msg, **kwargs):
    # Print info message in Stdout
    print(f"INFO: {msg}", file=sys.stdout, **kwargs)


def request(url: str, method: str = "GET", data=None, headers: dict = {}, insecure=False) -> dict:
    # Send a HTTP request using urllib. This function does not raise an error,
    # instead it will exit with code 1. This function support insecure request.
    try:
        req = urllib.request.Request(
            url, data=data, method=method, headers=headers)
        res = urllib.request.urlopen(
            req, context=ssl._create_unverified_context() if insecure else None)
        return {
            "code": res.getcode(),
            "response": json.loads(res.read().decode("utf-8"))
        }
    except urllib.error.HTTPError as e:
        err(f"URL: {url}")
        err(f"Respone code: {e.code} - Message: {e.msg}")
        return None


def cat(path: str) -> str:
    # Open the file in text mode, read it, and close the file.
    f = Path(path)
    if not f.is_file():
        err(f"{path}: No such file or directory")
    return f.read_text()

def required(key: str) -> str: 
  value = env(key, None) 
  if value is None: 
    err(f"${key} is required")
    exit(1)

BRIDGE_REPO = "the-bridge"
BRIDGE_OWNER = "vietanhduong"

REPO_NAME = required("CI_PROJECT_NAME")
GH_PAT = required("GH_PAT")
BRANCH = env("CI_COMMIT_BRANCH", "master")
COMMIT_HASH = env("CI_COMMIT_SHA")

payload = {
  "event_type": REPO_NAME,
  "client_payload": {
    "branch": BRANCH,
    "sha": COMMIT_HASH
  }
}

headers = {
  "Accept": "application/vnd.github.v3+json",
  "Authorization": f"token {GH_PAT}"
}

resp = request(f"https://api.github.com/repos/{BRIDGE_OWNER}/{BRIDGE_REPO}/dispatches", method="POST", data=payload, headers=headers)
if resp is None:
  exit(1)

info("Trigger to brigde successful!")
exit(0)
