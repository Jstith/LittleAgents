# Little Agents

A python and ollama tool for performing agentic search using Small Language Models (SLMs).


**Background:**
The single most useful thing language models (LMs) do for me is search the internet and summarize results really well. During my holiday break, I was playing around with [SearXNG](https://docs.searxng.org/) to explore private web search. Once I got the server set up, I wanted to do more. In a self-hosted frenzy, I ~~googled~~ SearXNG'd local LLM search platforms. But, after trying a few, I decided I wanted to build my own to learn more about agents and see how good I could make a local model performing web search.

## Install

This project requires `python3` and `ollama`, as well as a computer capable of running ~ 5BG worth of AI models from ollama. The inference is pretty light in this project, so CPU will do the trick (just slower than a dedicated GPU).

1. Download ollama from: https://ollama.com/download
2. Download the ollama models you wish to use (defaults are `llama3.1:8b` and `qwen3:8b`)

```
ollama pull llama3.1:8b
ollama pull qwen3:8b
```

3. Clone the project

```
git clone https://github.com/Jstith/LittleAgents.git
cd LittleAgents
```

4. Install the python dependencies (a venv is recommended but not required obv.)

Optional:
```
python3 -m venv venv
source venv/bin/activate
```

Required:
```
pip install -r requirements.txt
```

5. Set the configuration files

Change both `agent_config.default` and `chat_engine.default` to `.yaml` files and modify and defaults you wish to change. At a minimum, you will need to enter a valid URL for SearXNG in WebSearch's `agent_config.yaml`. I recommend self hosting an instance, but there are numerous public instances you can try, too. They can be found here: https://searx.space/ (of course, be mindful of the data you're sending over a public and untrusted server).

6. Run the program

Run the program with python.
```
python3 run.py [-vvv]
```
Note: for debugging or better understanding how the program works, verbose flags `-v`, `-vv`, or `-vvv` will give more and more status output about the program as it runs.

## Structure

Organization:
```
LittleAgents/
├── run.py
├── agents/
│   └── websearch/
│       ├── agent.py
│       ├── tools.py
│       ├── workers.py
│       ├── agent_config.yaml
│       └── tuning/
│           ├── readme.md
│           └── {various tuning scripts & data} 
├── core/
│   ├── chat_engine.py
│   └── chat_config.yaml
└── interfaces/
    └── cli.py
```

