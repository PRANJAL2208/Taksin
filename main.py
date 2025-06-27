from fastapi import FastAPI, UploadFile, File
from typing import Optional
from transformers import pipeline
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain_community.llms import HuggingFaceHub
from langchain_huggingface import HuggingFaceEmbeddings
import os, tempfile, subprocess
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
vectorstore = None

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

class QueryRequest(BaseModel):
    question: str
    model: str  # 'openai', 'huggingface', or 'ollama'
    openai_api_key: Optional[str] = None    # Optional user-provided API key

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(docs, embedding_model)
    return {"message": "Document uploaded and processed successfully."}

@app.post("/query")
async def query(req: QueryRequest):
    if not vectorstore:
        return {"error": "No document uploaded."}

    if req.model == 'openai':
        try:
            openai_key = req.openai_api_key or os.getenv('OPENAI_API_KEY')
            llm = OpenAI(api_key=openai_key, temperature=0)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever()
            )
            response = qa_chain.run(req.question)
            return {"answer": response}
        except Exception as e:
            return {"error": f"OpenAI error: {str(e)}"}

    elif req.model == 'huggingface':
        try:
            qa_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-large"
            )
            docs = vectorstore.similarity_search(req.question, k=4)
            context = " ".join([doc.page_content for doc in docs])

            prompt = f"Context: {context}\n\nQuestion: {req.question}\nAnswer:"
            response = qa_pipeline(prompt, max_length=512)
            return {"answer": response[0]['generated_text']}
        except Exception as e:
            return {"error": f"HuggingFace Local error: {str(e)}"}


    elif req.model == 'ollama':
        try:
            prompt = f"Answer this question: {req.question}"
            result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True)
            return {"answer": result.stdout.strip()}
        except Exception as e:
            return {"error": f"Ollama error: {str(e)}"}

    else:
        return {"error": "Invalid model choice. Use 'openai', 'huggingface', or 'ollama'."}
