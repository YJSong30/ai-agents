from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.clone_tool import git_clone_tool
from crewai_tools import DirectoryReadTool, SerperDevTool

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
    
    @agent
    def tech_stack_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['TechStackAnalyst'],
            verbose=True,
            tools=[DirectoryReadTool()]
        )

    @agent
    def security_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['SecurityAnalyst'],
            verbose=True,
            tools=[
                DirectoryReadTool(),
                SerperDevTool()
            ]
        )

    @task
    def clone_repo_task(self) -> Task:
        return Task(config=self.tasks_config['clone_repo_task'])

    @task
    def tech_stack_task(self) -> Task:
        return Task(config=self.tasks_config['tech_stack_task'])
    
    @task
    def security_analysis_task(self) -> Task:
        return Task(config=self.tasks_config['security_analysis_task'])

    @crew
    def crew(self) -> Crew:
        """Clones the repo crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )