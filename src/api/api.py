from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from src.graph import smartshop_graph
from dotenv import load_dotenv





load_dotenv()
print("### NEW API.PY LOADED ###")



def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("SMARTSHOP_API_KEY")

    print("RECEIVED:", repr(x_api_key))
    print("EXPECTED:", repr(expected_key))

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


app = FastAPI(
    title="SmartShop AI API",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "SmartShop AI"
    }


@app.post("/chat")
def chat(
    request: ChatRequest,
    _: None = Depends(verify_api_key)
):
    try:
        result = smartshop_graph.invoke(
            {
                "user_request": request.message,
                "selected_agent": "",
                "response": ""
            }
        )

        return {
            "agent": result["selected_agent"],
            "response": result["response"]
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the request."
        )