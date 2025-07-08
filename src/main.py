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
    If topic is not provided, prompts the user for a topic (or uses a default).
    This will execute the planner, writer, and editor tasks sequentially.
    """
    try:
        if not topic:
            # Prompt the user to enter a blog topic (example: AI in Healthcare)
            topic = input("Enter the blog topic (default: 'Agentic AI in healthcare'): ").strip()
            if not topic:
                topic = "Agentic AI in healthcare"
        inputs = {
            'topic': topic,
            'current_year': str(datetime.now().year)
        }
        InkwellAi().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


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
