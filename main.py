from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime
from fastapi.responses import JSONResponse

app = FastAPI(title="Local MCP Server", version="0.3.0")


from fastapi.responses import JSONResponse

@app.post("/")
async def post_root():
    """Standard MCP discovery endpoint"""
    return JSONResponse(
        content=MCP_MANIFEST,
        media_type="application/json",
        status_code=200
    )

@app.get("/schema")
def get_schema():
    """Expose MCP manifest for tool discovery (required by some MCP clients)."""
    return JSONResponse(content=MCP_MANIFEST)

# -------------------------------------------------------------------
# 1️⃣ Load Manifest (Single Source of Truth)
# -------------------------------------------------------------------

MCP_MANIFEST_PATH = Path(__file__).parent / "mcp.json"

try:
    with open(MCP_MANIFEST_PATH, "r") as f:
        MCP_MANIFEST = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"Missing manifest file: {MCP_MANIFEST_PATH}")

# -------------------------------------------------------------------
# 2️⃣ Mock Resource Data (for demonstration)
# -------------------------------------------------------------------

INSIGHTS_DB = [
    {
        "id": 1,
        "customer": "Acme Corp",
        "feedback": "The dashboard is slow to load.",
        "sentiment": "negative",
        "created_at": "2025-10-15T12:00:00Z"
    },
    {
        "id": 2,
        "customer": "Globex",
        "feedback": "Love the new UI, very clean design!",
        "sentiment": "positive",
        "created_at": "2025-10-14T09:30:00Z"
    }
]

# -------------------------------------------------------------------
# 3️⃣ Define Request Models
# -------------------------------------------------------------------

class InvokeRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any]

# -------------------------------------------------------------------
# 4️⃣ Implement Tools
# -------------------------------------------------------------------

def summarize_feedback(text: str) -> str:
    """Simple summarizer for demonstration."""
    if not text:
        return "Empty input."
    return text[:80] + "..." if len(text) > 80 else text

def sentiment_check(text: str) -> str:
    """Basic sentiment classification."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["bad", "slow", "bug", "issue", "poor"]):
        return "negative"
    elif any(w in text_lower for w in ["good", "great", "excellent", "love", "amazing"]):
        return "positive"
    return "neutral"

# -------------------------------------------------------------------
# 5️⃣ Endpoints
# -------------------------------------------------------------------

@app.get("/")
def root():
    """Root route with metadata summary."""
    return {
        "server": MCP_MANIFEST["name"],
        "version": MCP_MANIFEST["version"],
        "description": MCP_MANIFEST["description"],
        "entry_point": MCP_MANIFEST["entry_point"],
        "resources": [r["endpoint"] for r in MCP_MANIFEST.get("resources", [])],
        "tools": [t["name"] for t in MCP_MANIFEST.get("tools", [])],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/resources/insights")
def list_insights(limit: Optional[int] = 10):
    """List recent insights (mock data)."""
    return {"data": INSIGHTS_DB[:limit], "count": len(INSIGHTS_DB)}


@app.post("/invoke")
def invoke_tool(req: InvokeRequest):
    """Invoke tools defined in the manifest."""
    tool_name = req.tool_name
    params = req.params

    if tool_name == "summarize_feedback":
        summary = summarize_feedback(params.get("text", ""))
        return {"summary": summary}

    elif tool_name == "sentiment_check":
        sentiment = sentiment_check(params.get("text", ""))
        return {"sentiment": sentiment}

    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
