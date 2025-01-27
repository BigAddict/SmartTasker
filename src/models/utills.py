from bs4 import BeautifulSoup
import requests

def extract_links_and_names(url: str) -> dict:
    """
    Extracts all links and their corresponding link names from a given webpage.

    Args:
        url: The URL of the webpage to extract links from.

    Returns:
        A list of tuples, where each tuple contains the link URL and its corresponding link name.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                link_name = link.text.strip()
                links.append((href, link_name))

        return links

    except requests.exceptions.RequestException as e:
        return {'error': e}