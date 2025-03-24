import streamlit as st
import requests
import base64
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set page config first - this must be the first Streamlit command
st.set_page_config(
    page_title="Token Counter",
    page_icon="🔢",
    layout="wide"
)

# Try to load environment variables from the top-level .env file
try:
    # Get the directory containing this script
    current_dir = Path(__file__).parent
    # Go up one level to the project root
    project_root = current_dir.parent
    # Load the .env file from the project root
    load_dotenv(project_root / ".env")
except Exception:
    # In Docker, we'll use environment variables directly
    pass

# API Configuration
API_HOST = os.getenv("API_HOST", "http://localhost:8000")
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "securepassword")

# Debug info - can be removed after confirming it works
st.sidebar.markdown("### Debug Info")
debug_info = f"""
- API_HOST: {API_HOST}
- API_USERNAME: {API_USERNAME}
- API_PASSWORD: {"*" * len(API_PASSWORD)}
"""
with st.sidebar.expander("Configuration"):
    st.code(debug_info)

# Basic auth header
def get_auth_header():
    credentials = f"{API_USERNAME}:{API_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

def count_tokens(text, model):
    """Call the token counting API for a single text."""
    url = f"{API_HOST}/v1/tokens/count"
    payload = {
        "text": text,
        "model": model
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_auth_header())
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    
    return None

def batch_count_tokens(texts, model):
    """Call the batch token counting API."""
    url = f"{API_HOST}/v1/tokens/batch-count"
    payload = {
        "texts": [{"text": text, "text_id": f"text{i+1}"} for i, text in enumerate(texts)],
        "model": model
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_auth_header())
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    
    return None

# App UI
st.title("🔢 Token Counter")
st.markdown("""
A tool for counting tokens in text for various AI models. 
This helps estimate token usage for OpenAI API calls.
""")

# Add a security note
st.sidebar.markdown("## Security & Privacy")
st.sidebar.info(
    "All text processing happens locally on your server. "
    "No data is sent to external services beyond your own API."
)

# API Connection Status
try:
    response = requests.get(f"{API_HOST}/v1/health")
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.error("❌ API Not Connected")

# Models
models = ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
selected_model = st.sidebar.selectbox("Select Model", models)

# Tabs for single text vs batch
tab1, tab2 = st.tabs(["Single Text", "Batch Processing"])

# Single text tab
with tab1:
    st.header("Count Tokens in Text")
    
    user_text = st.text_area(
        "Enter text to count tokens", 
        height=200,
        placeholder="Type or paste your text here..."
    )
    
    if st.button("Count Tokens", key="single_count"):
        if user_text.strip():
            with st.spinner("Counting tokens..."):
                result = count_tokens(user_text, selected_model)
                
                if result:
                    st.success(f"Text contains {result['token_count']} tokens")
                    
                    # Results in expandable section
                    with st.expander("View Full Results"):
                        st.json(result)
                        
                    # Visualization
                    st.metric("Token Count", result['token_count'])
                    st.metric("Processing Time (ms)", result['processing_time_ms'])
        else:
            st.warning("Please enter some text")

# Batch processing tab
with tab2:
    st.header("Batch Token Counting")
    
    # Add instructions
    st.markdown("""
    Enter multiple texts, one per line. Each line will be processed as a separate text.
    """)
    
    batch_text = st.text_area(
        "Enter multiple texts (one per line)",
        height=200,
        placeholder="Text 1\nText 2\nText 3"
    )
    
    if st.button("Process Batch", key="batch_count"):
        if batch_text.strip():
            # Split by lines and remove empty lines
            texts = [line for line in batch_text.split('\n') if line.strip()]
            
            if texts:
                with st.spinner(f"Processing {len(texts)} texts..."):
                    results = batch_count_tokens(texts, selected_model)
                    
                    if results and 'results' in results:
                        st.success(f"Processed {len(results['results'])} texts")
                        
                        # Create a dataframe for better visualization
                        import pandas as pd
                        df = pd.DataFrame([
                            {
                                "Text ID": r.get("text_id", f"text{i+1}"),
                                "Text": texts[i][:50] + "..." if len(texts[i]) > 50 else texts[i],
                                "Token Count": r["token_count"],
                                "Processing Time (ms)": r["processing_time_ms"]
                            }
                            for i, r in enumerate(results['results'])
                        ])
                        
                        st.dataframe(df)
                        
                        # Total tokens
                        total_tokens = sum(r["token_count"] for r in results['results'])
                        st.metric("Total Tokens", total_tokens)
                        
                        # Full results in expandable section
                        with st.expander("View Raw API Results"):
                            st.json(results)
            else:
                st.warning("No valid texts found. Please enter at least one text.")
        else:
            st.warning("Please enter some texts")

# Add instructions for running the app
st.sidebar.markdown("""
## How to Run
```bash
cd /Users/chasedovey/Desktop/Tools/TokenCounter
streamlit run frontend/app.py
```
""")

# Generated by Copilot
