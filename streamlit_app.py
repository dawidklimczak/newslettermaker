import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from urllib.parse import urlparse
from streamlit_ace import st_ace

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Set up OpenAI client
client = OpenAI()

def get_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article = soup.find('article')
        if article:
            return article.get_text(strip=True)
        else:
            return None
    except Exception as e:
        st.error(f"Błąd podczas pobierania treści z {url}: {str(e)}")
        return None

def summarize_article(content):
    max_tokens = 4000
    truncated_content = content[:max_tokens]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś wnikliwym analitykiem i literatem, który koncentruje się na tworzeniu treści publicystycznych o wysokiej wartości literackiej. Twoim zadaniem jest generowanie zwięzłych, maksymalnie 500-znakowych podsumowań tekstów. Unikaj fraz typu 'artykuł jest o...' lub innych banałów. Stawiaj na przyciągające uwagę, inspirujące i merytoryczne opisy, które zaintrygują czytelnika i wciągną go w treść. Wszystko w języku polskim."},
            {"role": "user", "content": f"Na podstawie poniższego tekstu wygeneruj jego podsumowanie, które nie przekracza 500 znaków. Twórz atrakcyjny literacko opis w stylu publicystycznym, unikając wszelkich trywialnych sformułowań. Podsumowanie ma być angażujące, przemyślane i zachęcające do zgłębienia tematu, a jednocześnie precyzyjnie oddawać esencję tekstu.:\n\n{truncated_content}"}
        ]
    )
    return response.choices[0].message.content

def generate_title(content):
    max_tokens = 4000
    truncated_content = content[:max_tokens]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem, który generuje chwytliwe i informacyjne tytuły dla artykułów w języku polskim."},
            {"role": "user", "content": f"Wygeneruj chwytliwy i informacyjny tytuł dla tego artykułu w maksymalnie 10 słowach:\n\n{truncated_content}"}
        ]
    )
    return response.choices[0].message.content

def get_domain(url):
    return urlparse(url).netloc

def create_newsletter(titles, summaries, urls):
    newsletter_content = ""
    for title, summary, url in zip(titles, summaries, urls):
        domain = get_domain(url)
        newsletter_content += f"""
        <div style="background-color: white; margin-bottom: 20px; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h2 style="color: #2980b9; margin-top: 0;">{title}</h2>
            <p>{summary}</p>
            <p><a href="{url}" style="color: #e74c3c; text-decoration: none;">Przeczytaj cały artykuł</a></p>
            <p style="color: #7f8c8d; font-size: 0.9em;">Źródło: {domain}</p>
        </div>
        """

    newsletter_html = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Newsletter Tygodniowy</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .header {{
                background-color: #3498db;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Newsletter Tygodniowy</h1>
        </div>
        {newsletter_content}
    </body>
    </html>
    """
    return newsletter_html

def main():
    st.title('Generator Newslettera')

    # Input for article URLs
    article_urls = st.text_area("Adresy artykułów (jeden URL na linię):")
    
    if st.button("Pobierz treść artykułów"):
        urls = [url.strip() for url in article_urls.split('\n') if url.strip()]
        
        # Store the content in session state
        st.session_state.article_contents = {}
        
        for url in urls:
            with st.spinner(f'Pobieranie treści z: {url}'):
                content = get_article_content(url)
                st.session_state.article_contents[url] = content
        
        st.success("Treść artykułów pobrana. Sprawdź i edytuj w razie potrzeby.")

    if 'article_contents' in st.session_state:
        for url, content in st.session_state.article_contents.items():
            st.subheader(f"Treść dla: {url}")
            
            if content:
                edited_content = st.text_area(
                    "Sprawdź i edytuj treść artykułu:",
                    value=content,
                    height=300,
                    key=f"content_{url}"
                )
            else:
                edited_content = st.text_area(
                    "Nie udało się automatycznie pobrać treści. Wklej treść artykułu tutaj:",
                    height=300,
                    key=f"content_{url}"
                )
            
            st.session_state.article_contents[url] = edited_content
            st.markdown("---")  # Add a separator between articles
        
        if st.button("Generuj Newsletter"):
            summaries = []
            titles = []
            for url, content in st.session_state.article_contents.items():
                with st.spinner(f'Generowanie podsumowania i tytułu dla: {url}'):
                    summary = summarize_article(content)
                    title = generate_title(content)
                    summaries.append(summary)
                    titles.append(title)
            
            newsletter_html = create_newsletter(titles, summaries, st.session_state.article_contents.keys())
            
            # Display newsletter preview
            st.subheader("Podgląd newslettera")
            st.components.v1.html(newsletter_html, height=600, scrolling=True)
            
            # Display editable HTML code with syntax highlighting
            st.subheader("Kod HTML newslettera")
            st.markdown("Poniżej znajduje się edytowalny kod HTML newslettera. Możesz go modyfikować wedle potrzeb:")
            edited_html = st_ace(
                value=newsletter_html,
                language="html",
                theme="monokai",
                key="html_editor",
                height=400
            )
            
            if edited_html != newsletter_html:
                st.success("Kod HTML został zmodyfikowany. Możesz go teraz skopiować i użyć.")

if __name__ == "__main__":
    main()