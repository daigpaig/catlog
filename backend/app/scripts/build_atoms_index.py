# scripts/build_atoms_index.py
from __future__ import annotations
from pathlib import Path
import json
import uuid
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file, data_gen_file

def make_atoms(course):
    """Extract atoms (searchable text chunks) from a course record."""
    atoms = []
    cid = course["course_id"]
    title = course.get("title", "")
    desc = (course.get("desc") or "").strip()
    first_sents = desc.split(". ")[:2]
    desc_snippet = ". ".join(first_sents).strip()

    if title:
        atoms.append((cid, "TITLE", title))
    if desc_snippet:
        atoms.append((cid, "DESC_SENT", desc_snippet))

    for inst in course.get("instructors", []):
        if inst and inst.strip():
            atoms.append((cid, "INSTRUCTOR", inst.strip()))

    # Handle meeting_text from Paper API normalized format
    meeting_text = course.get("meeting_text", "")
    if meeting_text and meeting_text.strip():
        atoms.append((cid, "MEETING", meeting_text.strip()))

    # Handle topics from sections
    sections = course.get("sections", [])
    for sec in sections:
        if isinstance(sec, dict):
            topic = sec.get("topic", "")
            if topic and topic.strip():
                atoms.append((cid, "TOPIC", topic.strip()))

def embed_texts(texts):
    """Embed texts using OpenAI embeddings API."""
    try:
        from openai import OpenAI
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Use text-embedding-3-small or text-embedding-ada-002
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"Warning: Could not embed texts: {e}")
        print("Returning zero vectors (index will be empty)")
        return [[0.0] * 1536 for _ in texts]  # text-embedding-3-small dimension

def main():
    catalog_path = data_file("5000_w_desc.json")
    if not catalog_path.exists():
        print(f"Error: {catalog_path} not found. Run build_catalog_json.py first.")
        return
    
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    
    # Initialize Chroma
    try:
        import chromadb
        chroma_path = data_gen_file("chroma")
        chroma_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(chroma_path))
        col = client.get_or_create_collection("atoms")
    except ImportError:
        print("Error: chromadb not installed. Run: pip install chromadb")
        return
    except Exception as e:
        print(f"Error initializing Chroma: {e}")
        return

    texts, metadatas, ids = [], [], []
    for c in catalog:
        for (cid, atom_type, text) in make_atoms(c):
            if not text.strip():
                continue
            texts.append(text)
            metadatas.append({"course_id": cid, "atom_type": atom_type})
            ids.append(str(uuid.uuid4()))

    if not texts:
        print("no atoms to index")
        return

    # Embed in batches
    B = 256
    print(f"Indexing {len(texts)} atoms in batches of {B}...")
    for i in range(0, len(texts), B):
        batch = texts[i:i+B]
        batch_ids = ids[i:i+B]
        batch_metas = metadatas[i:i+B]
        print(f"Processing batch {i//B + 1}/{(len(texts) + B - 1)//B}...")
        embs = embed_texts(batch)
        col.add(
            ids=batch_ids,
            metadatas=batch_metas,
            embeddings=embs,
            documents=batch
        )

    print(f"Indexed {len(texts)} atoms into {chroma_path}")

if __name__ == "__main__":
    main()


