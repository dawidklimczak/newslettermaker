import streamlit as st

st.set_page_config(
    page_title="Newsletter Generator",
    page_icon="📰",  # Ikona gazety
    menu_items={
        "Get Help": "mailto:dawid.klimczak@forum-media.pl",
        "Report a bug": "mailto:dawid.klimczak@forum-media.pl",
        'About': 'Generator newslettera'
    }
)

hide_st_app_toolbar = """
    <style>
    [data-testid="stAppToolbar"] {
        visibility: hidden;
    }
    </style>
    """

st.markdown(hide_st_app_toolbar, unsafe_allow_html=True)


import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from urllib.parse import urlparse
from streamlit_ace import st_ace
from streamlit_quill import st_quill

# Set default settings if not exist
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'model': 'gpt-3.5-turbo',
        'system_prompt_summary': """Jesteś wnikliwym analitykiem i literatem, który koncentruje się na tworzeniu treści publicystycznych o wysokiej wartości literackiej. Twoim zadaniem jest generowanie zwięzłych, maksymalnie 500-znakowych podsumowań tekstów. Unikaj fraz typu 'artykuł jest o...' lub innych banałów. Stawiaj na przyciągające uwagę, inspirujące i merytoryczne opisy, które zaintrygują czytelnika i wciągną go w treść. Wszystko w języku polskim.""",
        'user_prompt_summary': """Na podstawie poniższego tekstu wygeneruj jego podsumowanie, które nie przekracza 500 znaków. Twórz atrakcyjny literacko opis w stylu publicystycznym, unikając wszelkich trywialnych sformułowań. Podsumowanie ma być angażujące, przemyślane i zachęcające do zgłębienia tematu, a jednocześnie precyzyjnie oddawać esencję tekstu.""",
        'system_prompt_title': """Jesteś pomocnym asystentem, który generuje chwytliwe i informacyjne tytuły dla artykułów w języku polskim.""",
        'user_prompt_title': """Wygeneruj chwytliwy i informacyjny tytuł dla tego artykułu w maksymalnie 10 słowach."""
    }

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
        model=st.session_state.settings['model'],
        messages=[
            {"role": "system", "content": st.session_state.settings['system_prompt_summary']},
            {"role": "user", "content": f"{st.session_state.settings['user_prompt_summary']}:\n\n{truncated_content}"}
        ]
    )
    return response.choices[0].message.content

def generate_title(content):
    max_tokens = 4000
    truncated_content = content[:max_tokens]
    
    response = client.chat.completions.create(
        model=st.session_state.settings['model'],
        messages=[
            {"role": "system", "content": st.session_state.settings['system_prompt_title']},
            {"role": "user", "content": f"{st.session_state.settings['user_prompt_title']}:\n\n{truncated_content}"}
        ]
    )
    return response.choices[0].message.content

def clean_quill_content(html_content):
    """
    Usuwa zewnętrzne tagi <p> zachowując formatowanie wewnętrzne
    """
    if not html_content:
        return ""
    if html_content.startswith('<p>') and html_content.endswith('</p>'):
        return html_content[3:-4]  # usuwa pierwsze <p> i ostatnie </p>
    return html_content

def get_domain(url):
    return urlparse(url).netloc

def create_newsletter(titles, summaries, urls):
    total_news = len(titles)  # Suma wszystkich newsów
    
    newsletter_content = ""
    for index, (title, summary, url) in enumerate(zip(titles, summaries, urls), 1):  # start=1 zaczyna liczenie od 1
        domain = get_domain(url)
        # Czyszczenie tytułu i podsumowania z tagów <p>
        cleaned_title = clean_quill_content(title)
        cleaned_summary = clean_quill_content(summary)
        newsletter_content += f"""
<tr>
  <td align="left" class="es-p20t es-p20r es-p20l esd-structure">
  <table cellpadding="0" cellspacing="0" align="right" class="es-right">
    <tbody>
      <tr>
        <td width="560" align="left" class="es-m-p20b esd-container-frame">
          <table cellpadding="0" cellspacing="0" width="100%">
            <tbody>
              <tr>
                <td align="center" class="esd-block-text">
                  <p style="font-size:12px">
                    <em>{index}/{total_news}</em>
                  </p>
                </td>
              </tr>
              <tr>
                <td align="left" class="esd-block-text es-p10t es-p10b">
                  <h3 class="b_title" style="font-size:25px;line-height:100%;font-family:georgia,times,&#39;times new roman&#39;,serif">
                    {cleaned_title}
                  </h3>
                </td>
              </tr>
              <tr>
                <td align="left" class="esd-block-text es-m-p10b">
                  <p class="b_description es-m-txt-l" style="font-size:14px;line-height:150%">
                    {cleaned_summary}
                  </p>
                </td>
              </tr>
              <tr>
                <td align="right" class="esd-block-button">
                  <span class="es-button-border es-m-il es-button-border-7748" style="background:#fad02c;border:1px solid #fad02c">
                    <a href="{url}" target="_blank" class="es-button es-button-7808" style="font-size:14px;font-family:arial,&#39;helvetica neue&#39;,helvetica,sans-serif;background:#fad02c;mso-border-alt:10px solid #fad02c;font-weight:bold">
                      Przejdź do artykułu
                    </a>
                  </span>
                </td>
              </tr>
              <tr>
                <td align="left" class="esd-block-text es-p5t es-text-9242">
                  <p class="b_description es-text-mobile-size-14 es-m-txt-l" style="font-size:14px;line-height:150%;color:#999999">
                    <em>Źródło: {domain}</em>
                  </p>
                </td>
              </tr>
              <tr>
                <td align="center" class="esd-block-spacer es-p20" style="font-size:0">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%" height="100%" class="es-spacer">
                    <tbody>
                      <tr>
                        <td style="width:100%;margin:0px 0px 0px 0px;border-bottom:1px solid #cccccc;background:none;height:1px"></td>
                      </tr>
                    </tbody>
                  </table>
                </td>
              </tr>
            </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table>
</td>
</tr>
        """

    # Teraz całość opakujemy w tabelę główną
    newsletter_html = f"""
    <td align="center" class="esd-stripe">
  <table bgcolor="#ffffff" align="center" cellpadding="0" cellspacing="0" width="600" class="es-content-body">
    <tbody>
            {newsletter_content}
        </tbody>
    </table>
    </td>
    """
    return newsletter_html

