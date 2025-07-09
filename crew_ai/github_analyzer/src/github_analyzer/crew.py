from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.clone_tool import git_clone_tool

@CrewBase
class GithubAnalyzer():
    """GithubAnalyzer crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def repo_cloner(self) -> Agent:
        return Agent(
            config=self.agents_config['RepoCloner'],
            verbose=True,
            tools=[git_clone_tool]
        )

    @task
    def clone_repo_task(self) -> Task:
        return Task(config=self.tasks_config['clone_repo_task'])

    @crew
    def crew(self) -> Crew:
        """Clones the repo crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )