#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from github_analyzer.crew import GithubAnalyzer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'github_url': 'https://github.com/YJSong30/NexusAI',
        'target_dir': 'C:/Users/young/GitRepos/ai-agents/crew_ai/cloned_repo',
        'current_year': str(datetime.now().year)
    }
    
    try:
        GithubAnalyzer().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")