import streamlit as st
import requests
import base64
import json
import os
from pathlib import Path

# Set page config first - this must be the first Streamlit command
st.set_page_config(
    page_title="Token Counter",
    page_icon="🔢",
    layout="wide"
)

# Initialize session state for credentials
if 'api_host' not in st.session_state:
    st.session_state.api_host = os.getenv("API_HOST", "http://localhost:8000")
if 'api_username' not in st.session_state:
    st.session_state.api_username = os.getenv("API_USERNAME", "")
if 'api_password' not in st.session_state:
    st.session_state.api_password = os.getenv("API_PASSWORD", "")
if 'credentials_valid' not in st.session_state:
    st.session_state.credentials_valid = False

# Function to get auth header from session state
def get_auth_header():
    credentials = f"{st.session_state.api_username}:{st.session_state.api_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

# API interaction functions
def count_tokens(text, model):
    """Call the token counting API for a single text."""
    url = f"{st.session_state.api_host}/v1/tokens/count"
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
    url = f"{st.session_state.api_host}/v1/tokens/batch-count"
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

# Main app UI
st.title("🔢 Token Counter")
st.markdown("""
A tool for counting tokens in text for various AI models. 
This helps estimate token usage for OpenAI API calls.
""")

# Sidebar for API connection and credentials
with st.sidebar:
    st.title("API Connection")
    
    # API Host URL
    api_host = st.text_input(
        "API Host URL",
        value=st.session_state.api_host,
        help="The URL of the Token Counter API"
    )
    
    # API Credentials
    st.subheader("API Credentials")
    api_username = st.text_input("Username", value=st.session_state.api_username)
    api_password = st.text_input("Password", value=st.session_state.api_password, type="password")
    
    # Test connection button
    if st.button("Test Connection"):
        # Save values to session state
        st.session_state.api_host = api_host
        st.session_state.api_username = api_username
        st.session_state.api_password = api_password
        
        # Test connection
        try:
            response = requests.get(f"{api_host}/v1/health", headers=get_auth_header())
            if response.status_code == 200:
                st.success("✅ API Connected Successfully")
                st.session_state.credentials_valid = True
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.session_state.credentials_valid = False
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")
            st.session_state.credentials_valid = False
    
    # Models
    models = ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
    selected_model = st.selectbox("Select Model", models)
    
    # Security notice
    st.markdown("## Security & Privacy")
    st.info(
        "All text processing happens locally on your server. "
        "No data is sent to external services beyond your own API."
    )
    
    # How to Run instructions
    st.markdown("""
    ## How to Run
    ```bash
    cd /Users/chasedovey/Desktop/Tools/TokenCounter
    streamlit run frontend/app.py
    ```
    """)

# Check credentials before showing main UI
if not st.session_state.credentials_valid:
    st.warning("⚠️ Please enter valid API credentials in the sidebar and test the connection")
else:
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
