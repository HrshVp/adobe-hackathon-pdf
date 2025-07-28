import os
import fitz  # PyMuPDF
import json
import datetime
from sentence_transformers import SentenceTransformer, util
import torch

def read_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_chunks(pdf_path):
    # Returns list of {document, page, heading, text}
    doc = fitz.open(pdf_path)
    chunks = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("text")
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        for para in paragraphs:
            chunks.append({
                "document": os.path.basename(pdf_path),
                "page": page_num + 1,
                "section_title": None,      # Could extract headings here (advanced)
                "text": para
            })
    return chunks

def get_relevance_scores(chunks, query, model):
    chunk_texts = [chunk['text'] for chunk in chunks]
    device = "cpu"
    query_emb = model.encode(query, convert_to_tensor=True, device=device)
    chunk_embs = model.encode(chunk_texts, convert_to_tensor=True, device=device, show_progress_bar=False)
    scores = util.pytorch_cos_sim(query_emb, chunk_embs)[0].cpu().numpy()
    for i, chunk in enumerate(chunks):
        chunk['score'] = float(scores[i])
    chunks = sorted(chunks, key=lambda x: -x['score'])
    return chunks

def highlight_matching_sentences(chunk, query, model, top_k=2):
    sentences = [s.strip() for s in chunk['text'].split('. ') if len(s.strip()) > 10]
    if not sentences:
        return []
    device = "cpu"
    query_emb = model.encode(query, convert_to_tensor=True, device=device)
    sent_embs = model.encode(sentences, convert_to_tensor=True, device=device, show_progress_bar=False)
    sims = util.pytorch_cos_sim(query_emb, sent_embs)[0].cpu().numpy()
    ranked = sorted(zip(sentences, sims), key=lambda x: -x[1])
    return [s for s, _ in ranked[:top_k]]

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    persona = read_text_file("/app/persona.txt")
    job = read_text_file("/app/job.txt")
    query = persona + " " + job

    # Always load model from local cache!
    model = SentenceTransformer('/app/models/paraphrase-MiniLM-L6-v2', device='cpu')

    all_chunks = []
    for fname in os.listdir(input_dir):
        if fname.lower().endswith(".pdf"):
            all_chunks += extract_chunks(os.path.join(input_dir, fname))

    scored_chunks = get_relevance_scores(all_chunks, query, model)

    results = []
    for rank, chunk in enumerate(scored_chunks[:10], 1):   # Top 10
        highlights = highlight_matching_sentences(chunk, query, model)
        results.append({
            "document": chunk["document"],
            "page_number": chunk["page"],
            "section_title": chunk.get("section_title"),
            "importance_rank": rank,
            "refined_text": chunk["text"],
            "highlighted_sentences": highlights
        })

    metadata = {
        "input_documents": [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.datetime.now().isoformat(),
    }
    output = {
        "metadata": metadata,
        "extracted_sections": results,
    }
    with open(os.path.join(output_dir, "challenge1b_output.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
