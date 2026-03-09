from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client
from tools.file_tools import FILE_TOOLS


def build_file_agent():
    return AssistantAgent(
        name="FileAgent",
        model_client=get_model_client(),
        tools=FILE_TOOLS,
        system_message="""You are a file agent.
You can inspect CSV files, read CSV files, and write text files.
- To inspect: call inspect_csv with just the filename e.g. 'titanic.csv'
- To read: call read_csv with just the filename e.g. 'titanic.csv'
- To write: call write_file with a filename and the content to write
Always use a tool — never guess file contents."""
    )