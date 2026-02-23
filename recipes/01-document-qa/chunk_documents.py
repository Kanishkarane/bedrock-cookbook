"""
Parse SEC filings and split into chunks for embedding
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/chunks")

# Target chunk size (in words)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50  # Words to overlap between chunks


def extract_text_from_html(filepath: Path) -> str:
    """
    Extract clean text from SEC HTML filing.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    # Remove script and style elements
    for element in soup(["script", "style", "table"]):
        element.decompose()
    
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = " ".join(chunk for chunk in chunks if chunk)
    
    return text


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """
    Split text into overlapping chunks.
    """
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        
        if len(chunk.strip()) > 100:  # Skip tiny chunks
            chunks.append({
                "text": chunk,
                "word_count": len(words[start:end]),
                "start_index": start
            })
        
        start = end - overlap  # Overlap for context continuity
    
    return chunks


def process_filing(filepath: Path, output_dir: Path) -> dict:
    """
    Process a single filing: extract text and chunk it.
    """
    filename = filepath.stem
    
    print(f"Processing {filename}...")
    
    # Extract text
    text = extract_text_from_html(filepath)
    print(f"  Extracted {len(text.split())} words")
    
    # Chunk
    chunks = split_into_chunks(text)
    print(f"  Created {len(chunks)} chunks")
    
    # Save chunks
    output_file = output_dir / f"{filename}_chunks.json"
    
    output_data = {
        "source_file": str(filepath),
        "total_chunks": len(chunks),
        "chunk_size": CHUNK_SIZE,
        "chunks": chunks
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"  ✓ Saved to {output_file}")
    
    return output_data


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all HTML files in input directory
    html_files = list(INPUT_DIR.glob("*.htm"))
    
    print(f"Found {len(html_files)} files to process\n")
    
    total_chunks = 0
    for filepath in html_files:
        result = process_filing(filepath, OUTPUT_DIR)
        total_chunks += result["total_chunks"]
    
    print(f"\n{'='*40}")
    print(f"Total chunks created: {total_chunks}")