import os
import json
import gradio as gr

from llama_index import (
    Document,
    GPTVectorStoreIndex,
    ServiceContext,
    LLMPredictor,
)
from transformers import AutoTokenizer, AutoModelForCausalLM
from chromadb.config import Settings
from llama_index import ChromaVectorStore

# 1. Chargement du token Hugging Face (défini en variable d'environnement)
HF_TOKEN = os.getenv("HF_TOKEN")

# 2. Lecture des chunks générés
documents = []
with open("chunks.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        documents.append(
            Document(
                text=obj["text"],
                doc_id=obj["id"],
                extra_info={"source": obj["source"]}
            )
        )

# 3. Configuration de ChromaDB pour le stockage des vecteurs
chroma_settings = Settings()
vector_store = ChromaVectorStore(
    persist_directory="./chroma_db",
    settings=chroma_settings
)

# 4. Création de l’index vectoriel RAG
service_context = ServiceContext.from_defaults()
index = GPTVectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
    service_context=service_context
)

# 5. Chargement du modèle Mistral-7B-Instruct quantifié
tokenizer = AutoTokenizer.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3-quantized",
    use_auth_token=HF_TOKEN,
    use_fast=True
)
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3-quantized",
    use_auth_token=HF_TOKEN,
    device_map="auto",
    torch_dtype="auto"
)
llm_predictor = LLMPredictor(llm=model, tokenizer=tokenizer)

# 6. Fonction de réponse
def answer(message, history):
    """
    Prend le message utilisateur et l'historique (non utilisé ici),
    renvoie la réponse générée par le moteur RAG.
    """
    query_engine = index.as_query_engine(llm_predictor=llm_predictor)
    resp = query_engine.query(message)
    return resp.response

# 7. Interface Gradio en mode Chat
demo = gr.ChatInterface(
    fn=answer,
    title="Chatbot Mouvement Koa",
    description="Posez vos questions au sujet du Mouvement Koa."
)

if __name__ == "__main__":
    demo.launch()
