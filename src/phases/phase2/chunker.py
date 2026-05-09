"""Phase 2: Semantic Chunking of Markdown documents."""
import hashlib

def chunk_markdown(markdown_text: str, scheme_id: str, source_url: str, snapshot_id: str, extra_metadata: dict = None) -> list[dict]:
    """
    Split markdown text by headers and attach metadata.
    """
    chunks = []
    current_headers = {}
    current_chunk_lines = []
    
    extra_metadata = extra_metadata or {}
    
    for line in markdown_text.split('\n'):
        if line.startswith('#'):
            # Save previous chunk
            text = "\n".join(current_chunk_lines).strip()
            if text:
                heading_path = " > ".join(current_headers[k] for k in sorted(current_headers.keys()))
                content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
                
                meta = {
                    "scheme_id": scheme_id,
                    "source_url": source_url,
                    "heading_path": heading_path,
                    "snapshot_id": snapshot_id,
                    "content_hash": content_hash
                }
                meta.update(extra_metadata)
                
                chunks.append({
                    "text": text,
                    "metadata": meta
                })
            current_chunk_lines = []
            
            # Update headers
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            
            # Clear deeper headers
            current_headers = {k: v for k, v in current_headers.items() if k < level}
            current_headers[level] = header_text
        else:
            if line.strip() or current_chunk_lines: # keep intra-paragraph blank lines but ignore leading blanks
                current_chunk_lines.append(line)
                
    # Save the final chunk
    text = "\n".join(current_chunk_lines).strip()
    if text:
        heading_path = " > ".join(current_headers[k] for k in sorted(current_headers.keys()))
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        meta = {
            "scheme_id": scheme_id,
            "source_url": source_url,
            "heading_path": heading_path,
            "snapshot_id": snapshot_id,
            "content_hash": content_hash
        }
        meta.update(extra_metadata)
        
        chunks.append({
            "text": text,
            "metadata": meta
        })
        
    return chunks
