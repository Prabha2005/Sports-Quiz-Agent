from typing import List, Dict
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


class SearchService:
    """Service class encapsulating sports news web searches and deduplication."""

    def __init__(self):
        pass

    def search_recent_news(self, sport: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Searches DuckDuckGo for recent sports news and deduplicates articles by URL.
        Returns a list of dicts with keys: 'title', 'body', 'href'.
        """
        queries = [
            f"{sport} latest match results",
            f"{sport} latest tournament winner",
            f"{sport} recent player news"
        ]

        results_list = []
        seen_links = set()

        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = ddgs.text(query, max_results=max_results)
                    for result in results:
                        href = result.get("href", "")
                        if not href or href in seen_links:
                            continue

                        seen_links.add(href)
                        results_list.append({
                            "title": result.get("title", ""),
                            "body": result.get("body", ""),
                            "href": href
                        })

                        if len(results_list) >= max_results:
                            return results_list
        except Exception as e:
            print(f"SearchService Error: {e}")

        return results_list
