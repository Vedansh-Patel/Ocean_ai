import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("Autonomous QA Agent")
st.markdown("Ingest Docs -> Generate Test Cases -> Create Selenium Scripts")


with st.sidebar:
    st.header("1. Knowledge Base")
    uploaded_files = st.file_uploader("Upload Support Docs & HTML", accept_multiple_files=True)
    
    if st.button("Upload & Build KB"):
        if uploaded_files:
            files_payload = [('files', (file.name, file, file.type)) for file in uploaded_files]
            
            
            with st.spinner("Uploading..."):
                res = requests.post(f"{API_URL}/upload/", files=files_payload)
            
            if res.status_code == 200:
                st.success("Files Uploaded.")
                
                
                with st.spinner("Ingesting into Vector DB..."):
                    build_res = requests.post(f"{API_URL}/build-kb/")
                    if build_res.status_code == 200:
                        st.success(build_res.json()['message'])
            else:
                st.error("Upload failed.")
        else:
            st.warning("Please select files first.")


st.header("2. Test Case Generator")

query = st.text_input("Describe the scope (e.g., 'Generate tests for Discount Code feature')", value="Generate positive and negative test cases for the discount code feature.")

if st.button("Generate Test Cases"):
    with st.spinner("Analyzing documents..."):
        payload = {"query": query}
        response = requests.post(f"{API_URL}/generate-tests/", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state['test_cases'] = data.get('test_cases', [])
            st.session_state['raw_response'] = data.get('raw_text', "")
        else:
            st.error(f"Error: {response.text}")


if 'test_cases' in st.session_state and st.session_state['test_cases']:
    st.subheader("Generated Test Plan")
    st.json(st.session_state['test_cases'])
    
    
    html_file = st.text_input("Target HTML Filename", value="checkout.html")

    
    st.header("3. Selenium Script Generator")
    
    
    test_options = [f"{tc['Test_ID']}: {tc['Test_Scenario']}" for tc in st.session_state['test_cases']]
    selected_option = st.selectbox("Select a Test Case to Automate", test_options)
    
    if st.button("Generate Selenium Script"):
        
        selected_index = test_options.index(selected_option)
        selected_tc = st.session_state['test_cases'][selected_index]
        
        with st.spinner("Writing Python code..."):
            payload = {
                "test_case": selected_tc,
                "html_filename": html_file
            }
            script_res = requests.post(f"{API_URL}/generate-script/", json=payload)
            
            if script_res.status_code == 200:
                code = script_res.json()['script']
                
                code = code.replace("```python", "").replace("```", "")
                st.subheader("Generated Selenium Script")
                st.code(code, language='python')
            else:
                st.error("Failed to generate script.")

elif 'raw_response' in st.session_state:
    st.warning("Could not parse JSON structured output. Here is the raw response:")

    st.write(st.session_state['raw_response'])
