import streamlit as st
import os
import pandas as pd
from pdf_utils import extract_toc_images, write_toc_to_pdf
from ocr_service import extract_toc_from_images

st.set_page_config(page_title="PDF TOC Generator", layout="wide")

st.title("PDF Directory Generator")
st.markdown("Upload a PDF, extract the Table of Contents using AI, edit it, and save it back to the PDF.")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("OpenAI API Key", type="password")
    base_url = st.text_input("API Base URL", value="https://ai.hybgzs.com/v1")
    model_name = st.text_input("Model Name", value="gpt-4o")
    
    st.header("Help")
    st.markdown("""
    **Offset Calculation:**
    If the text "Page 1" in the book is actually on the 10th page of the PDF file:
    Offset = 10 - 1 = 9.
    """)

# Main Content
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file and api_key:
    # Save uploaded file strictly to a temp path to handle it with fitz
    temp_path = "temp_input.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success("File uploaded successfully!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        toc_page_input = st.text_input("TOC Page Numbers (e.g., 5-8, 10)", help="The PDF page numbers where the directory checks are located.")
        
    with col2:
        page_offset = st.number_input("Page Offset", value=0, help="PDF Page Number - Printed Page Number")
        
    with col3:
        st.write("") # Spacer
        st.write("")
        extract_btn = st.button("Extract TOC from PDF")

    # Session State for TOC Data
    if "toc_data" not in st.session_state:
        st.session_state.toc_data = []

    if extract_btn:
        if not toc_page_input:
            st.error("Please enter TOC page numbers.")
        else:
            # Parse page numbers
            try:
                pages = []
                parts = toc_page_input.split(',')
                for part in parts:
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        pages.extend(range(start, end + 1))
                    else:
                        pages.append(int(part))
                
                with st.spinner("Rendering pages and extracting text with AI..."):
                    images = extract_toc_images(temp_path, pages)
                    if not images:
                        st.error("No images rendered. Check page numbers.")
                    else:
                        st.subheader("Preview of TOC Pages")
                        st.image(images, width=200, caption=[f"Page {p}" for p in pages])
                        
                        extracted_data = extract_toc_from_images(images, api_key, base_url, model_name)
                        if extracted_data:
                            st.session_state.toc_data = extracted_data
                            st.success(f"Extracted {len(extracted_data)} items!")
                        else:
                            st.error("AI returned no data.")
                            
            except ValueError:
                st.error("Invalid page format. Use '5-8' or '5,6,7'.")

    # Editable DataFrame
    if st.session_state.toc_data:
        st.subheader("Edit TOC")
        
        df = pd.DataFrame(st.session_state.toc_data)
        
        # Ensure correct column types
        if 'level' not in df.columns: df['level'] = 1
        if 'title' not in df.columns: df['title'] = ""
        if 'page' not in df.columns: df['page'] = 0
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "level": st.column_config.NumberColumn("Level", min_value=1, max_value=5, step=1),
                "title": st.column_config.TextColumn("Title"),
                "page": st.column_config.NumberColumn("Page Number")
            },
            width="stretch"
        )
        
        if st.button("Write TOC to PDF"):
            output_path = "output_with_toc.pdf"
            toc_list = edited_df.to_dict('records')
            
            try:
                write_toc_to_pdf(temp_path, toc_list, int(page_offset), output_path)
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download PDF with TOC",
                        data=f,
                        file_name="processed_document.pdf",
                        mime="application/pdf"
                    )
                st.success("TOC written successfully! Click above to download.")
                
            except Exception as e:
                st.error(f"Failed to write PDF: {e}")