def main():
    st.title('Generator Newslettera')

    # Initialize session state variables if they don't exist
    if 'summaries' not in st.session_state:
        st.session_state.summaries = {}
    if 'titles' not in st.session_state:
        st.session_state.titles = {}
    if 'regenerate_url' not in st.session_state:
        st.session_state.regenerate_url = None

    # Display current model
    st.sidebar.markdown(f"**Aktualny model:** {st.session_state.settings['model']}")

    # Input for article URLs
    article_urls = st.text_area("Adresy artykułów (jeden URL na linię):")
    
    if st.button("Pobierz treść artykułów"):
        urls = [url.strip() for url in article_urls.split('\n') if url.strip()]
        
        # Store the content in session state
        st.session_state.article_contents = {}
        # Clear previous summaries and titles
        st.session_state.summaries = {}
        st.session_state.titles = {}
        
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
            st.markdown("---")

        if st.button("Generuj podsumowania"):
            for url, content in st.session_state.article_contents.items():
                with st.spinner(f'Generowanie podsumowania i tytułu dla: {url}'):
                    st.session_state.summaries[url] = summarize_article(content)
                    st.session_state.titles[url] = generate_title(content)

            st.success("Podsumowania wygenerowane. Możesz je teraz edytować.")

        # Display editable summaries if they exist
        if st.session_state.summaries or st.session_state.titles:
            st.header("Edycja podsumowań")
            
            for url in st.session_state.article_contents.keys():
                st.subheader(f"Podsumowanie dla: {url}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Editable title with rich text editor
                    st.markdown("### Tytuł:")
                    default_title = st.session_state.titles.get(url, "")
                    edited_title = st_quill(
                        value=default_title,
                        html=True,
                        key=f"edit_title_{url}"
                    )
                    st.session_state.titles[url] = clean_quill_content(edited_title) 

                    # Editable summary with rich text editor
                    st.markdown("### Podsumowanie:")
                    default_summary = st.session_state.summaries.get(url, "")
                    edited_summary = st_quill(
                        value=default_summary,
                        html=True,
                        key=f"edit_summary_{url}"
                    )
                    st.session_state.summaries[url] = clean_quill_content(edited_summary)

                with col2:
                    # Regenerate button for this specific summary
                    if st.button("Wygeneruj ponownie", key=f"regenerate_{url}"):
                        st.session_state.regenerate_url = url
                        st.rerun()

                # Handle regeneration for this specific URL
                if st.session_state.regenerate_url == url:
                    with st.spinner("Generuję nowe podsumowanie..."):
                        content = st.session_state.article_contents[url]
                        new_summary = summarize_article(content)
                        new_title = generate_title(content)
                        st.session_state.summaries[url] = new_summary
                        st.session_state.titles[url] = new_title
                        st.session_state.regenerate_url = None
                        st.rerun()

                st.markdown("---")

            # Generate final newsletter button
            if st.button("Generuj końcowy newsletter"):
                if all(url in st.session_state.summaries and url in st.session_state.titles 
                       for url in st.session_state.article_contents.keys()):
                    newsletter_html = create_newsletter(
                        [st.session_state.titles[url] for url in st.session_state.article_contents.keys()],
                        [st.session_state.summaries[url] for url in st.session_state.article_contents.keys()],
                        st.session_state.article_contents.keys()
                    )
                    
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
                else:
                    st.warning("Najpierw wygeneruj podsumowania dla wszystkich artykułów.")

if __name__ == "__main__":
    main()