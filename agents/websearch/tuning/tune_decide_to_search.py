from pathlib import Path
import yaml
import time
import statistics
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools import *

test_cases = [
    # Clear True cases - needs current/recent data
    ("What's the weather today?", "True"),
    ("Who won the Super Bowl this year?", "True"),
    ("Current price of Bitcoin", "True"),
    ("Is the government shutdown still happening?", "True"),
    ("Latest iPhone release date", "True"),
    ("Stock price of NVIDIA", "True"),
    ("Who is the current president of France?", "True"),
    ("What time does the sun set tonight?", "True"),
    ("Are there any recalls on 2024 Tesla Model 3?", "True"),
    ("How many people live in Tokyo right now?", "True"),
    ("What's trending on Twitter today?", "True"),
    ("Did NASA launch anything this week?", "True"),
    ("Current mortgage rates", "True"),
    ("Is ChatGPT down right now?", "True"),
    ("What movies are in theaters?", "True"),
    ("Who won the NBA finals?", "True"),
    ("Latest COVID variant information", "True"),
    ("Current gas prices near me", "True"),
    ("Is Amazon having a sale today?", "True"),
    ("What's the score of the game?", "True"),
    
    # Clear False cases - general knowledge from training
    ("How do I make chocolate chip cookies?", "False"),
    ("Explain quantum entanglement", "False"),
    ("What is the capital of France?", "False"),
    ("How to write a binary search algorithm", "False"),
    ("What causes rainbows?", "False"),
    ("Translate 'hello' to Spanish", "False"),
    ("Explain photosynthesis", "False"),
    ("What is the Pythagorean theorem?", "False"),
    ("How do volcanoes form?", "False"),
    ("What are the symptoms of the flu?", "False"),
    ("Explain how a car engine works", "False"),
    ("What is Object Oriented Programming?", "False"),
    ("How to tie a bowline knot", "False"),
    ("What is the water cycle?", "False"),
    ("Explain Newton's three laws of motion", "False"),
    
    # Edge cases - tricky ones
    ("How many Pokemon are there?", "True"),  # Number changed after 2023
    ("What happened on D-Day?", "False"),  # Historical fact
    ("Best practices for React hooks", "False"),  # Tech concept from training
    ("Is Elon Musk still CEO of Twitter?", "True"),  # Changed to X, status could change
    ("How to center a div in CSS", "False"),  # Timeless web dev
    ("What are the planets in our solar system?", "False"),  # Unchanging fact
    ("Rust vs Go performance comparison", "False"),  # General tech knowledge
    ("When did World War 2 end?", "False"),  # Historical
    ("Latest Rust language features", "True"),  # Language evolves
    ("How does TCP/IP work?", "False"),  # Fundamental networking
    ("Is GitHub Copilot free?", "True"),  # Pricing could change
    ("Explain the SOLID principles", "False"),  # Software design fundamentals
    ("What is the tallest building in the world?", "True"),  # Could change
    ("How to reverse a linked list", "False"),  # Classic algorithm
    ("Current state of quantum computing", "True"),  # Rapidly evolving field
]

def epoch(n, agent_config):
    results = []
    times = []
    for i, test_case in enumerate(test_cases):
        
        print(f"[+] Epoch {n}, testing use case #{i}")
        user_prompt = test_case[0]
        correct_result = bool(test_case[1])

        start_time = time.time()
        result = decide_to_search(user_prompt, agent_config)
        end_time = time.time()
        times.append(end_time - start_time)
        if result == correct_result:
            results.append(1)
        else:
            results.append(0)
        
    return results, times

if __name__ == '__main__':

    # Load agent config
    active_dir = Path(__file__).resolve().parent
    config_data_path = active_dir / "agent_config_tuning.yaml"
    with config_data_path.open('r') as f:
        agent_config = yaml.safe_load(f)

    # Test-specific changes to agent config
    # agent_config["tools"]["decide_to_search"]["model"] = "llama3.1:8b"

    all_results = []
    all_times = []

    for n in range(5):
        results, times = epoch(n, agent_config)
        all_results.append(results)
        all_times.append(times)

    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)

    # Timing statistics
    print("\n--- Timing Statistics ---")
    flat_times = [t for epoch_times in all_times for t in epoch_times]
    print(f"Mean:   {statistics.mean(flat_times):.3f}s")
    print(f"Median: {statistics.median(flat_times):.3f}s")
    print(f"Std:    {statistics.stdev(flat_times):.3f}s")
    print(f"Min:    {min(flat_times):.3f}s")
    print(f"Max:    {max(flat_times):.3f}s")

    # Per-epoch timing
    print("\nPer-Epoch Timing:")
    for i, epoch_times in enumerate(all_times):
        print(f"  Epoch {i}: {statistics.mean(epoch_times):.3f}s avg")

    # Accuracy statistics
    print("\n--- Accuracy Statistics ---")
    flat_results = [r for epoch_results in all_results for r in epoch_results]
    total_correct = sum(flat_results)
    total_tests = len(flat_results)
    print(f"Overall Accuracy: {total_correct}/{total_tests} ({100*total_correct/total_tests:.1f}%)")

    # Category breakdown (using your test case structure)
    print("\nBy Category:")
    categories = [
        ("Simple True (needs current data)", 0, 20),
        ("Simple False (timeless knowledge)", 20, 35),
        ("Edge Cases (tricky)", 35, 50)
    ]

    for cat_name, start, end in categories:
        cat_results = [r for epoch_results in all_results for r in epoch_results[start:end]]
        cat_correct = sum(cat_results)
        cat_total = len(cat_results)
        print(f"  {cat_name:40} {cat_correct}/{cat_total} ({100*cat_correct/cat_total:.1f}%)")

    # Per-epoch accuracy
    print("\nPer-Epoch Accuracy:")
    for i, epoch_results in enumerate(all_results):
        correct = sum(epoch_results)
        total = len(epoch_results)
        print(f"  Epoch {i}: {correct}/{total} ({100*correct/total:.1f}%)")

    # Consistency check
    print("\n--- Consistency ---")
    if len(all_results) > 1:
        # Check how many test cases got same result across all epochs
        consistent = 0
        for test_idx in range(len(all_results[0])):
            test_results = [epoch[test_idx] for epoch in all_results]
            if len(set(test_results)) == 1:  # All same
                consistent += 1
        print(f"Consistent across epochs: {consistent}/{len(all_results[0])} ({100*consistent/len(all_results[0]):.1f}%)")

    print("="*60 + "\n")


"""
Gen 0 prompt:

You are not an AI assistant. Your only task is to decide if the last user prompt in a conversation with an AI assistant requires more data to be retrieved from searching Google for the assistant to respond correctly. The conversation may or may not already have exactly the context data needed. If the assistant should search google for more data before responding to ensure a correct response, simply respond \"True\". If the conversation already has the context, or a Google search is not what an intelligent human would do to respond correctly to the last message in the convo, respond \"False\". Do not generate any explanations. Only generate \"True\" or \"False\" as a response in this conversation using the logic in these instructions."

Gen 1 prompt:

# Role
- You are a robot that only outputs one word: either "True" or "False".

# Instructions
- Silently answer each question below for the user's prompt.
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
"""