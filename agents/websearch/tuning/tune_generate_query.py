import sys
from pathlib import Path
import yaml
import time
import statistics

# Add parent to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools import *

def print_gemini_prompt():
    """Print the prompt for Gemini to generate test cases"""
    print("\n" + "="*70)
    print("STEP 1: GENERATE TEST CASES WITH GEMINI")
    print("="*70)
    print("\nCopy the prompt below and paste into Google Gemini:\n")
    print("-"*70)
    
    prompt = """You are a test case generator for evaluating a web search agent. Generate exactly 50 diverse user questions that would benefit from or require web search to answer properly.

# Requirements

## Distribution (must follow exactly):
- 25 questions: Clearly require web search (current events, prices, weather, recent data)
- 15 questions: Moderately benefit from search (could use general knowledge OR current data)
- 10 questions: Edge cases (barely need search, but user might want fresh data)

## Length Distribution:
- 15 questions: Short (3-7 words) - e.g. "weather today", "stock price NVDA"
- 20 questions: Medium (8-15 words) - natural conversational questions
- 15 questions: Long (16-30+ words) - detailed, context-heavy questions

## Complexity Distribution:
- 15 questions: Simple/direct - single fact lookups
- 20 questions: Moderate - require some analysis or comparison
- 15 questions: Complex - multi-part, need synthesis from multiple sources

## Style Variety (mix throughout):
- Casual/colloquial ("what's up with...", "any idea if...")
- Formal/professional ("Please provide...", "I require information on...")
- Incomplete/fragmented ("best laptop 2024?", "restaurants nearby good?")
- Question format ("Who won...", "When does...", "Is it true that...")
- Command format ("Find me...", "Show me...", "Tell me about...")
- Implicit questions ("I need to know...", "Looking for...")

## Topic Variety (ensure coverage):
- Current events & news (politics, disasters, announcements)
- Stock prices, crypto, financial data
- Weather & local conditions
- Sports scores & schedules
- Product releases & tech news
- Entertainment (movies, music, TV)
- Health/medical updates (variants, recalls, studies)
- Business (company status, CEO changes, acquisitions)
- Science & research breakthroughs
- Local information (restaurants, events, services)
- Pricing & availability
- Government & policy changes
- Pop culture & trends

# Output Format

Return ONLY a Python list of tuples. No explanations, no preamble. Format:

[
    ("question text here", "category"),
    ...
]

Categories: "clear_search", "moderate_search", "edge_case"

# Example (DO NOT COPY THESE):
[
    ("What's the weather in Seattle right now?", "clear_search"),
    ("Best practices for prompt engineering with small language models", "moderate_search"),
    ("How many countries are in the UN?", "edge_case")
]

NOW GENERATE 50 QUESTIONS. Ensure variety in every dimension. Start your response with the opening bracket ["""
    
    print(prompt)
    print("-"*70)

def get_test_cases():
    """Get test cases from user input"""
    print("\n" + "="*70)
    print("PASTE GEMINI OUTPUT BELOW")
    print("="*70)
    print("Paste the list of tuples from Gemini, then press Enter twice:\n")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "" and lines:
            break
        lines.append(line)
    
    # Join and evaluate
    test_cases_str = "\n".join(lines)
    test_cases = eval(test_cases_str)
    
    print(f"\n✓ Loaded {len(test_cases)} test cases")
    return test_cases

def run_query_generation(test_cases, agent_config, epochs=3):
    """Run query generation for all test cases across epochs"""
    print("\n" + "="*70)
    print(f"STEP 2: GENERATING QUERIES ({epochs} EPOCHS)")
    print("="*70)
    
    all_epoch_data = []
    all_times = []
    
    for epoch_num in range(epochs):
        print(f"\n[Epoch {epoch_num}]")
        epoch_data = []
        times = []
        
        for i, (question, category) in enumerate(test_cases):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(test_cases)}")
            
            start_time = time.time()
            generated_query = generate_query(question, agent_config)
            end_time = time.time()
            
            times.append(end_time - start_time)
            epoch_data.append({
                'question': question,
                'query': generated_query,
                'category': category,
                'length': len(question.split()),
                'query_length': len(generated_query.split())
            })
        
        all_epoch_data.append(epoch_data)
        all_times.append(times)
        print(f"  ✓ Epoch {epoch_num} complete: {statistics.mean(times):.3f}s avg")
    
    return all_epoch_data, all_times

