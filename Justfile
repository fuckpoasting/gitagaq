load_env:= "PINECONE_API_KEY=$(<credentials/pinecone_api_key) PINECONE_ENV=$(<credentials/pinecone_env) OPENAI_API_KEY=$(<credentials/openai)"


download-gita:
    curl -L https://www.gutenberg.org/files/2388/2388-h/2388-h.htm -o ./datasets/gita.htm

generate-embeddings:
    {{load_env}} python -m gitagqa.embedding

predict: 
    {{load_env}} python -m gitagqa.predict

run:
    streamlit run ui.py