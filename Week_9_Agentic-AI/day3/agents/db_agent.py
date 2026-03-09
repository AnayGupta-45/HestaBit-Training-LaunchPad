from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client
from tools.db_tools import run_query_tool


def build_db_agent():
    return AssistantAgent(
        name="DBAgent",
        model_client=get_model_client(),
        tools=[run_query_tool],
        system_message="""You are a database agent.
You query the Titanic SQLite database using SQL.
Table: titanic
Columns: PassengerId, Survived, Pclass, Name, Sex, Age, SibSp, Parch, Ticket, Fare, Cabin, Embarked
Always call run_query with a valid SELECT statement to answer the user's question."""
    )