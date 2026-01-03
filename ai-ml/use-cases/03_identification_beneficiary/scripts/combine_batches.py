#!/usr/bin/env python3
"""
Combine all batch JSON files into one training dataset
"""

import json
from pathlib import Path

def combine_batches(batch_dir: str = "data/training/batches", 
                   output_file: str = "data/training/schemes_raw.json"):
    """Combine all batch JSON files into one"""
    
    all_schemes = []
    # Try both naming patterns: batch_*.json and Batch*.json
    batch_files = sorted(list(Path(batch_dir).glob("batch_*.json")) + 
                        list(Path(batch_dir).glob("Batch*.json")))
    
    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        return []
    
    for batch_file in batch_files:
        print(f"Loading {batch_file.name}...")
        try:
            with open(batch_file, "r", encoding="utf-8") as f:
                schemes = json.load(f)
                if isinstance(schemes, list):
                    all_schemes.extend(schemes)
                    print(f"  ✓ Added {len(schemes)} schemes")
                else:
                    print(f"  ✗ Warning: {batch_file.name} is not a JSON array")
        except json.JSONDecodeError as e:
            print(f"  ✗ Error parsing {batch_file.name}: {e}")
        except Exception as e:
            print(f"  ✗ Error reading {batch_file.name}: {e}")
    
    # Save combined
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_schemes, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Combined {len(all_schemes)} schemes into {output_file}")
    return all_schemes

if __name__ == "__main__":
    combine_batches()

