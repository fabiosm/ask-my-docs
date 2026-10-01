import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI

load_dotenv()
client = OpenAI(
  api_key=os.getenv("GEMINI_API_KEY"),
  base_url=os.getenv("GEMINI_BASE_URL")
)
app = FastAPI(title="Ask My Docs", description="Ask questions about your documents using OpenAI's API.", version="1.0.0")

@app.post("/ask")
def ask(question: str):
  stream = client.chat.completions.create(
    model=os.getenv("GEMINI_MODEL_NAME"),
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": question}
    ],
    stream=True
  )
  def generate():
    for chunk in stream:
      if chunk.choices[0].delta.content:
        yield f"data: {chunk.choices[0].delta.content}\n\n"

  return StreamingResponse(generate(), media_type="text/event-stream")
