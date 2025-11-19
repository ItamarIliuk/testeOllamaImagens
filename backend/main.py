import base64
import json
from typing import AsyncGenerator

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ollama import AsyncClient

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form("llava"),
) -> StreamingResponse:
    """
    Analyzes an uploaded image using Ollama and streams the response.
    """
    # Read image content
    image_content = await image.read()
    
    # Encode image to base64 (Ollama expects base64 string or bytes)
    # The python ollama library handles bytes directly usually, but let's be safe
    # and pass the bytes we read.
    
    async def generate_response() -> AsyncGenerator[str, None]:
        client = AsyncClient()
        try:
            async for part in await client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_content],
                    }
                ],
                stream=True,
            ):
                # Extract content from the response chunk
                content = part.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate_response(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
