from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from src.graph import smartshop_graph
from dotenv import load_dotenv
import os
import logging


load_dotenv()

# Application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("smartshop")


def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("SMARTSHOP_API_KEY")

    # Never print API keys
    if x_api_key != expected_key:
        logger.warning("Unauthorized API request")
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
        logger.info("USER QUESTION: %s", request.message)

        result = smartshop_graph.invoke(
            {
                "user_request": request.message,
                "selected_agents": [],
                "agent_results": [],
                "response": ""
            }
        )

        logger.info(
            "AGENTS USED: %s",
            result["selected_agents"]
        )

        logger.info(
            "SMARTSHOP RESPONSE: %s",
            result["response"]
        )

        return {
            "agents": result["selected_agents"],
            "response": result["response"]
        }

    except Exception as e:
        logger.exception("CHAT ERROR: %s", e)

        raise HTTPException(
            status_code=500,
            detail="Unable to process the request."
        )