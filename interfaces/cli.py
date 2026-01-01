from agents.websearch.agent import WebSearchAgent
from core.chat_engine import ChatEngine


def setup_agents():
    """Helper function to set up agents, manually updated with new agent instantiation"""
    agents = []

    # Load WebSearchAgent and set operating mode
    launch_websearch = input("[>] Launch WebSearchAgent? (Y/n): ")
    if "n" not in launch_websearch:
        agents.append(WebSearchAgent())
        websearch_mode = input("[>] Set WebSearchAgent mode to 'conditional'> (Y/n): ")
        if "n" not in websearch_mode:
            agents[0].set_agent_mode("conditional")
    return agents


def main():
    """Looped function handles user I/O with the model until program exit"""
    agents = setup_agents()
    if len(agents) > 0:
        engine = ChatEngine(agents)
    else:
        engine = ChatEngine()

    while True:
        user_prompt = input("[>] User: ")
        if user_prompt.lower().strip() == "exit":
            return

        for i, chunk in enumerate(engine.process_message(user_prompt)):
            if i == 0:
                print("\n[#] Assistant: ", end="")
            print(chunk, end="", flush=True)

        # If web search agent is in use, print used URLs
        if engine.last_search_used and len(engine.last_search_urls) > 0:
            print("\n\n[#] Web search context from:")
            for i, url in enumerate(engine.last_search_urls):
                print(f"[{i + 1}] - {url}")
        print("\n")
