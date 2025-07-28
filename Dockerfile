FROM --platform=linux/amd64 python:3.9-slim

# Install dependencies
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir pymupdf sentence-transformers torch

# Copy the transformer model to the offline cache directory
COPY models /app/models

ENTRYPOINT ["python", "persona_summarizer.py"]
