from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.auth.dependencies import get_current_active_user
from backend.database.models import User
from models.llm.model import ClinicalLLMModel

router = APIRouter(prefix="/chat", tags=["chat"])

# Instantiate the LLM model
llm = ClinicalLLMModel()

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
async def chat_with_copilot(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        if request.context:
            prompt = f"Context:\n{request.context}\n\nUser: {request.message}\nCopilot:"
        else:
            prompt = f"User: {request.message}\nCopilot:"
            
        reply = llm.predict(prompt)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
