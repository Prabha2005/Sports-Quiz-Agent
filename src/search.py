from ddgs import DDGS


def search_latest_news(sport: str, max_results: int = 3):
    """
    Search for the latest news related to a sport.
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

                    # Skip duplicates
                    if href in seen_links:
                        continue

                    seen_links.add(href)

                    results_list.append({
                        "title": result.get("title", ""),
                        "body": result.get("body", ""),
                        "href": href
                    })

                    # Keep only top 3 unique results
                    if len(results_list) >= max_results:
                        return results_list

    except Exception as e:
        print(f"Search Error: {e}")

    return results_list