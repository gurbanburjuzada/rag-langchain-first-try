import fitz

from src.config import path_to_data

file_names = ["2606.01360v2.pdf", "2607.16496v1.pdf", "2607.16576v1.pdf",
              "2607.16880v1.pdf", "2607.17006v1.pdf", "2607.17141v1.pdf",
              "2607.17609v1.pdf", "2607.17821v1.pdf", "2607.17932v1.pdf"]

# We open each of the 9 files, move through pages and extract them one-by-one.
# texts dictionary is supposed to store this converted extractions
texts = {}
for i, fn in enumerate(file_names, start=1):
    # Initialising an empty string for the file key to avoid a KeyError
    texts[i] = ""
    file_path = path_to_data / "raw_pdfs" / fn
    with fitz.open(file_path) as doc:
        for page in doc:
            texts[i] += page.get_text()
        target_path = path_to_data / "extracted_text" / f"article{i}.txt"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as file:
            file.write(texts[i])

print(f"Extracted {len(texts)} papers to {path_to_data / 'extracted_text'}")
