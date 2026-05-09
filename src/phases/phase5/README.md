# Phase 5 — Generation and Formatting

Status: **Groq integration implemented**.

Planned responsibilities:
- grounded answer generation using **Groq** (`llama3-8b-8192`),
- 3-sentence and single-link formatting validation,
- footer date formatting.

## Usage

```python
from src.phases.phase5 import GroqGenerator

generator = GroqGenerator()
answer = generator.generate_answer("What is the exit load?", context_chunks)
```

