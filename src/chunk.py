import json
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import path_to_data, CHUNK_SIZE, CHUNK_OVERLAP


# Physics papers reliably have a references section marked this way — cut everything after it
def strip_references(text: str) -> str:
    match = re.search(r"\n\s*REFERENCES\s*\n", text, re.IGNORECASE)
    if match:
        return text[:match.start()]
    return text


chunks = []
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
for i in range(1, 10):
    with open(path_to_data / "extracted_text" / f"article{i}.txt", encoding="utf-8") as article:
        # splitter.split_text returns list of chunks by slicing given input into "chunk_size" sized strings
        input_string = article.read()
        input_string = strip_references(input_string)
        chunked_text_list = splitter.split_text(input_string)
        # Enumeration is for capturing chunk index, too.
        for j, ct in enumerate(chunked_text_list, start=0):
            chunk = {
                "text": ct,
                "source": f"article{i}",
                "chunk_index": j
            }
            chunks.append(chunk)
target_path = path_to_data / "chunks.json"
with open(target_path, 'w', encoding="utf-8") as file:
    # indent=4 makes the JSON file human-readable and pretty
    # ensure_ascii=False keeps special non-English characters intact
    json.dump(chunks, file, indent=4, ensure_ascii=False)

print(f"Successfully saved {len(chunks)} chunks to {target_path}")
