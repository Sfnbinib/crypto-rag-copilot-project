import os, time, pathlib, glob
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "5"))
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

DATA_DIR = pathlib.Path("data/processed")
INDEX_DIR = pathlib.Path("index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

class RagPipeline:
    def __init__(self):
        self._model = SentenceTransformer(MODEL_NAME)
        self._client = chromadb.PersistentClient(path=str(INDEX_DIR))
        self._coll = self._client.get_or_create_collection(
            "crypto_docs",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=MODEL_NAME
            )
        )
        # build index once if empty
        if self._coll.count() == 0:
            self._bulk_ingest()

        self._q_count = 0
        self._p95 = 0.0

    def _bulk_ingest(self):
        docs, ids, metas = [], [], []
        for p in sorted(glob.glob(str(DATA_DIR / "*.txt"))):
            with open(p, "r", encoding="utf-8") as f:
                text = f.read().strip()
            # simple chunk
            for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk = text[i:i+CHUNK_SIZE]
                if len(chunk) < 50: 
                    continue
                docs.append(chunk)
                ids.append(f"{pathlib.Path(p).stem}-{i}")
                metas.append({"source": pathlib.Path(p).name, "offset": i})
        if docs:
            self._coll.add(documents=docs, ids=ids, metadatas=metas)

    def answer(self, question: str) -> Dict:
        t0 = time.time()
        rets = self._coll.query(query_texts=[question], n_results=TOP_K)
        ctxs = [d for d in rets["documents"][0]]
        metas = rets["metadatas"][0]
        # naive synth answer: return concatenated summary-like response
        # (\u0437\u0430\u043c\u0435\u043d\u0438 \u043d\u0430 LLM call, \u0435\u0441\u043b\u0438 \u043d\u0443\u0436\u0435\u043d \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u0438\u0432\u043d\u044b\u0439 \u043e\u0442\u0432\u0435\u0442)
        ans = self._extractive_answer(question, ctxs)
        dt = (time.time() - t0) * 1000

        # online P95 (simple streaming estimate)
        self._q_count += 1
        alpha = 0.1
        self._p95 = max(self._p95, dt) if self._q_count < 10 else (1-alpha)*self._p95 + alpha*dt

        citations = [{"source": m.get("source"), "offset": m.get("offset")} for m in metas]
        return {"answer": ans, "citations": citations, "latency_ms": round(dt, 1)}

    def _extractive_answer(self, question: str, ctxs: List[str]) -> str:
        # \u043f\u0440\u043e\u0441\u0442\u0430\u044f Heuristic: \u0432\u0437\u044f\u0442\u044c 2-3 \u0441\u0430\u043c\u044b\u0435 \u043a\u043e\u0440\u043e\u0442\u043a\u0438\u0435 \u0440\u0435\u043b\u0435\u0432\u0430\u043d\u0442\u043d\u044b\u0435 \u0447\u0430\u0441\u0442\u0438
        chunks = sorted(ctxs, key=len)[:3]
        return "\n\n".join(chunks)

    def metrics(self) -> Dict:
        return {"q_count": self._q_count, "latency_p95_ms": round(self._p95, 1)}
