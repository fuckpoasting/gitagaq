import json
from pathlib import Path
from pinecone import Vector
from gitagqa.prep import Chapter, num_tokens_from_string, get_parsed_text
from gitagqa.config import openai_client, max_tokens, model, get_pinecone_index


def batch_chapters(book: list[Chapter]) -> list[list[Chapter]]:
    book.sort(key=lambda x: x.index)

    batches: list[list[Chapter]] = [[]]
    for chapter in book:
        if chapter.tokens + sum([x.tokens for x in batches[-1]]) < max_tokens:
            batches[-1].append(chapter)
        else:
            batches.append([chapter])

    return batches


def generate_embeddings(
    batches: list[list[Chapter]],
):
    batched_prose = []
    for batch in batches:
        batched_prose.append(" ".join([x.prose for x in batch]))

    assert not any([num_tokens_from_string(x) >= max_tokens for x in batched_prose])
    res = openai_client.Embedding.create(input=batched_prose, engine=model)
    return [record["embedding"] for record in res["data"]]


def save_embeddings_to_index(embeddings, metadata, ids):

    vectors = []

    for i in range(len(embeddings)):
        idx_mt = metadata[i]
        for k in idx_mt:

            # drop prose because pinecoom cant handle big metadata
            # this is incredible annoying because then i have to do 
            # a weird hack to get the relevant prose (see: predict.py)
            del idx_mt[k]["book"]
            del idx_mt[k]["tokens"]
            del idx_mt[k]["prose"]

            # convert to str because again, their api is trash
            idx_mt[k] = str(idx_mt[k])

        vectors.append(Vector(id=ids[i], values=embeddings[i], metadata=idx_mt))

    get_pinecone_index().upsert(vectors=vectors)


if __name__ == "__main__":
    cache = Path("./scratch/cached_gita_embeddings.json")

    dry_run = input("dry run (y/n): ")
    if dry_run not in ["y", "n"]:
        raise ValueError

    use_cached_embeddings = input("use cached embeddings (y/n): ")
    if use_cached_embeddings not in ["y", "n"]:
        raise ValueError

    parsed_text = get_parsed_text(Path("./datasets/raw_gita"))
    batches = batch_chapters(parsed_text)

    if dry_run == "y":
        print(batches)
        exit

    if use_cached_embeddings == "n":
        x = generate_embeddings(batches)
        batched_metadata = [{x.index: x.to_json() for x in y} for y in batches]
        ids = ["_".join([str(x.index) for x in y]) for y in batches]

        # cache embeddings
        master = list()
        for y in range(len(x)):
            master.append(
                {"id": ids[y], "values": x[y], "metadata": batched_metadata[y]}
            )

        with open(cache, "w") as f:
            json.dump(master, f)

        save_embeddings_to_index(x, batched_metadata, ids)
    else:
        with open(cache, "r") as f:
            master = json.load(f)

        save_embeddings_to_index(
            [x["values"] for x in master],
            [x["metadata"] for x in master],
            [x["id"] for x in master],
        )
