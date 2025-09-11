from fastapi import FastAPI
from pydantic import BaseModel
from app.rag import RagPipeline
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Crypto RAG Copilot", version="0.1.0")
rag = RagPipeline()  # lazy loads index/embeddings

class AskReq(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskReq):
    answer = rag.answer(req.question)
    return answer

@app.get("/metrics")
def metrics():
    return rag.metrics()
