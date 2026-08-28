import csv
import os
import time
from datetime import datetime, timedelta
import requests

# Set working directory to project directory
OUTPUT_DIR = r"E:\ai_pro_project"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_FILE = os.path.join(OUTPUT_DIR, "hn_mentions_log.csv")

TOOLS = [
    "LangChain",
    "CrewAI",
    "LlamaIndex",
    "AutoGen",
    "Semantic Kernel",
    "Haystack",
    "DSPy",
    "LiteLLM",
    "Instructor",
    "Phidata",
    "Mem0",
    "vLLM",
    "Ollama",
    "TGI",
    "LlamaCpp",
    "LM Studio",
    "Chroma",
    "Pinecone",
    "Milvus",
    "Qdrant",
    "Weaviate",
    "Flowise",
    "Langflow",
    "Open WebUI",
]


def fetch_hn_mentions(query):
    base_url = "http://hn.algolia.com/api/v1/search"

    # Overall mentions
    p_all = {"query": f'"{query}"', "hitsPerPage": 0}
    res_all = requests.get(base_url, params=p_all).json()
    total_mentions = res_all.get("nbHits", 0)

    # Last 90 days
    ninety_days_ago = int((datetime.now() - timedelta(days=90)).timestamp())
    p_90 = {
        "query": f'"{query}"',
        "numericFilters": f"created_at_i>{ninety_days_ago}",
        "hitsPerPage": 0,
    }
    res_90 = requests.get(base_url, params=p_90).json()
    mentions_90d = res_90.get("nbHits", 0)

    return total_mentions, mentions_90d


def main():
    print("Fetching Hacker News mentions...")
    today = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists(CSV_FILE)

    rows = []
    for tool in TOOLS:
        try:
            total, m90 = fetch_hn_mentions(tool)
            rows.append(
                {
                    "snapshot_date": today,
                    "tool": tool,
                    "hn_total_mentions": total,
                    "hn_mentions_last_90d": m90,
                }
            )
            print(f"  └─ [{tool}] Total: {total} | 90d: {m90}")
            time.sleep(0.2)
        except Exception as e:
            print(f"  └─ Error fetching {tool}: {e}")

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "snapshot_date",
                "tool",
                "hn_total_mentions",
                "hn_mentions_last_90d",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved HN mentions to: {CSV_FILE}")


if __name__ == "__main__":
    main()