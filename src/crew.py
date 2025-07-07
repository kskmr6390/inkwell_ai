from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from src.tools.custom_tool import DevToPostTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class InkwellAi():
    """
    InkwellAi crew for creating blog content.
    
    This crew consists of four agents:
    - Planner: Creates content plans and outlines
    - Writer: Writes engaging content based on the plan
    - Editor: Reviews and refines the content
    - Dev Poster: Publishes the final article to dev.to
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'], # type: ignore[index]
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            verbose=True
        )
    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config['editor'], # type: ignore[index]
            verbose=True
        )
    @agent
    def dev_poster(self) -> Agent:
        return Agent(
            config=self.agents_config['dev_poster'], # type: ignore[index]
            verbose=True,
            tools=[DevToPostTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['plan_task'], # type: ignore[index]
        )

    @task
    def writer_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_task'], # type: ignore[index]
            output_file='blog_post.md'
        )

    @task
    def editor_task(self) -> Task:
        return Task(
            config=self.tasks_config['edit_task'], # type: ignore[index]
            output_file='blog_post.md'
        )

    @task
    def post_to_dev_task(self) -> Task:
        return Task(
            config=self.tasks_config['post_to_dev_task'], # type: ignore[index]
            output_file='devto_post_result.md' 
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the InkwellAi crew for blog content creation.
        
        The crew executes tasks sequentially:
        1. Planner creates content outline
        2. Writer creates content based on outline
        3. Editor reviews and refines content
        4. Dev Poster publishes the article to dev.to
        
        Returns:
            Configured Crew instance
        """
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
