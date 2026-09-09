import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# RAG imports
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

load_dotenv()

# 1. Initialize Embeddings and Vector Store (ChromaDB)
# We use a free, lightweight local embedding model from HuggingFace
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Let's load a sample document into ChromaDB if it doesn't exist yet
vector_store = Chroma(
    collection_name="sales_knowledge",
    embedding_function=embeddings,
    persist_directory="./vector_db",
)

# If database is empty, add our sample product data
# if vector_store._collection.count() == 0:
#     sample_doc = Document(
#         page_content="Our platform provides automated cloud compliance, SOC-2 certification, and saves teams 400 engineering hours on security audits.",
#         metadata={"source": "product_info.txt"},
#     )
#     vector_store.add_documents([sample_doc])

# If database is empty, load the real file from your knowledge folder
if vector_store._collection.count() == 0:
    file_path = "./knowledge/product_info.txt"

    # Verify the file actually exists where we expect it
    if os.path.exists(file_path):
        # Open and read the text file
        with open(file_path, "r", encoding="utf-8") as file:
            actual_content = file.read()

        # Create a document from your actual file's text
        real_doc = Document(
            page_content=actual_content, metadata={"source": "product_info.txt"}
        )

        # Add the real document to the database
        vector_store.add_documents([real_doc])
        print("Success: Loaded your custom text file into ChromaDB!")
    else:
        print(
            "Error: Could not find the product_info.txt file in the knowledge folder."
        )


# 2. Create a Custom Tool for RAG Retrieval
@tool
def search_internal_knowledge(query: str) -> str:
    """Search internal product features, pricing, and company documentation to answer technical questions."""
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "No internal documentation found."
    return "\n".join([doc.page_content for doc in results])


# 3. Combine Tools (Web Search + Internal RAG)
tavily_tool = TavilySearch(max_results=3, topic="general")
tools = [tavily_tool, search_internal_knowledge]

# 4. Initialize the LLM
llm = ChatGroq(model_name="openai/gpt-oss-20b", temperature=0.7)

# 5. System Prompt instructing the agent to use both tools
system_prompt = (
    "You are an expert enterprise Sales Executive. "
    "Use 'search_internal_knowledge' to find our product features, "
    "and use the web search tool to research the prospect's company news. "
    "Combine both to write a highly personalized, natural-sounding cold email. "
    "\n\nCRITICAL FORMATTING RULES:\n"
    "1. Write the email as plain text ready to be copy-pasted directly into Gmail or Outlook.\n"
    "2. NEVER use markdown tables, bolding (**), or hashtags.\n"
    "3. Use standard spacing and standard bullet points (-) if listing features.\n"
    "4. NEVER include a 'Sources' or 'References' section at the bottom. Keep the magic hidden."
)

agent_executor = create_react_agent(llm, tools, prompt=system_prompt)


# 6. Main execution function
def generate_sales_email(prospect_name: str, company: str):
    query = f"Research {prospect_name} at {company} and find recent news. Also check our internal product features to match them up, then write a cold email."
    result = agent_executor.invoke({"messages": [("user", query)]})
    return result["messages"][-1].content
