# RAG Design

Supported inputs:

- `.txt`
- `.md`
- `.pdf`

Current flow:

1. Validate upload size and type.
2. Extract text.
3. Normalize whitespace.
4. Chunk into overlapping spans.
5. Store embeddings, metadata, and source references.
6. Rank chunks by similarity at query time.
7. Return grounded snippets with citations.

