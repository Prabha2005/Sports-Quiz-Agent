from src.search import search_latest_news

news = search_latest_news("Cricket")

print("\nLatest Cricket News\n")

for i, item in enumerate(news, start=1):
    print(f"News {i}")
    print("Title :", item["title"])
    print("Body  :", item["body"])
    print("Link  :", item["href"])
    print("-" * 60)