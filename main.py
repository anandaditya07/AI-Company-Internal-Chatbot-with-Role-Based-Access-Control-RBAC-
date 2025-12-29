from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import jwt
import datetime
import os
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import openai

# FastAPI app
app = FastAPI()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Secret key for JWT
SECRET_KEY = "your_secret_key"

# Updated users_db with email IDs and passwords
users_db = {
    "finance_user@company.com": {"username": "finance_user", "password": "finance123", "role": "Finance"},
    "marketing_user@company.com": {"username": "marketing_user", "password": "marketing123", "role": "Marketing"},
    "hr_user@company.com": {"username": "hr_user", "password": "hr123", "role": "HR"},
    "engineering_user@company.com": {"username": "engineering_user", "password": "engineering123", "role": "Engineering"},
    "general_user@company.com": {"username": "general_user", "password": "general123", "role": "General"},
}

# Role-based access control
ROLE_HIERARCHY = {
    "C-Level": 5,
    "Finance": 4,
    "Marketing": 3,
    "HR": 2,
    "Employees": 1,
}

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str

class Query(BaseModel):
    query: str

# Authenticate user
def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return None
    return user

# Create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Dependency: Get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user = users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# Initialize ChromaDB client
client = PersistentClient(path="vector_store")
collection = client.get_collection("company_documents")

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai_client = openai.OpenAI(api_key=api_key)
else:
    openai_client = None

# Token endpoint
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@app.get("/protected")
def read_protected(user: dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, you have access to {user['role']} data!"}

# RAG query endpoint
@app.post("/query")
def query_rag_pipeline(query: Query, user: dict = Depends(get_current_user)):
    try:
        # Generate embedding for the query
        query_embedding = embedding_model.encode(query.query).tolist()

        # Perform semantic search filtered by role
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where={"role": user["role"]}
        )

        # Prepare context from results
        context = "\n".join([doc for doc in results["documents"][0]]) if results["documents"] else "No relevant documents found."

        # Generate answer using OpenAI
        if openai_client:
            try:
                prompt = f"Based on the following context, answer the question: {query.query}\n\nContext:\n{context}\n\nAnswer:"
                response = openai_client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7
                )
                answer = response.choices[0].text.strip()
            except Exception as e:
                answer = f"OpenAI Error: {str(e)}. Context preview: {context[:200]}..."
        else:

            # Fallback: Return the retrieved context directly as the answer
            answer = context

        return {"answer": answer, "role": user["role"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")
