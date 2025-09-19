#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from src.crew import InkwellAi

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Main entry point for the InkwellAi crew
# This file provides functions to run, train, replay, and test the crew
# with predefined inputs for blog content creation

def run(topic=None):
    """
    Run the crew to create blog content about a user-specified topic.
    Prompts the user for the blog topic and (optionally) the year.
    """
    from datetime import datetime
    topic = input("Enter the blog topic: ").strip()
    if not topic:
        print("Topic is required.")
        return
    year_input = input(f"Enter the year (default: {datetime.now().year}): ").strip()
    current_year = year_input if year_input else str(datetime.now().year)
    inputs = {
        'topic': topic,
        'current_year': current_year
    }
    try:
        InkwellAi().crew().kickoff(inputs=inputs)
    except Exception as e:
        # Handle OpenAI RateLimitError or similar
        if e.__class__.__name__ == "RateLimitError":
            print("Error: OpenAI API rate limit exceeded. Please wait and try again later, or check your OpenAI API usage limits.")
        else:
            print(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    Usage: python main.py train <iterations> <filename>
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        InkwellAi().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    Usage: python main.py replay <task_id>
    """
    try:
        InkwellAi().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    Usage: python main.py test <iterations> <eval_llm>
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        InkwellAi().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
