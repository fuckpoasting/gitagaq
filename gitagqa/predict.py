from pathlib import Path
from textwrap import dedent
from gitagqa.config import (
    openai_client,
    get_pinecone_index,
    generative_model,
    retrieve_token_limit,
    model,
)

from dataclasses import dataclass

from gitagqa.prep import get_parsed_text, Chapter

book = get_parsed_text(Path("./datasets/raw_gita"))
index = get_pinecone_index()


@dataclass
class PredictionResult:
    relevant_prose: list[Chapter]
    response: str


def retrieve(query):
    openai_res = openai_client.Embedding.create(input=[query], engine=model)

    query_embedding = openai_res["data"][0]["embedding"]
    res = index.query(query_embedding, top_k=2, include_metadata=True)
    ## Hack to get relevant prose from metadata
    # Each embedding has multiple chapters so for now pick the first one
    chapters = res["matches"][0]["id"].split("_")

    relevant_chapters = [x for x in filter(lambda x: str(x.index) in chapters, book)]

    prose_contexts = " ".join([x.prose for x in relevant_chapters])
    prompt_start = "Based on this poem, answer the question.\n\n" + "Poem:\n"

    # This needs some experimenting, right now it spits out a lot of cringe
    limited_context = prose_contexts[:retrieve_token_limit]

    prompt_end = f"\n\nQuestion: {query}\nAnswer:"

    prompt = dedent(
        f"""
        {prompt_start}
        {limited_context}
        ----
        {prompt_end}
        """
    )

    print(prompt)

    res = openai_client.Completion.create(
        prompt=prompt,
        engine=generative_model,
        max_tokens=4096 - len(prompt),  # there has to be a better way lol
    )["choices"][0]["text"]

    return PredictionResult(relevant_prose=relevant_chapters, response=res)


if __name__ == "__main__":
    query = input("Enter prompt: ")
    print(retrieve(query))
