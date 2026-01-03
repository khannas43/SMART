#!/usr/bin/env python3
"""
Clean and extract JSON from Perplexity responses
Handles cases where Perplexity adds markdown or explanations
"""

import json
import re
from pathlib import Path

def clean_perplexity_response(text: str) -> list:
    """Extract JSON from Perplexity response"""
    
    # Try to find JSON array
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Try to parse entire response
    try:
        return json.loads(text)
    except:
        pass
    
    # Try to extract between ```json and ```
    code_block = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except:
            pass
    
    # Try to extract between ``` and ```
    code_block = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except:
            pass
    
    return []

def clean_batch_file(filepath: Path) -> bool:
    """Clean a single batch file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Try to parse as JSON first
        try:
            json.loads(content)
            print(f"✓ {filepath.name} is already valid JSON")
            return True
        except:
            pass
        
        # Clean and extract JSON
        schemes = clean_perplexity_response(content)
        if schemes:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(schemes, f, indent=2, ensure_ascii=False)
            print(f"✓ Cleaned {filepath.name}: {len(schemes)} schemes")
            return True
        else:
            print(f"✗ Failed to extract JSON from {filepath.name}")
            print(f"  File size: {len(content)} bytes")
            print(f"  First 200 chars: {content[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error processing {filepath.name}: {e}")
        return False

if __name__ == "__main__":
    batch_dir = Path("data/training/batches")
    
    if not batch_dir.exists():
        print(f"Error: {batch_dir} not found")
        exit(1)
    
    # Process all JSON files
    batch_files = sorted(list(batch_dir.glob("batch_*.json")) + 
                        list(batch_dir.glob("Batch*.json")))
    
    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        exit(1)
    
    print(f"Processing {len(batch_files)} batch files...\n")
    
    success_count = 0
    for batch_file in batch_files:
        if clean_batch_file(batch_file):
            success_count += 1
    
    print(f"\n✓ Successfully processed {success_count}/{len(batch_files)} files")
    
    if success_count < len(batch_files):
        print(f"\n⚠ {len(batch_files) - success_count} files need manual review")

