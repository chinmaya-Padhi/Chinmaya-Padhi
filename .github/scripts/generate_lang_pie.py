#!/usr/bin/env python3
"""
generate_lang_pie.py
Generate a pie chart of languages used across all public repos for a GitHub user.

Usage:
  # (option A) without auth (rate-limited)
  python generate_lang_pie.py --user YOUR_GITHUB_USERNAME

  # (option B) with a GitHub token (recommended for many repos / to avoid rate limits):
  export GITHUB_TOKEN="ghp_xxx..."
  python generate_lang_pie.py --user YOUR_GITHUB_USERNAME

Output:
  languages_pie.png
"""
import os
import sys
import math
import argparse
import requests
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt

API_BASE = "https://api.github.com"

def get_json(url, token=None, params=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def fetch_all_repos(username, token=None):
    repos = []
    page = 1
    per_page = 100
    while True:
        params = {"per_page": per_page, "page": page, "type": "owner"}
        url = f"{API_BASE}/users/{username}/repos"
        batch = get_json(url, token=token, params=params)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return repos

def fetch_repo_languages(owner, repo_name, token=None):
    url = f"{API_BASE}/repos/{owner}/{repo_name}/languages"
    return get_json(url, token=token)

def aggregate_languages(repos, token=None):
    totals = defaultdict(int)
    for r in repos:
        owner = r['owner']['login']
        name = r['name']
        try:
            langs = fetch_repo_languages(owner, name, token=token)
        except requests.HTTPError as e:
            print(f"Warning: failed to fetch languages for {owner}/{name}: {e}", file=sys.stderr)
            continue
        for lang, bytes_count in langs.items():
            totals[lang] += bytes_count
    return totals

def prepare_pie_data(totals, min_pct_display=2.0):
    total_bytes = sum(totals.values())
    if total_bytes == 0:
        return [], []
    # compute percentages
    items = [(lang, bytes_count, (bytes_count/total_bytes)*100) for lang, bytes_count in totals.items()]
    # sort by bytes desc
    items.sort(key=lambda x: x[1], reverse=True)

    # group small slices into "Other"
    labels = []
    sizes = []
    other_size = 0.0
    for lang, bytes_count, pct in items:
        if pct < min_pct_display:
            other_size += bytes_count
        else:
            labels.append(f"{lang} ({pct:.1f}%)")
            sizes.append(bytes_count)
    if other_size > 0:
        other_pct = (other_size/total_bytes)*100
        labels.append(f"Other ({other_pct:.1f}%)")
        sizes.append(other_size)

    return labels, sizes

def draw_pie(labels, sizes, out_path="languages_pie.png"):
    if not labels or not sizes:
        # Create a placeholder image
        plt.figure(figsize=(6,4))
        plt.text(0.5, 0.5, "No language data", ha="center", va="center", fontsize=14)
        plt.axis('off')
        plt.savefig(out_path, bbox_inches='tight', dpi=120)
        plt.close()
        print(f"Wrote placeholder image to {out_path}")
        return

    # convert sizes to percents for autopct
    total = sum(sizes)
    def autopct(pct):
        # display percent with one decimal
        return f"{pct:.1f}%"

    plt.figure(figsize=(7,7))
    patches, texts, autotexts = plt.pie(sizes, labels=None, autopct=autopct, startangle=140)
    plt.legend(patches, labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title("Languages used across repos")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Wrote pie chart to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", "-u", required=True, help="GitHub username to analyze")
    parser.add_argument("--out", "-o", default="languages_pie.png", help="Output image path")
    parser.add_argument("--min-pct", type=float, default=2.0, help="Min percent to show a separate slice; smaller grouped into 'Other'")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")  # optional
    print(f"Fetching repos for user: {args.user} (auth={'yes' if token else 'no'})")
    repos = fetch_all_repos(args.user, token=token)
    print(f"Found {len(repos)} repos. Aggregating languages...")
    totals = aggregate_languages(repos, token=token)

    if not totals:
        print("No language bytes found (maybe repos are empty or private). Producing placeholder image.")
    labels, sizes = prepare_pie_data(totals, min_pct_display=args.min_pct)
    draw_pie(labels, sizes, out_path=args.out)

if __name__ == "__main__":
    main()
