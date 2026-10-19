from actions.search.web_search import WebSearchAction


search = WebSearchAction()

result = search.execute("artificial intelligence")

print(result)