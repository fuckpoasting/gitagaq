# notes:

- downloaded the gita from gutenberg
- nuked the last ref + intro/toc
- removed appendix ref matching regex: `\[FN#[0-9]+\]`
- last 3 lines of each chapter are metadata
- dump index into pinecone
- embed question, run cosine sim to index
- get context, dump it into the prompt and generate an answer

# broken:

- ui formatting
- could be refactored in a MUCH better way