Python scrpits:
- **run.py:** Program entry point
- **core/chat_engine.py:** Runs the back-and-forth conversation with the underlying SLM
- **interfaces/cli.py**: Runs a bare bones loop for user CLI input / output with  `chat_engine`.
- **agents/**: contains modular agents written for the SLM (initially, just `websearch`)
- **agents/websearch/**
	- **agent.py**: Contains the core logic for the agent, including the class and run function(s)
	- **tools.py**: Contain functions and variables for LM actions
	- **workers.py**: Contain functions and variables for non-LM actions

### Entry: `run.py`

The entry script has a very small set of responsibilities, as most of the program logic is handled elsewhere. The entry script is responsible for:

1. Loading global program arguments
2. Calling the appropriate interface command to start a conversation

In the future, this can be used to switch between GUI and CLI mode if I (or you <3) adds a GUI in interfaces/*.py

### Interfaces: `cli.py`

The interfaces scripts handle the user interaction for the program, taking in user prompts and sending them to the chat engine to process. Interface scripts are responsible for:

1. Determining which agents will be available in a session
2. Determining which agents will be used in a single query
3. Receiving queries from the user and passing them to the chat engine
4. Receiving responses from the chat engine and printing them to the user

Currently, I do not have a GUI in python, but I've successfully used [ttyd](https://github.com/tsl0922/ttyd) to host in a browser.

### Chat Engine: `core/chat_engine.py`

This script contains the `ChatEngine` class, which carries out the back-and-forth interaction with the core SLM. In an infinite loop, the chat engine does the following:

1. Receives a query from an interfaces script
2. Modifies the input with agents
3. Sends the query to the SLM
4. Receives a response from the SLM
5. Updates list of conversation in memory
6. Sends response to interface script

### Agents: `agents/`

The `agents` directory contains the heart and soul of this tool: modular agentic AI programs. The first agent I designed this tool for was web search. While each agent will have different code and needs, they should all follow a general model:

- **agent.py** contains a class for the agent which can be instantiated and used in the chat engine. All programmable variables for the agent must be writable in the constructor and through mutator functions. Finally, the main call method to invoke the agent must be in this file.
- **tools.py** contains all functions utilized by the agent that contain LLM calls. Parameters for the SLM call, such as the model and system prompt, must be stored in an environment file that can be modified for tuning. 
- **workers.py** contains all functions utilized by the agent that do not contain SLM calls. While parameters for these functions should also be stored in an environment file as necessary, these calls tend to be standard python functions that don't always need much parameterization.
- **agent_config.yaml** contains all of the editable parameters for the agent, including system prompts for agentic tools, models to use for agent and tool calls, and other things that can be tuned or changed. Once loaded in the class, the agent config should be passed to all worker and tool functions, ensuring that all tuning for the agent can be done by modifying a single yaml file.

## Design Decisions

I made several decisions while making this tool that impact how it functions. Here are some of the major decisions I made and the justification behind them:

### 0. I am learning as I go

I started this project with no idea how to code an AI agent and no idea how capable or incapable 8B open models are. I changed a lot of things as I went, and I'm sure a lot of this is still inefficient. But, it's a learning project :)

### 1. Model Size & Choice

I wanted to see how good of a web search-informed LM I could make using small language models (SMLs) that can run on my computer "normally". I did all of the development for this on an TX-3070 with 8bg VRAM, and inference runs decently fast on standard DDR4/5 RAM. Obviously, this tool would work MUCH better with larger models, such as `gpt-oss:20b`. However, I decided to stay small and see how good I could make it. I tested and tuned with both `qwen3:8b` and `llama3.1:8b` (see the `agents/websearch/tuning` folder) and settled with `llama3.1:8b` for the agentic functions and `qwen3:8b` for the main SLM the user converses with.

Note: `llama3.1:8b` is considerably faster for the conversational SLM, but `qwen3:8b` gives higher quality results and handles the system prompt better.

### 2. No SLM Tool Calling

The standard way to integrate agentic tools to LLMs is to provide the LM with awareness of the tool, including the technique to "call it", in the system prompt for the LM. Then, the LM processes an input, decides a tool call is necessary, and spits out a formatted call to some program which will take the input and do something with it. Once that extra context is returned, the LM takes the entire stack of information and generates a response (for a much better explanation, see here: https://platform.openai.com/docs/guides/function-calling).

However, through my testing and research I discovered that the 8B models struggle to do both tool calling and accurate responses. They can do either one decently. Regarding their `llama:3.1` model, Meta says:

```
Note: We recommend using Llama 70B-instruct or Llama 405B-instruct for applications that combine conversation and tool calling. Llama 8B-Instruct can not reliably maintain a conversation alongside tool calling definitions. It can be used for zero-shot tool calling, but tool instructions should be removed for regular conversations between the model and the user.
```
(https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/)

So, to give the conversational SLMs a fighting chance, I choose to remove the tool calling from the hands of the SLM and integrate it logically instead. When the user starts a conversation, they specify what agent(s) they would like to use. If they choose an agent, it is automatically loaded in.

**Giving the Agent... agency**

In order to not force the WebSearch agent to search the web every query, I introduced agent `operating modes`, which dictate how often the agent should be activated. For the WebSearch agent, it can operate in one of two modes:
- `explicit` performs a web search to add context to every user query
- `conditional` performs a separate agentic assessment on every user query to determine if a web search is necessary or not.

The conversation flow for an `explicit` WebSearch agent looks like this:
```
┌─────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────┐
│ cli.py  │         │ ChatEngine  │         │ WebSearch   │         │ SLM │
└────┬────┘         └──────┬──────┘         │   Agent     │         └──┬──┘
     │                     │                └──────┬──────┘            │
     │  1. user input      │                       │                   │
     │────────────────────>│                       │                   │
     │                     │                       │                   │
     │                     │  2. iterate agents    │                   │
     │                     │──────────────────────>│                   │
     │                     │                       │                   │
     │                     │  3. search results    │                   │
     │                     │<──────────────────────│                   │
     │                     │                       │                   │
     │                     │  4. modified prompt                       │
     │                     │──────────────────────────────────────────>│
     │                     │                                           │
     │                     │  4. response chunks                       │
     │                     │<──────────────────────────────────────────│
     │                     │                       │                   │
     │  5. stream chunks   │                       │                   │
     │<────────────────────│                       │                   │
     │                     │                       │                   │
     ▼                     ▼                      ▼                   ▼
```

The conversation flow for a `conditional` WebSearch agent looks like this:
```
┌─────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────┐
│ cli.py  │         │ ChatEngine  │         │ WebSearch   │         │ SLM │
└────┬────┘         └──────┬──────┘         │   Agent     │         └──┬──┘
     │                     │                └──────┬──────┘            │
     │  1. user input      │                       │                   │
     │────────────────────>│                       │                   │
     │                     │                       │                   │
     │                     │  2. iterate agents    │                   │
     │                     │──────────────────────>│                   │
     │                     │                       │                   │
     │                     │                       │  3. need search?  │
     │                     │                       │──────────────────>│
     │                     │                       │                   │
     │                     │                       │  3. yes/no        │
     │                     │                       │<──────────────────│
     │                     │                       │                   │
     │                     │                       │  [if yes: search] │
     │                     │                       │                   │
     │                     │  4. search results    │                   │
     │                     │<──────────────────────│                   │
     │                     │                       │                   │
     │                     │  5. modified prompt                       │
     │                     │──────────────────────────────────────────>│
     │                     │                                           │
     │                     │  5. response chunks                       │
     │                     │<──────────────────────────────────────────│
     │                     │                       │                   │
     │  6. stream chunks   │                       │                   │
     │<────────────────────│                       │                   │
     │                     │                       │                   │
     ▼                     ▼                      ▼                   ▼
```

### 3. Agentic System Prompting

My initial system prompts for the agents were from a youtube tutorial I followed to start this project (https://www.youtube.com/watch?v=9KKnNh89AGU). It's a great tutorial, but there were some serious issues with the system prompts. So, I read about system prompting and tested new prompts. I have more details on that in the `agents/websearch/tuning` folder.

**Giving agentic context to the conversational SML:**

When an agent is run, the agent is responsible for adding the both the agent's context and the situational awareness of the agent to the user prompt sent to the conversational SLM. This is a different technique than many agentic tools, where the system prompt for the conversational LM is loaded with tool context instead. Since the conversational LM does not need to call the tool itself, it saves context and complexity in that LM's system prompt to leave the tool context in the user prompt (https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/#:~:text=Notes,-With).
