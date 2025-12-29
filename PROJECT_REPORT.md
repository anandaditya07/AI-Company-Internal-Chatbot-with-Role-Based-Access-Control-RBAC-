# Project Report: Internal RAG Chatbot with Role-Based Access Control

## 1. Executive Summary
This project involves the development of a secure, internal AI-powered chatbot designed to assist employees in retrieving information from company documents. The core innovation of this system is the integration of **Retrieval-Augmented Generation (RAG)** with strict **Role-Based Access Control (RBAC)**. This ensures that employees can only access information relevant to their specific department (e.g., Finance, HR, Engineering), protecting sensitive data while leveraging the power of AI.

## 2. Key Features Implemented

### 🔐 Secure Authentication & Authorization
- **JWT Authentication:** Implemented a secure login system using JSON Web Tokens (JWT). Users must log in to access the chatbot.
- **Role-Based Access Control (RBAC):** Defined specific roles (Finance, Marketing, HR, Engineering, General) and restricted document access based on these roles.
  - *Example:* A user with the "Finance" role can query financial reports, but an "Engineering" user cannot.

### 🧠 Retrieval-Augmented Generation (RAG) Pipeline
- **Document Ingestion:** Built a preprocessing pipeline to read, parse, and "chunk" various document formats (Markdown, CSV) from the `workspace_documents` directory.
- **Vector Database:** Utilized **ChromaDB** to store vector embeddings of document chunks, allowing for semantic search (finding documents based on *meaning* rather than just keywords).
- **Semantic Search:** Integrated `SentenceTransformers` to convert text into numerical vectors for efficient similarity search.

### 🤖 Intelligent Response Generation
- **Context Awareness:** The system retrieves the most relevant document chunks based on the user's query and their assigned role.
- **AI Integration (with Fallback):** 
  - **Primary Mode:** Designed to connect with OpenAI's GPT models to generate natural language answers based on retrieved context.
  - **Mock/Fallback Mode:** Implemented a robust fallback mechanism. If no OpenAI API key is provided, the system directly presents the raw text retrieved from the documents, ensuring users can still access information without external dependencies.

### 🖥️ User-Friendly Interface
- **Streamlit Frontend:** Developed a clean, interactive web interface.
  - **Login Screen:** concise and secure entry point.
  - **Chat Interface:** Simple text input for queries with clear display of answers and source citation (role verification).

## 3. Technical Architecture

*   **Backend:** Python **FastAPI**
    *   Handles API requests for login (`/token`) and querying (`/query`).
    *   Enforces security logic and coordinates the RAG pipeline.
*   **Frontend:** **Streamlit**
    *   Provides the graphical user interface (GUI) for end-users.
    *   Communicates with the backend via HTTP requests.
*   **Database:** **ChromaDB** (Vector Store)
    *   Persists document embeddings for fast retrieval.
*   **ML/AI Models:** 
    *   `all-MiniLM-L6-v2` (SentenceTransformers) for embeddings.
    *   OpenAI GPT (Optional) for answer synthesis.

## 4. Implementation Workflow (What I Did)

### Step 1: Data Preparation
1.  Analyzed the raw data in `workspace_documents`.
2.  Wrote `preprocessing.py` to iterate through files, splitting text into manageable chunks.
3.  Mapped specific files to specific roles (e.g., `hr_data.csv` -> HR Role).

### Step 2: Vector Store Setup
1.  Created `vector_db_setup.py` to initialize ChromaDB.
2.  Generated embeddings for all document chunks and stored them with metadata (Role, Filename).

### Step 3: Backend Development
1.  Set up `main.py` using FastAPI.
2.  Implemented the `/token` endpoint to validate credentials and issue JWTs.
3.  Built the `/query` endpoint:
    *   Validates the user's token.
    *   Embeds the user's query.
    *   Queries ChromaDB with a filter: `where={"role": user["role"]}`.
    *   Returns the results.

### Step 4: Frontend Development
1.  Created `frontend/app.py` using Streamlit.
2.  Built state management to handle user sessions (staying logged in).
3.  Connected the UI forms to the Backend APIs.

### Step 5: Refinement & "Mock Mode" Enhancement
1.  Identified that running without an OpenAI key was returning unhelpful error messages.
2.  Modified the backend logic (`main.py`) to return the **full retrieved text** when no API key is present. This ensures the tool is immediately useful for document retrieval even without an LLM subscription.

## 5. How to Run the Project

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initialize Database (First time only):**
    ```bash
    python preprocessing.py
    python vector_db_setup.py
    ```
3.  **Start the Backend:**
    ```bash
    uvicorn backend.main:app --reload
    ```
4.  **Start the Frontend:**
    ```bash
    streamlit run frontend/app.py
    ```

## 6. Conclusion
This project successfully demonstrates a secure, enterprise-grade architecture for internal knowledge management. By combining modern vector search with strict access controls, it provides a scalable foundation for any organization looking to leverage their internal data securely.
