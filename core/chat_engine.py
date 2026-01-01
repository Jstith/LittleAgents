import logging
from pathlib import Path

import ollama
import yaml

from agents.websearch.agent import WebSearchAgent


class ChatEngine:
    """
    A class used to converse with an LM using agents

    Methods:
        __init__: loads the configuration YAML file to set preferences for the LM conversation
        process_message: passes user input through loaded agent(s) and modifies user prompt
        _generate_response: receives input from process_message, generates response from engine's LM, and returns it
    """

    def __init__(self, agents=None):
        """
        Constructor to set conversation preferences and active agents

        Args:
            agents (list, default=None): a list of agent python objects to be processed before a message is sent to the engine's LM.

        Config:
            chat_config.yaml: Configuration file that allows modification of all settings besides which agents to use
        """
        active_dir = Path(__file__).resolve().parent
        config_data_path = active_dir / "chat_config.yaml"
        with config_data_path.open("r") as f:
            self.chat_config = yaml.safe_load(f)

        self.host = self.chat_config["chat_engine"]["host"]
        self.model = self.chat_config["chat_engine"]["model"]
        self.system_message = self.chat_config["chat_engine"]["system_message"]

        self.agents = []
        if agents is not None:
            self.agents = agents

        self.conversation = [self.system_message]

        # Coded for WebSearch agent
        self.last_search_used = False
        self.last_search_urls = []

    def process_message(self, user_prompt):
        """
        Mutator function to modify user input with agents then process using the agent's LM

        Args:
            user_prompt (str): The user input to the LM

        Returns:
            _generate_response (func): The user input is passed to the LM and returns a generator of chunks
        """
        query = {"role": "user", "content": user_prompt}

        # Coded for WebSearch agent, if defaults then agent was not used
        self.last_search_used = False
        self.last_search_urls = []

        for agent in self.agents:
            if isinstance(agent, WebSearchAgent):
                result, revised_query, urls = agent.search(user_prompt)
                if result:
                    query["content"] = revised_query
                    self.last_search_used = True  # Set flag when search is used
                    self.last_search_urls = urls  # Store the source URL

        logging.info(f"[*] ChatEngine: Query is - {query}")
        self.conversation.append(query)
        return self._generate_response()

    def _generate_response(self):
        """
        Mutator function to generate a LM resposne to user input

        Returns:
            content (generator): A generator of chunks from the LM with the resposne to the user input
        """
        client = ollama.Client(self.host)
        response_stream = client.chat(
            model=self.model, messages=self.conversation, stream=True
        )
        complete_response = ""

        for chunk in response_stream:
            content = chunk["message"]["content"]
            complete_response += content
            yield content

        self.conversation.append({"role": "assistant", "content": complete_response})
