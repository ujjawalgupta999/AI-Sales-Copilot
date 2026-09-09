import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import generate_sales_email

app = FastAPI(title="AI Sales Copilot API")

# Add this block to allow your React app to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the expected data format from the user
class ProspectRequest(BaseModel):
    prospect_name: str
    company: str


# Create a POST route to trigger the AI
@app.post("/generate-email")
def api_generate_email(request: ProspectRequest):
    # Run the LangGraph agent
    email_content = generate_sales_email(request.prospect_name, request.company)

    # Return the generated email as JSON
    return {
        "status": "success",
        "prospect": request.prospect_name,
        "email": email_content,
    }


# This keeps the server running when you execute `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
