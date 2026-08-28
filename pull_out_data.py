import os
import time
import requests
import pandas as pd
from datetime import datetime

# Global Configuration (Add GitHub Personal Access Token if hitting rate limits)
GITHUB_TOKEN = "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"

# Corrected 24 Core AI Tools Mapping
AI_TOOLS = [
    # Frameworks & Agents
    {"name": "LangChain", "repo": "langchain-ai/langchain", "pypi": "langchain", "so_tag": "langchain"},
    {"name": "CrewAI", "repo": "crewAIInc/crewAI", "pypi": "crewai", "so_tag": "crewai"},
    {"name": "LlamaIndex", "repo": "run-llama/llama_index", "pypi": "llama-index-core", "so_tag": "llama-index"},
    {"name": "AutoGen", "repo": "microsoft/autogen", "pypi": "pyautogen", "so_tag": "autogen"},
    {"name": "SemanticKernel", "repo": "microsoft/semantic-kernel", "pypi": "semantic-kernel", "so_tag": "semantic-kernel"},
    {"name": "Haystack", "repo": "deepset-ai/haystack", "pypi": "haystack-ai", "so_tag": "haystack"},
    {"name": "DSPy", "repo": "stanfordnlp/dspy", "pypi": "dspy", "so_tag": "dspy"},
    {"name": "LiteLLM", "repo": "BerriAI/litellm", "pypi": "litellm", "so_tag": "litellm"},
    {"name": "Instructor", "repo": "jxnl/instructor", "pypi": "instructor", "so_tag": "instructor"},
    {"name": "Phidata", "repo": "agno-agi/agno", "pypi": "agno", "so_tag": "phidata"},
    {"name": "Mem0", "repo": "mem0ai/mem0", "pypi": "mem0ai", "so_tag": "mem0"},

    # Inference & Local LLM Serving
    {"name": "vLLM", "repo": "vllm-project/vllm", "pypi": "vllm", "so_tag": "vllm"},
    {"name": "Ollama", "repo": "ollama/ollama", "pypi": None, "so_tag": "ollama"},
    {"name": "TGI", "repo": "huggingface/text-generation-inference", "pypi": None, "so_tag": "text-generation-inference"},
    {"name": "LlamaCpp", "repo": "ggerganov/llama.cpp", "pypi": "llama-cpp-python", "so_tag": "llama.cpp"},
    {"name": "LMStudio", "repo": "lmstudio-ai/lmstudio-python", "pypi": "lmstudio", "so_tag": "lm-studio"},

    # Vector Databases
    {"name": "Chroma", "repo": "chroma-core/chroma", "pypi": "chromadb", "so_tag": "chromadb"},
    {"name": "Pinecone", "repo": "pinecone-io/pinecone-python-client", "pypi": "pinecone-client", "so_tag": "pinecone"},
    {"name": "Milvus", "repo": "milvus-io/milvus", "pypi": "pymilvus", "so_tag": "milvus"},
    {"name": "Qdrant", "repo": "qdrant/qdrant", "pypi": "qdrant-client", "so_tag": "qdrant"},
    {"name": "Weaviate", "repo": "weaviate/weaviate", "pypi": "weaviate-client", "so_tag": "weaviate"},

    # UI / Visual Workflow Tools
    {"name": "Flowise", "repo": "FlowiseAI/Flowise", "pypi": None, "so_tag": "flowise"},
    {"name": "Langflow", "repo": "langflow-ai/langflow", "pypi": "langflow", "so_tag": "langflow"},
    {"name": "OpenWebUI", "repo": "open-webui/open-webui", "pypi": "open-webui", "so_tag": "open-webui"}
]


def get_github_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN.strip():
        headers["Authorization"] = f"token {GITHUB_TOKEN.strip()}"
    return headers