def print_judge_prompt(epoch_data, epoch_num):
    """Print evaluation prompt for one epoch"""
    print("\n" + "="*70)
    print(f"STEP 3: EVALUATE EPOCH {epoch_num}")
    print("="*70)
    print("\nCopy the prompt below and paste into ChatGPT or Claude:\n")
    print("-"*70)
    
    prompt = """You are evaluating search query quality for a web search agent. You will receive pairs of:
1. Original user question
2. Generated search query

Rate each generated query on a scale of 1-5 based on these criteria:

**Scoring Rubric:**

5 - Excellent
- Captures core intent perfectly
- Removes conversational fluff ("please", "I need", "can you")
- Optimal length for search engines (2-8 words typically)
- Includes key terms that will return relevant results
- Uses search operators appropriately (quotes, OR, site:) when helpful

4 - Good
- Captures main intent well
- Minor unnecessary words remain
- Slightly too long or too short, but workable
- Would return good results with minor noise

3 - Adequate
- Gets the general idea
- Contains some fluff or awkward phrasing
- Missing some key terms OR includes too many irrelevant terms
- Would return mixed results

2 - Poor
- Misses important aspects of the question
- Too verbose or too vague
- Would return many irrelevant results
- Key search terms missing

1 - Very Poor
- Fundamentally misunderstands the question
- Would return wrong results entirely
- Unusable as a search query

**Output Format:**

For each question/query pair, respond with ONLY:
```
Q[number]: [score]/5
```

Example:
```
Q1: 5/5
Q2: 3/5
Q3: 4/5
```

**Important:**
- Be strict but fair
- Focus on search effectiveness, not grammar
- Shorter is often better for search queries
- Consider if the query would actually return useful results
- Do NOT provide explanations, ONLY scores

---

**Input Data:**

"""
    
    for i, item in enumerate(epoch_data, 1):
        prompt += f"\nQ{i}: {item['question']}\n"
        prompt += f"Generated: {item['query']}\n"
    
    prompt += "\n---\n\nBEGIN EVALUATION:\n"
    
    print(prompt)
    print("-"*70)

def get_judge_scores(num_questions):
    """Get scores from user input"""
    print(f"\nPaste the judge's scores (Q1: X/5 format), then press Enter twice:\n")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "" and lines:
            break
        lines.append(line)
    
    # Parse scores
    scores = []
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        # Extract number after colon
        try:
            score_part = line.split(':')[1].strip()
            score = int(score_part.split('/')[0])
            scores.append(score)
        except:
            continue
    
    if len(scores) != num_questions:
        print(f"⚠ Warning: Got {len(scores)} scores, expected {num_questions}")
    
    return scores

