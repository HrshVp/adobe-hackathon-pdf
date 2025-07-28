# Adobe India Hackathon 2025 - Round 1B  
**Persona-Driven Document Intelligence (Enhanced Semantic Section Extractor)**

---

## Overview

This project provides a Dockerized solution that processes a collection of PDFs and, given a persona description and a job-to-be-done, extracts and ranks the most relevant document sections. The solution uses lightweight, offline NLP with sentence-transformers (MiniLM model) for semantic similarity scoring, paragraph-level granularity, and highlights relevant sentences for improved interpretability.

---

## Features

- **Input:**  
  - Folder of PDFs (`/app/input`)  
  - `persona.txt` - text description of the persona (user role/expertise)  
  - `job.txt` - text description of the job-to-be-done

- **Output:**  
  - JSON file (`challenge1b_output.json` in `/app/output`) containing:  
    - Metadata (input docs, persona, job, timestamp)  
    - Ranked list of relevant sections with:  
      - Document name  
      - Page number  
      - Section title (if available)  
      - Text snippet (paragraph)  
      - Highlighted sentences relevant to the query  
      - Importance rank

- Uses **offline transformer model** (`paraphrase-MiniLM-L6-v2`) included in `models/` folder to avoid any internet calls.

---

## Folder Structure (Prior to Docker Build)

adobe_pdf_persona/
├── input/ # PDFs to analyze (3-10)
├── output/ # Output JSON is saved here
├── models/ # Pre-downloaded transformer model files
│ └── paraphrase-MiniLM-L6-v2/
├── persona.txt # Persona description text file
├── job.txt # Job to be done text file
├── persona_summarizer.py # Main Python script
├── Dockerfile # Docker build instructions
├── README.md # This file
├── approach_explanation.md # Write-up describing methodology

text

---

## Requirements

- Docker (tested on amd64 platform)
- No internet connection required during Docker build or runtime
- Runs entirely on CPU within time and resource limits

---

## How to Build

From the project root directory, run:

docker build --platform=linux/amd64 -t persona_extractor:myid .

text

This will create a docker image that includes all dependencies and the offline NLP model.

---

## How to Run

Make sure:  
- Your PDFs are inside the `input` folder.  
- `persona.txt` and `job.txt` are at the project root with relevant text.

Run the container with this command (adjust volume mounts to your OS):

**Linux/Mac:**

docker run --rm
-v $(pwd)/input:/app/input
-v $(pwd)/output:/app/output
-v $(pwd)/persona.txt:/app/persona.txt
-v $(pwd)/job.txt:/app/job.txt
--network none persona_extractor:myid

text

**Windows CMD:**

docker run --rm ^
-v %cd%\input:/app/input ^
-v %cd%\output:/app/output ^
-v %cd%\persona.txt:/app/persona.txt ^
-v %cd%\job.txt:/app/job.txt ^
--network none persona_extractor:myid

text

---

## Output Format

The output JSON (`output/challenge1b_output.json`) will contain:

{
"metadata": {
"input_documents": ["doc1.pdf", "doc2.pdf"],
"persona": "PhD Researcher in Computational Biology",
"job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
"processing_timestamp": "2025-07-28T23:00:00"
},
"extracted_sections": [
{
"document": "doc1.pdf",
"page_number": 5,
"section_title": null,
"importance_rank": 1,
"refined_text": "Paragraph text related to the query...",
"highlighted_sentences": [
"The most relevant sentence to the persona and job.",
"Another important sentence with key details."
]
},
...
]
}

text

---

## Approach

Please see the attached `approach_explanation.md` for a detailed explanation of:  

- How semantic similarity is used for relevance scoring  
- Use of sentence-transformer MiniLM (paraphrase-MiniLM-L6-v2) for offline embeddings  
- Chunking PDFs into paragraphs for granular analysis  
- Highlighting of relevant sentences for each top-ranked section  
- Fully offline processing within a Docker container to meet hackathon constraints

---

## Additional Notes

- **Model files** under `models/paraphrase-MiniLM-L6-v2/` are included to guarantee offline execution.  
- The solution is designed for scalability and can be extended to include heading-level structure extraction or integrate additional NLP features if needed.  
- Output JSON adheres to the hackathon’s prescribed format.

---

## Contact / Author

Name: Your Name  
Email: your.email@example.com  
College: Your College Name  

Feel free to reach out for any clarifications or assistance with running the solution.

---

## License

This project is for Adobe India Hackathon 2025 submission and is under a non-commercial use license.

---

Thank you for considering my submission! 🚀
