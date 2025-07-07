# InkwellAi Crew

Welcome to the InkwellAi Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your 'OPENAI_API_KEY' into the '.env' file**

- Modify 'src/inkwell_ai/config/agents.yaml' to define your agents
- Modify 'src/inkwell_ai/config/tasks.yaml' to define your tasks
- Modify 'src/inkwell_ai/crew.py' to add your own logic, tools and specific args
- Modify 'src/inkwell_ai/main.py' to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the inkwell_ai Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will create a 'blog_post.md' file with content about AI LLMs in the root folder.

## Understanding Your Crew

The inkwell_ai Crew is composed of three AI agents working together to create blog content:

1. **Planner Agent**: Creates content plans and outlines for blog posts
2. **Writer Agent**: Writes engaging and factual content based on the plan
3. **Editor Agent**: Reviews and refines the content for quality and clarity

These agents collaborate on a series of tasks, defined in 'config/tasks.yaml', leveraging their collective skills to achieve complex objectives. The 'config/agents.yaml' file outlines the capabilities and configurations of each agent in your crew.

## Testing

The project includes comprehensive tests for agent and task configurations:

```bash
# Run tests directly
python tests/test_write_task.py

# Run tests with pytest
pytest tests/
```

## Development

For development, install additional dependencies:

```bash
pip install -r requirements-dev.txt
```

## Support

For support, questions, or feedback regarding the InkwellAi Crew:
- Email: ksatyam1038@gmail.com
- Website: [www.satyam.my](https://www.satyam.my)

Let's create wonders together with the power and simplicity of crewAI.
