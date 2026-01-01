import logging
from copy import deepcopy

import requests
from bs4 import BeautifulSoup
from trafilatura import extract, fetch_url
from trafilatura.settings import DEFAULT_CONFIG as TRF_CONFIG


def searxng_search(query, agent_config):
    """
    Executes query on SearXNG and returns top results

    Args:
        query (str): The search query to be run
        agent_config (dict): The agent class instance's configuration values, including parameters for workers

    Returns:
        web_contexts (list): A list of dictionary objects of format {"name": "{name}", "url": "{url}", "context": "{page content}"}
    """

    num_search_results = agent_config["workers"]["searxng_search"]["num_search_results"]
    num_sites_scraped = agent_config["workers"]["searxng_search"]["num_sites_scraped"]
    max_scrape_tries = agent_config["workers"]["searxng_search"]["max_scrape_tries"]

    headers = agent_config["workers"]["searxng_search"]["search_headers"]
    url = f"{agent_config['workers']['searxng_search']['url']}{query}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    logging.debug(
        f"[*] WebSearchAgent.searxng_search: Web search returned status: {response.status_code}"
    )

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # BS4 scraping scripted for SearXNG in December 2025
    for i, result in enumerate(soup.find_all("article", class_="result"), start=1):
        if i > num_search_results:
            break

        h3_tag = result.find("h3")
        if not h3_tag:
            continue

        link_tag = h3_tag.find("a")
        if not link_tag:
            continue

        link = link_tag["href"]
        title = link_tag.get_text(strip=True)

        snippet_tag = result.find("p", class_="content")
        snippet = (
            snippet_tag.get_text(strip=True)
            if snippet_tag
            else "No description available"
        )

        results.append(
            {"id": i, "title": title, "link": link, "search_description": snippet}
        )

    # Call scrape_webpage to get `num_sites_scraped` page results, trying up to `max_scrape_tries` differnet pages.
    web_contexts = []
    for i in range(max_scrape_tries):
        site_url = results[i]["link"]
        try:
            site_context = _scrape_webpage(site_url, agent_config)
            if site_context is not None:
                web_contexts.append(
                    {
                        "name": results[i]["title"],
                        "url": site_url,
                        "context": site_context,
                    }
                )
                if len(web_contexts) >= num_sites_scraped:
                    break
        except Exception:
            continue
    if len(web_contexts) == 0:
        # No sites were successfully scraped
        return None
    return web_contexts


def _scrape_webpage(url, agent_config):
    """
    Get the plaintext contents of a webpage using trafilatura

    Args:
        url (str): The url to be scraped
        agent_config (dict): The agent class instance's configuration values, including parameters for workers

    Returns:
        contents (str): The plain text contents of the scraped website
    """
    trafilatura_config = deepcopy(TRF_CONFIG)
    trafilatura_config["DEFAULT"]["DOWNLOAD_TIMEOUT"] = agent_config["workers"][
        "scrape_webpage"
    ]["trafilatura_download_timeout"]
    trafilatura_config["DEFAULT"]["EXTRACTION_TIMEOUT"] = agent_config["workers"][
        "scrape_webpage"
    ]["trafilatura_extraction_timeout"]

    try:
        downloaded = fetch_url(url=url, config=trafilatura_config)
        contents = extract(
            downloaded,
            include_formatting=True,
            include_links=True,
            config=trafilatura_config,
        )
        logging.debug("[+] WebSearchAgent.scrape_webpage: returning webpage text")
        return contents
    except Exception:
        logging.debug(
            "[-] WebSearchAgent.scrape_webpage: failed to scrape webpage text"
        )
        return None
