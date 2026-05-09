"""Script to run Phase 2 semantic chunking on the latest Phase 1 snapshots."""
import json
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phases.phase2.chunker import chunk_markdown

def main():
    state_file = "data/ingestion/state.json"
    manifest_file = "config/phase0/url_manifest.json"
    output_dir = "data/chunks"
    output_file = os.path.join(output_dir, "chunks.jsonl")
    
    if not os.path.exists(state_file) or not os.path.exists(manifest_file):
        print("Error: Required Phase 1 or Phase 0 state/manifest files missing.")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
        
    with open(state_file, 'r') as f:
        state = json.load(f)
        
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
        
    # Map scheme_id to source_url
    url_map = {item['scheme_id']: item['url'] for item in manifest}
        
    all_chunks = []
    
    for scheme_id, info in state.get('schemes', {}).items():
        snapshot_dir = info.get('last_ok_snapshot_dir')
        snapshot_id = info.get('last_ok_batch_id')
        
        if not snapshot_dir:
            print(f"Skipping {scheme_id}, no valid snapshot.")
            continue
            
        parsed_file = os.path.join(snapshot_dir, "parsed", f"{scheme_id}.txt")
        if not os.path.exists(parsed_file):
            print(f"Skipping {scheme_id}, missing parsed markdown: {parsed_file}")
            continue
            
        with open(parsed_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
            
        source_url = url_map.get(scheme_id, "unknown_url")
        fetched_at = info.get('last_ok_fetched_at')
        
        extra_meta = {}
        if fetched_at:
            extra_meta['fetched_at'] = fetched_at
        
        chunks = chunk_markdown(markdown_text, scheme_id, source_url, snapshot_id, extra_metadata=extra_meta)
        all_chunks.extend(chunks)
        print(f"[{scheme_id}] Generated {len(chunks)} chunks.")
        
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
            
    print(f"\nSuccessfully wrote {len(all_chunks)} chunks to {output_file}")

if __name__ == "__main__":
    main()
