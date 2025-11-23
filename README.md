# Autonomous QA Agent

## Project Overview

This project implements an intelligent, autonomous QA agent capable of constructing a "testing brain" from project documentation. The system ingests support documents (specifications, guidelines) and HTML structures to:

1. Generate comprehensive, grounded test cases.  
2. Convert those test cases into executable Python Selenium scripts.  

The architecture consists of a FastAPI backend for logic processing and a Streamlit frontend for user interaction. It utilizes RAG (Retrieval-Augmented Generation) to ensure all generated tests are strictly grounded in the provided documentation.

## Prerequisites

- Python 3.10 or higher  
- Google Chrome Browser (for Selenium execution)

## Setup Instructions

### 1. Project Setup

Extract the project files or clone the repository to your local machine.

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**For Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**For macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required libraries using the provided requirements file:

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a file named `.env` in the root directory of the project. Add your Groq API key inside the file:

```text
GROQ_API_KEY=gsk_your_actual_api_key_here
```

## How to Run the Application

The application requires two terminal windows running simultaneously:  
one for the Backend (FastAPI) and one for the Frontend (Streamlit).

### Step 1: Start the Backend

Open your first terminal window, ensure your virtual environment is active, and run:

```bash
uvicorn backend:app --reload --port 8000
```

You should see a message indicating the server is running at:

http://127.0.0.1:8000

### Step 2: Start the Frontend

Open a second terminal window, ensure your virtual environment is active, and run:

```bash
streamlit run app.py
```

This will automatically open the UI in your browser (usually at):

http://localhost:8501

## Usage Examples

Follow this workflow to test the application:

### 1. Ingest Knowledge Base

- Open the Streamlit UI.  
- Go to the sidebar.  
- Click **Browse files**.  
- Upload the provided assets:
  - `checkout.html`
  - `product_specs.md`
- Click **Upload & Build KB**.  
- Wait for the success message:  
  **"Knowledge Base built successfully."**

### 2. Generate Test Cases

- In the **Test Case Generator** section, enter a prompt such as:

```
Generate positive and negative test cases for the discount code feature.
```

- Click **Generate Test Cases**.  
- The system will display a JSON-structured test plan.

### 3. Generate Selenium Scripts

- Scroll to the **Selenium Script Generator** section.  
- Enter the target filename: `checkout.html`.  
- Select a specific test case (e.g., **Verify valid discount code**).  
- Click **Generate Selenium Script**.  

The agent will produce a runnable Python Selenium script.

### 4. Run the Script

- Copy the generated code.  
- Save it as a file named `run_test.py`.  
- Open a terminal and run:

```bash
python run_test.py
```

A Chrome browser will open and automatically execute the test.

## Explanation of Included Support Documents

### 1. `checkout.html` (Target Web Project)

This is the single-page web application being tested. It contains:

- HTML structure (IDs, Classes) for the agent to identify selectors.  
- JavaScript interaction logic (e.g., clicking **Pay Now** hides the form and shows a success message).  
- Input fields for:
  - Name  
  - Email  
  - Discount Code  
  - Shipping Method  
  - Payment Method  

### 2. `product_specs.md` (Support Document)

This document contains the authoritative business rules used by the agent as its **knowledge base**. It defines:

- Discount rules (e.g., **SAVE15** gives 15% off).  
- Shipping costs (Standard is free, Express is $10).  
- Validation requirements (Email must contain "@", Name is mandatory).  

The agent strictly references this file to avoid hallucinating functionality.  
Every generated test case includes a reference to this document.

## Technology Stack

- Python  
- FastAPI  
- Streamlit  
- Selenium  
- Groq LLM API  
- Retrieval-Augmented Generation (RAG)
