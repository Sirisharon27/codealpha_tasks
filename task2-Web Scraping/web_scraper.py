import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- WEBSITE CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Custom Book Data Scraper", page_icon="📚", layout="centered")

st.title("📚 Custom Web Dataset Generator")
st.write("This application scrapes live data from **Books to Scrape** (Mystery Category) and generates a downloadable custom dataset.")

st.markdown("---")

# --- STEP 1: CHOOSE DATA PREFERENCES ---
st.subheader("1. Configure Your Dataset")
max_books = st.slider("Select maximum number of books to extract:", min_value=5, max_value=20, value=10)

# --- STEP 2: THE SCRAPING PROCESS ---
st.subheader("2. Extract Live Data")

if st.button("🚀 Run Web Scraper", type="primary"):
    
    # Visual status loaders
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.text("Connecting to website server...")
    time.sleep(0.5)
    
    URL = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL, headers=headers)
        
        if response.status_code == 200:
            status_text.text("Connection successful! Parsing HTML structure...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            soup = BeautifulSoup(response.text, "html.parser")
            book_containers = soup.find_all("article", class_="product_pod")
            
            scraped_books = []
            status_text.text("Navigating HTML tags and extracting specific metrics...")
            
            # Loop through books up to the user-defined slider limit
            for i, book in enumerate(book_containers[:max_books]):
                title = book.h3.a["title"]
                price = book.find("p", class_="price_color").text.strip()
                availability = book.find("p", class_="instock availability").text.strip()
                
                scraped_books.append({
                    "Book Title": title,
                    "Price (GBP)": price,
                    "Availability Status": availability
                })
                
                # Update progress bar dynamically
                percent_complete = 30 + int((i + 1) / len(book_containers[:max_books]) * 70)
                progress_bar.progress(percent_complete)
                time.sleep(0.1) # Simulate scraping buffer
                
            status_text.text("Transformation complete! Structuring data...")
            
            # Convert to Pandas DataFrame
            df = pd.DataFrame(scraped_books)
            
            # Clear progress text on completion
            status_text.success(f"Successfully generated a custom dataset with {len(df)} records!")
            
            # --- STEP 3: DISPLAY AND DOWNLOAD ---
            st.markdown("### 📊 Preview Generated Dataset")
            st.dataframe(df, use_container_width=True)
            
            # Convert DataFrame to CSV bytes for download button
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Custom CSV Dataset",
                data=csv_data,
                file_name="custom_mystery_books.csv",
                mime="text/csv"
            )
            
        else:
            status_text.error(f"Failed to fetch website data. HTTP Error: {response.status_code}")
            
    except Exception as e:
        status_text.error(f"An unexpected error occurred: {e}")