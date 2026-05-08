def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5", 
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True
        }
    )