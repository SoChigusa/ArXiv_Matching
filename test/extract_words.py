import requests
from bs4 import BeautifulSoup


def fetch_wikipedia_physics_terms():
    url = "https://en.wikipedia.org/wiki/Glossary_of_physics"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    terms = set()
    for item in soup.find_all('dt'):
        term = item.get_text().strip()
        if term:
            terms.add(term.lower())

    return terms


# Example usage
physics_terms = fetch_wikipedia_physics_terms()
print(physics_terms)
