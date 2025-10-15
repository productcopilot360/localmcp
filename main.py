from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Local MCP Server")

# ✅ Your MCP manifest
MCP_MANIFEST = {
    "name": "local-mcp-server",
    "version": "0.1.0",
    "description": "Local MCP server exposing summarize and sentiment analysis tools",
    "entry_point": "https://web-production-fac8.up.railway.app",
    "protocol": "http/1.1",
    "authentication": {"type": "none"},
    "tools": [
        {
            "name": "summarize_feedback",
            "description": "Summarizes user feedback text.",
            "args": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Feedback text to summarize."
                    }
                },
                "required": ["text"]
            },
            "returns": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"}
                }
            }
        },
        {
            "name": "sentiment_check",
            "description": "Detects sentiment (positive/neutral/negative) in text.",
            "args": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Input text to analyze."
                    }
                },
                "required": ["text"]
            },
            "returns": {
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string"}
                }
            }
        }
    ],
    "resources": [
        {
            "name": "insight_resource",
            "description": "Example insight resource endpoint",
            "endpoint": "/resources/insights"
        }
    ]
}

# ✅ 1. Discovery endpoint for MCP clients (POST /)
@app.post("/")
async def post_manifest():
    return JSONResponse(content=MCP_MANIFEST)

# ✅ 2. Optional schema endpoint for manual testing
@app.get("/schema")
async def get_schema():
    return JSONResponse(content=MCP_MANIFEST)

# ✅ 3. Tool invocation model and endpoint
class InvokeRequest(BaseModel):
    tool_name: str
    params: dict

@app.post("/invoke")
async def invoke_tool(req: InvokeRequest):
    tool_name = req.tool_name
    params = req.params

    if tool_name == "summarize_feedback":
        text = params.get("text", "")
        summary = text[:75] + "..." if len(text) > 75 else text
        return {"summary": summary}

    elif tool_name == "sentiment_check":
        text = params.get("text", "").lower()
        sentiment = "neutral"
        if any(x in text for x in ["good", "great", "excellent", "love", "amazing"]):
            sentiment = "positive"
        elif any(x in text for x in ["bad", "terrible", "poor", "hate", "slow"]):
            sentiment = "negative"
        return {"sentiment": sentiment}

    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")

# ✅ 4. Example resource endpoint
@app.get("/resources/insights")
async def get_insights():
    return {"insights": ["This is a demo resource endpoint."]}
