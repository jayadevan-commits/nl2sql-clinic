import os
from dotenv import load_dotenv

# ──  import paths as specified for Vanna AI  ────
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory

# ── LLM: Google Gemini -----------------
from vanna.integrations.google import GeminiLlmService

# ── Load .env  ───────────────────────
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")   # key name from PDF page 16
DB_PATH        = "clinic.db"

if not GOOGLE_API_KEY:
    raise ValueError(" GOOGLE_API_KEY not found. Add it to your .env file.")


# ── Component 1: LLM Service 
#  "Create an LLM Service using your chosen provider (GeminiLlmService)"
llm_service = GeminiLlmService(api_key=GOOGLE_API_KEY)


# ── Component 2: SQL Runner 
#  "Vanna provides a built-in SqliteRunner"
# # Fix: correct parameter is `database_path` not `db_path`
sql_runner = SqliteRunner(database_path=DB_PATH)


# ── Component 3: Tool Registry 
#  "Create a ToolRegistry and register:
#               RunSqlTool, VisualizeDataTool,
#               SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool"
tool_registry = ToolRegistry()
tool_registry.register_local_tool(RunSqlTool(sql_runner=sql_runner), access_groups=["users"])
tool_registry.register_local_tool(VisualizeDataTool(),               access_groups=["users"])
tool_registry.register_local_tool(SaveQuestionToolArgsTool(),        access_groups=["users"])
tool_registry.register_local_tool(SearchSavedCorrectToolUsesTool(),  access_groups=["users"])


# ── Component 4: Agent Memory ─────────────────────────────────────────────────
#  "Create a DemoAgentMemory instance (Vanna 2.0's learning system)"
agent_memory = DemoAgentMemory()


# ── Component 5: User Resolver ────────────────────────────────────────────────
#  "Create a UserResolver — a simple one that identifies
#               all users as a default user"
class DefaultUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="default_user", email="user@clinic.com", group_memberships=["users"])

user_resolver = DefaultUserResolver()


# ── Component 6: Create the Agent with all components connected ───────────────
#  "Create the Agent with all components connected"
def create_agent() -> Agent:
    agent = Agent(
        llm_service=llm_service,
        tool_registry=tool_registry,
        agent_memory=agent_memory,
        user_resolver=user_resolver,
        config=AgentConfig(),
    )
    return agent


# ── Quick test when run directly ──────────────────────────────────────────────
if __name__ == "__main__":
    agent = create_agent()
    print("✅ Vanna 2.0 Agent initialized successfully!")
    print(f"📁 Connected to database : {DB_PATH}")
    print(f"🤖 LLM Provider          : Google Gemini")
    print(f"🧠 Memory System         : DemoAgentMemory")