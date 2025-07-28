# Adobe Hackathon - Round 1A & 1B Persona-Driven PDF Intelligence

## Approach
(brief description...)

## Requirements
- Docker (tested on linux/amd64)
- No internet connection required

## How to Build
docker build --platform=linux/amd64 -t persona_extractor:YOURID .

## How to Run
docker run --rm \
-v $(pwd)/input:/app/input \
-v $(pwd)/output:/app/output \
-v $(pwd)/persona.txt:/app/persona.txt \
-v $(pwd)/job.txt:/app/job.txt \
--network none persona_extractor:YOURID

## Model
Model files are pre-included in the `models/` directory.

## Author
Your Name | Email | College
