import logging

import ollama


def decide_to_search(user_prompt, agent_config):
    """
    Determines if a provided prompt needs additional context from a web search

    Args:
        user_prompt (str): The user prompt being assessed
        agent_config (dict): The agent class instance's configuration values, including tool system prompts

    Returns:
        web_search_needed (bool): A boolean determiantion if a web search is necessary for additional context
    """

    host = agent_config["tools"]["decide_to_search"]["host"]
    model = agent_config["tools"]["decide_to_search"]["model"]
    system_message = agent_config["tools"]["decide_to_search"]["system_message"]

    logging.info(
        "[+] WebSearchAgent.decide_to_search: Assessing query to determine if web search is necessary"
    )
    client = ollama.Client(host)
    response = client.chat(
        model=model, messages=[system_message, {"role": "user", "content": user_prompt}]
    )
    content = response["message"]["content"]
    web_search_needed = "true" in content.lower()

    logging.info(
        f"[+] WebSearchAgent.decide_to_search: Exiting tool with return value: {web_search_needed}"
    )
    return web_search_needed


def generate_query(user_prompt, agent_config):
    """
    Generates a web search query based on a user prompt

    Args:
        user_prompt (str): The user prompt being assessed
        agent_config (dict): The agent class instance's configuration values, including tool system prompts

    Returns:
        search_query (str): The generated search query
    """

    host = agent_config["tools"]["generate_query"]["host"]
    model = agent_config["tools"]["generate_query"]["model"]
    system_message = agent_config["tools"]["generate_query"]["system_message"]
    prompt = f"CREATE AN INTERNET SEARCH QUERY FOR THIS PROMPT: \n{user_prompt}"

    client = ollama.Client(host)
    response = client.chat(
        model=model, messages=[system_message, {"role": "user", "content": prompt}]
    )
    search_query = response["message"]["content"]
    search_query = search_query.replace('"', "")
    logging.info(
        f"[+] WebSearchAgent.generate_query: Returning with value: {search_query}"
    )
    return search_query
