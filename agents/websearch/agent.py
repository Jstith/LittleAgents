import logging
from pathlib import Path

import yaml

from .tools import *
from .workers import *


class WebSearchAgent:
    """
    Agentic class for performing web searches using SearXNG to add context to LM prompts.
    """

    agent_message = None  # System prompt for the "websearch" tool
    websearch_conversation = []  # Tracked conversation between user and agent
    agent_config = None  # tool/agent system prompts
    agent_mode = None  # Agent's operating mode

    def __init__(self, agent_mode="explicit"):
        """
        Constructor to load agent configuration and set operating mode

        Args:
            agent_mode (str): The selected mode for the agent (see below)

        Agent Modes:
            explicit: When a user query is passed to the agent, it will add context via web search. (default)
            conditional: When a user query is passed to the agent, it will evaluate if a web search is needed and decide whether to add context via web search or not.

        Config:
            agent_config.yaml: Configuration file that allows modification of all settings besides agent operating mode

        Returns:
            None
        """

        # Loads agent config and sets class config variables
        active_dir = Path(__file__).resolve().parent
        config_data_path = active_dir / "agent_config.yaml"
        with config_data_path.open("r") as f:
            self.agent_config = yaml.safe_load(f)

        self.name = self.agent_config["agent"]["name"]
        self.agent_mode = self.agent_config["agent"]["mode"]
        self.agent_message = self.agent_config["agent"]["agent_message"]
        logging.warning(f"[+] WebSearchAgent: Loaded agent in mode {self.agent_mode}.")

    def set_agent_mode(self, agent_mode):
        """
        Mutator function to change the mode of the agent

        Args:
            agent_mode (str): The operating mode of the agent

        Agent Modes:
            explicit: When a user query is passed to the agent, it will add context via web search. (default)
            conditional: When a user query is passed to the agent, it will evaluate if a web search is needed and decide whether to add context via web search or not.
        """

        if "explicit" in agent_mode.lower():
            self.agent_mode = "explicit"
            logging.warning('[+] WebSearchAgent: Set agent mode to "explicit"')
        elif "conditional" in agent_mode.lower():
            self.agent_mode = "conditional"
            logging.warning('[+] WebSearchAgent: Set agent mode to "conditional"')

    def search(self, user_prompt):
        """
        Invokes the websearch agent

        Args:
            user_prompt (str): The query to the LM that is being run through the search agent (usually the most recent input from the user)

        Returns:
            result (bool): Boolean expression stating whether the agent added context or not
            query (str): A new query string with the added web context
            urls (list): The list of URL the source used for context (empty list if no context added)
        """

        # If agent is in "conditional mode", perform agentic assessment to determine if a search is necessary with `tools.decide_to_search`
        if self.agent_mode == "conditional":
            logging.warning(f"[+] WebSearchAgent: Running decide_to_search tool")
            if not decide_to_search(user_prompt, self.agent_config):
                logging.warning(f"[+] WebSearchAgent: Exiting...")
                return (False, "", [])

        # Run the WebSearch agent
        logging.critical("[+] Running WebSearch agent...")

        # Generate search query
        logging.warning("[+] WebSearchAgent: Running query_generator tool")
        search_query = generate_query(user_prompt, self.agent_config)

        # Run search query, return content from top pages
        logging.warning("[+] WebSearchAgent Running searxng_search worker")
        web_contexts = searxng_search(search_query, self.agent_config)
        web_urls = []
        query = f"{self.agent_message}\n\n"
        for i, web_data in enumerate(web_contexts):
            web_urls.append(web_data["url"])
            query += f"SEARCH RESULT #{i + 1}:\n"
            query += f"NAME: {web_data['name']}\n"
            query += web_data["context"]
            query += "\n\n"
        query += f"USER PROMPT: {user_prompt}"
        logging.info(f"[*] WebSearchAgent: Query is - {query}")
        # Return new query with additional web context
        logging.warning(f"[+] WebSearchAgent: Exiting.")
        return True, query, web_urls


if __name__ == "__main__":
    """Local test of the WebSearch agent"""
    websearch_agent = WebSearchAgent(agent_mode="conditional")
    user_input = input("> User:\t")
    result, query, url = websearch_agent.search(user_input)
    if result:
        print("New User Query:")
        print(query)
        print(f"Source URL: {url}")
