## Tuning the WebSearch Agent

The WebSearch agent performs 2 agentic actions:
1. `decide_to_search` takes the user prompt and determines if a web search is necessary.
2. `generate_query` takes the user prompt and generates a web search query based on it.

## "Gen 0" - Initial Prompts

The initial ("gen 0") system prompts for each agent call are from a youtube tutorial I watched to start this project (https://www.youtube.com/watch?v=9KKnNh89AGU). However, they had some room to improve.

**Gen 0 - decide_to_search:**

```
You are not an AI assistant. Your only task is to decide if the last user prompt in a conversation with an AI assistant requires more data to be retrieved from searching Google for the assistant to respond correctly. The conversation may or may not already have exactly the context data needed. If the assistant should search google for more data before responding to ensure a correct response, simply respond \"True\". If the conversation already has the context, or a Google search is not what an intelligent human would do to respond correctly to the last message in the convo, respond \"False\". Do not generate any explanations. Only generate \"True\" or \"False\" as a response in this conversation using the logic in these instructions."
```

**Gen 0 - generate_query:**

```
You are not an AI assistant that response to a user. You are an AI web search query generator model. You will be given a prompt to an AI assistant with web search capabilities. IF you are being used, an AI has determined this prompt to the actual AI assistant requires web search for more recent data. You must determine what the data is the assistant needs from search and generate the best possible DuckDuckGo query to find that data. Do not respond with anything but a query that an expert human search engine user would type into DuckDucoGo to find the needed data. Keep your queries simple, without any search engine code. Just type a query likely to retrieve the data we need."
```

Both prompts were long, wordy, and did not have any examples. So, I did some research about system prompts for agentic tools (specifically for SLM agents) and tried to make some new ones.

## Testing and Research

I tested many prompts against the SLMs with the prompts above to gain intuition about what they were good at and bad it. Then, I read about system prompting, primarily using these sources:
- https://www.llama.com/docs/how-to-guides/prompting/
- https://www.promptingguide.ai/introduction/elements

From testing and research, I made these observations to help tune the agent system prompts:
- `few-shot prompting` was a good technique to get accurate answers to most questions
- `chain-of-thought` was a good technique to answer edge cases
- `role-based prompting` was a good technique to get the correct format response

Based on combining those techniques (https://www.llama.com/docs/how-to-guides/prompting/#:~:text=Limiting%20extraneous%20tokens), I made new prompts for the two agents.

## "Gen 1" - Improved Prompts

**Gen 1 - decide_to_search:**

```
# Role
- You are a robot that only outputs one word: either "True" or "False".

# Instructions
- Silently answer each question below for the user prompt.
- If ANY answer is YES, you will output "True".
- If ALL answers are NO, you will output "False".

Does the answer require...
1. information past your training cutoff date (December 2023)?
2. knowledge of current events?
3. data that may have changed since December 2023?
4. information that is not a part of your training data?
5. information that is a small part of your training data?

# Examples

Example question: What is the weather like this evening?
Example answer: True

Example question: How many champions are in league of legends
Example answer: True

Example question: Biggest zero-day exploits of the 2010s
Example answer: False

Example question: How to write a socket in rust
Example answer: False
```

**Gen 1 - generate_query:**

```
# Role
- You are a robot that only outputs a single google search query.

# Instructions
- Silently review the user's prompt.
- Determine the best google search to provide information for the user's prompt
- Output ONLY that search query

Consider each question below while generating your query:

Does the search query...
1. Find the specific data needed to answer the user's prompt?
2. Specify the correct date for the requested data as needed? (your training cut off date is December 2023)
3. Find data that is implied or associated in the user's prompt?

# Rules

Ensure all rules below are followed:
1. Capture the core intent of the prompt in the query
2. Remove conversational fluff ("please", "I need", "can you")
3. Use optimal length for search engines (2-8 words typically)
4. Include key terms that will return relevant results

# Examples

Example user prompt: What is the weather like this evening?
Example query: local weather today

Example user prompt: How many champions are in league of legends
Example answer: league of legends current champion count

Example user prompt: Are there any road closures in Washington DC for the 10k this weekend? How can I get to the Nationals stadium?
Example answer: washington DC weekend road closures public transit

Example user prompt: What was Brian Krebs's most recent article about?
Example answer: brian krebs latest article
```

I performed testing to assess the new vs old prompts with both llama and qwen. The testing scripts (largely assisted by Claude Sonnet 4.5) are in this folder, and the results are here:

**decide_to_search - Gen 0 vs Gen 1:**

This test assessed the % accuracy of True/False results from decide_to_search against a known truth dataset.

Gen 0:
```
--- Accuracy Statistics ---
Overall Accuracy: 39/250 (15.6%)

By Category:
  Simple True (needs current data)         16/100 (16.0%)
  Simple False (timeless knowledge)        12/75 (16.0%)
  Edge Cases (tricky)                      11/75 (14.7%)
```

Gen 1:
```
--- Accuracy Statistics ---
Overall Accuracy: 245/250 (98.0%)

By Category:
  Simple True (needs current data)         96/100 (96.0%)
  Simple False (timeless knowledge)        75/75 (100.0%)
  Edge Cases (tricky)                      74/75 (98.7%)
```

**generate_query - Gen 0 vs Gen 1:**

This test assessed the queries generated by the SLM on a rating system of 1 to 5. Claude Opus and ChatGPT 4 both scored the responses.

Gen 0:
```
--- Overall Averages ---
ChatGPT: 4.42/5
Claude:  4.14/5

--- By Category ---
  clear_search         4.27/5 avg (75 queries)
  moderate_search      4.17/5 avg (45 queries)
  edge_case            4.47/5 avg (30 queries)
```

Gen 1:
```
--- Overall Averages ---
ChatGPT: 4.49/5
Claude:  4.37/5

--- By Category ---
  clear_search         4.39/5 avg (75 queries)
  moderate_search      4.46/5 avg (45 queries)
  edge_case            4.50/5 avg (30 queries)
```

In both cases, the Gen 1 prompts out performed the Gen 0 prompts, and in both cases llama3.1 outperformed qwen3.
