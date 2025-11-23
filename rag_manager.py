import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

DB_PATH = "./chromadb_store"
ASSET_PATH = "./assets"

class RAGManager:
    def __init__(self):
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
       
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile", 
            temperature=0.1, 
            api_key=os.environ.get("GROQ_API_KEY")
        )
        
    def ingest_documents(self):
        """Reads files from assets folder and builds vector DB."""
        if not os.path.exists(ASSET_PATH):
            os.makedirs(ASSET_PATH)
            
        loaders = [
            DirectoryLoader(ASSET_PATH, glob="*.md", loader_cls=UnstructuredMarkdownLoader),
            DirectoryLoader(ASSET_PATH, glob="*.txt", loader_cls=TextLoader),
            DirectoryLoader(ASSET_PATH, glob="*.html", loader_cls=TextLoader),
        ]
        
        documents = []
        for loader in loaders:
            try:
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading docs: {e}")

        if not documents:
            return "No documents found to ingest."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
            
        Chroma.from_documents(documents=chunks, embedding=self.embeddings, persist_directory=DB_PATH)
        return f"Knowledge Base built successfully with {len(documents)} documents and {len(chunks)} chunks."

    def generate_test_cases(self, prompt_query: str):
        db = Chroma(persist_directory=DB_PATH, embedding_function=self.embeddings)
        retriever = db.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(prompt_query)
        context_text = "\n\n".join([d.page_content + f"\n[Source: {d.metadata.get('source', 'unknown')}]" for d in docs])

        sys_prompt = """
        You are an expert QA Lead. 
        Generate comprehensive test cases based strictly on the provided documentation.
        Return the output as a JSON list of objects with keys: 
        "Test_ID", "Feature", "Test_Scenario", "Expected_Result", "Grounded_In" (source file).
        Do not hallucinate features not present in the context.
        Output ONLY raw JSON.
        """
        final_prompt = f"{sys_prompt}\n\nContext:\n{context_text}\n\nUser Request: {prompt_query}\n\nOutput JSON:"
        response = self.llm.invoke(final_prompt)
        return response.content

    
    def generate_selenium_script(self, test_case_json, html_content):
        """Generates a Python Selenium script based on a specific test case and raw HTML."""
        
        prompt = f"""
        Act as a Senior Selenium Automation Engineer (Python).
        
        Task: Write a professional, runnable Python Selenium script for the following Test Case.
        
        Test Case Info:
        {test_case_json}
        
        Target Page HTML Structure:
        {html_content}
        
        CRITICAL INSTRUCTIONS FOR GENERATION:
        1. **Setup**: Use `webdriver.Chrome()`. ALWAYS include `driver.maximize_window()` right after creating the driver.
        2. **Implicit Logic**: 
           - If the test case implies a successful submission (e.g., "Pay Now", "Checkout", "Happy Path"), **YOU MUST** generate code to fill in ALL required input fields found in the HTML (Name, Email, etc.) with dummy data (e.g., "Vedansh Patel"), even if the test case description implies it is only testing the discount.
           - The "Pay Now" button will NOT work if these fields are empty.
        3. **Negative Testing**: Only skip filling fields if the test case *explicitly* says to test validation errors (e.g., "Test invalid email").
        4. **Visual Feedback**: 
           - Add `print()` statements for every major step (e.g., `print("Applying discount...")`, `print("Filling user details...")`).
           - Add `time.sleep(15)` at the very end of the script (before `driver.quit()`) so the user can observe the final result.
        5. **Selectors**: Use the EXACT IDs found in the HTML provided above.
        6. **Output**: Return ONLY the Python code block.
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    