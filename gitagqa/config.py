import pinecone
import openai
import os


max_tokens = 8191
model = "text-embedding-ada-002"
embedding_dimensions = 1536
pinecone_index_name = "books"
retrieve_token_limit = 1000
generative_model = "text-davinci-003"


openai.api_key = os.environ["OPENAI_API_KEY"]
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"]
)

openai_client = openai
pinecone_client = pinecone


def get_pinecone_index():
    if pinecone_index_name not in pinecone_client.list_indexes():
        pinecone_client.create_index(
            pinecone_index_name,
            dimension=embedding_dimensions,
            metric="cosine",
            metadata_config={"indexed": ["book", "title", "index"]},
        )

    return pinecone_client.Index(pinecone_index_name)