def print_results(all_epoch_data, all_times, chatgpt_scores, claude_scores, test_cases):
    """Print comprehensive results"""
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    # Timing statistics
    print("\n--- Timing Statistics ---")
    flat_times = [t for epoch_times in all_times for t in epoch_times]
    print(f"Mean:   {statistics.mean(flat_times):.3f}s")
    print(f"Median: {statistics.median(flat_times):.3f}s")
    print(f"Std:    {statistics.stdev(flat_times):.3f}s")
    print(f"Min:    {min(flat_times):.3f}s")
    print(f"Max:    {max(flat_times):.3f}s")
    
    # Judge comparison
    print("\n--- Judge Scores ---")
    epochs = len(all_epoch_data)
    
    for epoch_num in range(epochs):
        epoch_chatgpt = chatgpt_scores[epoch_num]
        epoch_claude = claude_scores[epoch_num]
        
        print(f"\nEpoch {epoch_num}:")
        print(f"  ChatGPT: {statistics.mean(epoch_chatgpt):.2f}/5 avg (±{statistics.stdev(epoch_chatgpt):.2f})")
        print(f"  Claude:  {statistics.mean(epoch_claude):.2f}/5 avg (±{statistics.stdev(epoch_claude):.2f})")
        
        # Agreement
        agreement = sum(1 for c, cl in zip(epoch_chatgpt, epoch_claude) if c == cl)
        print(f"  Agreement: {agreement}/{len(epoch_chatgpt)} ({100*agreement/len(epoch_chatgpt):.1f}%)")
    
    # Overall averages
    print("\n--- Overall Averages ---")
    all_chatgpt = [s for epoch in chatgpt_scores for s in epoch]
    all_claude = [s for epoch in claude_scores for s in epoch]
    
    print(f"ChatGPT: {statistics.mean(all_chatgpt):.2f}/5")
    print(f"Claude:  {statistics.mean(all_claude):.2f}/5")
    
    # Category breakdown
    print("\n--- By Category ---")
    categories = {"clear_search": [], "moderate_search": [], "edge_case": []}
    
    for epoch_data, chatgpt_epoch, claude_epoch in zip(all_epoch_data, chatgpt_scores, claude_scores):
        for item, cg_score, cl_score in zip(epoch_data, chatgpt_epoch, claude_epoch):
            cat = item['category']
            avg_score = (cg_score + cl_score) / 2
            categories[cat].append(avg_score)
    
    for cat_name, scores in categories.items():
        print(f"  {cat_name:20} {statistics.mean(scores):.2f}/5 avg ({len(scores)} queries)")
    
    # Query length analysis
    print("\n--- Query Statistics ---")
    all_queries = [item for epoch in all_epoch_data for item in epoch]
    query_lengths = [item['query_length'] for item in all_queries]
    print(f"Mean query length: {statistics.mean(query_lengths):.1f} words")
    print(f"Median: {statistics.median(query_lengths):.1f}, Std: {statistics.stdev(query_lengths):.1f}")
    
    # Consistency across epochs
    print("\n--- Consistency ---")
    if epochs > 1:
        consistent = 0
        for q_idx in range(len(test_cases)):
            queries = [all_epoch_data[e][q_idx]['query'] for e in range(epochs)]
            if len(set(queries)) == 1:
                consistent += 1
        print(f"Identical queries across epochs: {consistent}/{len(test_cases)} ({100*consistent/len(test_cases):.1f}%)")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    
    # Load agent config
    active_dir = Path(__file__).resolve().parent
    config_data_path = active_dir / "agent_config_tuning.yaml"
    with config_data_path.open('r') as f:
        agent_config = yaml.safe_load(f)
    
    # Step 1: Get test cases from Gemini
    print_gemini_prompt()
    test_cases = get_test_cases()
    
    # Step 2: Generate queries
    EPOCHS = 3
    all_epoch_data, all_times = run_query_generation(test_cases, agent_config, EPOCHS)
    
    # Step 3: Get evaluations from judges
    chatgpt_scores = []
    claude_scores = []
    
    for epoch_num in range(EPOCHS):
        # ChatGPT evaluation
        print_judge_prompt(all_epoch_data[epoch_num], epoch_num)
        print("\n[Waiting for ChatGPT scores...]")
        chatgpt_epoch_scores = get_judge_scores(len(test_cases))
        chatgpt_scores.append(chatgpt_epoch_scores)
        
        # Claude evaluation
        print("\nNow paste the SAME prompt into Claude and enter scores:\n")
        print("[Waiting for Claude scores...]")
        claude_epoch_scores = get_judge_scores(len(test_cases))
        claude_scores.append(claude_epoch_scores)
    
    # Step 4: Print results
    print_results(all_epoch_data, all_times, chatgpt_scores, claude_scores, test_cases)



"""
Gen 0 Prompt:

You are not an AI assistant that response to a user. You are an AI web search query generator model. You will be given a prompt to an AI assistant with web search capabilities. IF you are being used, an AI has determined this prompt to the actual AI assistant requires web search for more recent data. You must determine what the data is the assistant needs from search and generate the best possible DuckDuckGo query to find that data. Do not respond with anything but a query that an expert human search engine user would type into DuckDucoGo to find the needed data. Keep your queries simple, without any search engine code. Just type a query likely to retrieve the data we need."

Gen 1 Prompt:

# Role
- You are a robot that only outputs a single google search query.

# Instructions
- Silently review the user's prompt.
- Determine the best google search to provide information for the user's prompt 
- Output ONLY that search query

Consider each question below while generating your query:

Does the search query...
1. Provide the data needed to answer the user's prompt?
2. Need to specify recent data past your training cut off date (December 2023)?
3. Contain implied or associated data to fully answer the user's prompt?

# Rules

Ensure all rules below are followed:
1. Capture the core intent of the prompt in the query
2. Remove converstaional fluff ("please", "I need", "can you")
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
"""