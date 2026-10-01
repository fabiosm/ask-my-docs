import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from openai import OpenAI

from rag import chunk_text, extract_text, save_chunks, search

load_dotenv()
client = OpenAI(
  api_key=os.getenv("GEMINI_API_KEY"),
  base_url=os.getenv("GEMINI_BASE_URL")
)
app = FastAPI(title="Ask My Docs", description="Ask questions about your documents using OpenAI's API.", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL")

@app.post("/ask")
def ask(question: str):
  context = "\n\n".join(search(question, DATABASE_URL))
  stream = client.chat.completions.create(
    model=os.getenv("GEMINI_MODEL_NAME"),
    messages=[
      {"role": "system", "content": f"Answer using this context:\n{context}"},
      {"role": "user", "content": question}
    ],
    stream=True
  )
  def generate():
    for chunk in stream:
      if chunk.choices[0].delta.content:
        yield f"data: {chunk.choices[0].delta.content}\n\n"

  return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/upload")
def upload(file: UploadFile):
  path = f"temp_{file.filename}"
  with open(path, "wb") as f:
    f.write(file.file.read())
  text = extract_text(path)
  chunks = chunk_text(text)
  save_chunks(chunks, DATABASE_URL)
  return {"chunks_saved": len(chunks), "message": "File uploaded and processed successfully."}
