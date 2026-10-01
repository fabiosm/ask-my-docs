import os

from dotenv import load_dotenv
from openai import OpenAI
import psycopg
from pypdf import PdfReader
from pgvector.psycopg import register_vector

load_dotenv()
client = OpenAI(
  api_key=os.getenv("GEMINI_API_KEY"),
  base_url=os.getenv("GEMINI_BASE_URL"),
)

def extract_text(pdf_path: str) -> str:
  reader = PdfReader(pdf_path)
  return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
  chunks = []
  for i in range(0, len(text), size - overlap):
    chunks.append(text[i:i + size])
  return chunks

def embed(text: str) -> list[float]:
  response = client.embeddings.create(
    model="gemini-embedding-001",
    input=text
  )
  return response.data[0].embedding

def save_chunks(chunks: list[str], conn_str: str):
  with psycopg.connect(conn_str) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    register_vector(conn)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS documents (
          id SERIAL PRIMARY KEY,
          content TEXT,
          embedding vector(3072)
      )""")

    for chunk in chunks:
      emb = embed(chunk)
      conn.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (chunk, emb)
      )
    conn.commit()

def search(query: str, conn_str: str, top_k: int = 3) -> list[str]:
  query_emb = embed(query)
  with psycopg.connect(conn_str) as conn:
    register_vector(conn)
    rows = conn.execute(
      "SELECT content FROM documents ORDER BY embedding <=> %s::vector LIMIT %s",
      (query_emb, top_k)
    ).fetchall()
  return [r[0] for r in rows]  