def fetch_github_data(repo):
    """Fetches stars, forks, open issues, and 52-week commit participation history."""
    headers = get_github_headers()
    repo_url = f"https://api.github.com/repos/{repo}"
    
    res = requests.get(repo_url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"GitHub API Error [{res.status_code}]: {res.text}")
    
    repo_data = res.json()
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    open_issues = repo_data.get("open_issues_count", 0)

    stats_url = f"https://api.github.com/repos/{repo}/stats/participation"
    res_stats = requests.get(stats_url, headers=headers)
    
    weekly_commits = []
    if res_stats.status_code == 200:
        stats_data = res_stats.json()
        weekly_commits = stats_data.get("all", [])
    elif res_stats.status_code == 202:
        weekly_commits = []
    
    if not weekly_commits or len(weekly_commits) < 52:
        weekly_commits = (weekly_commits + [0] * 52)[:52]

    return {
        "stars": stars,
        "forks": forks,
        "open_issues": open_issues,
        "weekly_commits": weekly_commits
    }


def fetch_pypi_downloads(package_name, retries=2):
    """Fetches last month's download statistics from PyPI Stats API with retry logic."""
    if not package_name:
        return None
    
    url = f"https://pypistats.org/api/packages/{package_name}/recent?period=month"
    headers = {"User-Agent": "DataEngineerPipeline/1.0"}

    for attempt in range(retries + 1):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return data.get("data", {}).get("last_month", 0)
        except Exception:
            pass
        time.sleep(1)  # Pause briefly before retry
        
    return None


def fetch_stackoverflow_questions(tag_name):
    """Fetches total question volume count from Stack Overflow API."""
    if not tag_name:
        return 0
    
    url = f"https://api.stackexchange.com/2.3/tags/{tag_name}/info?site=stackoverflow"
    res = requests.get(url, timeout=10)
    
    if res.status_code != 200:
        return 0
    
    data = res.json()
    items = data.get("items", [])
    if items:
        return items[0].get("count", 0)
    
    return 0


def main():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    snapshot_records = []
    commit_records = []

    print(f"Starting data ingestion run for {today_str}...\n")

    for tool in AI_TOOLS:
        name = tool["name"]
        repo = tool["repo"]
        pypi = tool["pypi"]
        so_tag = tool["so_tag"]

        print(f"[{name}] Fetching metrics...")

        stars, forks, open_issues = None, None, None
        weekly_commits = [0] * 52
        pypi_downloads = None
        so_questions = 0

        # Fetch GitHub
        try:
            gh_data = fetch_github_data(repo)
            stars = gh_data["stars"]
            forks = gh_data["forks"]
            open_issues = gh_data["open_issues"]
            weekly_commits = gh_data["weekly_commits"]
            print(f"  └─ GitHub: {stars} stars, {forks} forks")
        except Exception as e:
            print(f"  └─ GitHub Error: {e}")

        # Fetch PyPI
        try:
            pypi_downloads = fetch_pypi_downloads(pypi)
            print(f"  └─ PyPI Monthly Downloads: {pypi_downloads}")
        except Exception as e:
            print(f"  └─ PyPI Error: {e}")

        # Fetch Stack Overflow
        try:
            so_questions = fetch_stackoverflow_questions(so_tag)
            print(f"  └─ Stack Overflow Questions: {so_questions}")
        except Exception as e:
            print(f"  └─ Stack Overflow Error: {e}")

        # Append to snapshot log
        snapshot_records.append({
            "snapshot_date": today_str,
            "tool": name,
            "repo": repo,
            "pypi_package": pypi if pypi else "N/A",
            "github_stars": stars,
            "github_forks": forks,
            "github_open_issues": open_issues,
            "pypi_last_month_downloads": pypi_downloads,
            "stackoverflow_question_count": so_questions
        })

        # Append to weekly commit history
        for idx, commits in enumerate(weekly_commits):
            commit_records.append({
                "tool": name,
                "week_index": idx,
                "commits": commits
            })

        time.sleep(1)
        print("-" * 40)

    # Convert to DataFrames and Save CSVs
    snapshot_df = pd.DataFrame(snapshot_records)
    commit_df = pd.DataFrame(commit_records)

    snapshot_file = "snapshot_log.csv"
    commit_file = "commit_history_weekly.csv"

    snapshot_df.to_csv(snapshot_file, index=False)
    commit_df.to_csv(commit_file, index=False)

    print(f"\nExecution Complete.")
    print(f"Saved snapshot metrics to: {os.path.abspath(snapshot_file)}")
    print(f"Saved commit history to: {os.path.abspath(commit_file)}")


if __name__ == "__main__":
    main()