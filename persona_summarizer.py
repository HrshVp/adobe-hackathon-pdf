# import os
# import fitz  # PyMuPDF
# import json
# import datetime

# def read_text_file(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return f.read()

# def extract_sections(pdf_path):
#     # For each page: look for heading-style lines (font size, bold, etc.) as in 1A.
#     doc = fitz.open(pdf_path)
#     sections = []
#     for page_num, page in enumerate(doc, 1):
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if "lines" not in block: continue
#             for line in block["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"].strip()
#                     if len(text) < 5: continue  # Skip short "noise"
#                     # Assume font size > XX and bold = heading H1/H2/H3
#                     if span["size"] >= 14 or span["flags"] & 2:   # bold
#                         level = "Section"
#                         sections.append({
#                             "document": os.path.basename(pdf_path),
#                             "page": page_num,
#                             "section_title": text,
#                             "text": text,
#                             "font_size": span["size"]
#                         })
#     return sections

# def rank_sections(sections, persona, job):
#     key_words = set(persona.lower().split() + job.lower().split())
#     ranked = []
#     for sec in sections:
#         content = (sec["section_title"] + " " + sec["text"]).lower()
#         score = sum(kw in content for kw in key_words)
#         sec["importance_rank"] = score
#         if score > 0:  # Only keep 'relevant' sections
#             ranked.append(sec)
#     # Sort by score descending
#     ranked.sort(key=lambda x: -x["importance_rank"])
#     # Add a rank index (optional, for unique order)
#     for idx, sec in enumerate(ranked, 1):
#         sec["importance_rank"] = idx
#     return ranked

# def main():
#     input_dir = "/app/input"
#     output_dir = "/app/output"
#     persona = read_text_file("/app/persona.txt")
#     job = read_text_file("/app/job.txt")
#     all_sections = []
#     for fname in os.listdir(input_dir):
#         if fname.lower().endswith(".pdf"):
#             path = os.path.join(input_dir, fname)
#             all_sections += extract_sections(path)
#     # Now score/rank based on persona & job
#     ranked_sections = rank_sections(all_sections, persona, job)
#     # For sub-section analysis, we will just pick top N and return their text. (Can expand this for partial page highlighting).
#     refined_results = []
#     for sec in ranked_sections[:10]:  # Top 10 sections
#         refined_results.append({
#             "document": sec["document"],
#             "page_number": sec["page"],
#             "section_title": sec["section_title"],
#             "importance_rank": sec["importance_rank"],
#             "refined_text": sec["text"]  # You can expand this to paragraphs under the section, for now just return title
#         })
#     output = {
#         "metadata": {
#             "input_documents": [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")],
#             "persona": persona,
#             "job_to_be_done": job,
#             "processing_timestamp": datetime.datetime.now().isoformat(),
#         },
#         "extracted_sections": refined_results,
#     }
#     with open(os.path.join(output_dir, "challenge1b_output.json"), "w", encoding="utf-8") as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)
    
# if __name__ == "__main__":
#     main()


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
