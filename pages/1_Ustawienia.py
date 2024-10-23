import streamlit as st

st.title("Ustawienia")

# Initialize settings if not exists
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'model': 'gpt-3.5-turbo',
        'system_prompt_summary': """Jesteś wnikliwym analitykiem i literatem, który koncentruje się na tworzeniu treści publicystycznych o wysokiej wartości literackiej. Twoim zadaniem jest generowanie zwięzłych, maksymalnie 500-znakowych podsumowań tekstów. Unikaj fraz typu 'artykuł jest o...' lub innych banałów. Stawiaj na przyciągające uwagę, inspirujące i merytoryczne opisy, które zaintrygują czytelnika i wciągną go w treść. Wszystko w języku polskim.""",
        'user_prompt_summary': """Na podstawie poniższego tekstu wygeneruj jego podsumowanie, które nie przekracza 500 znaków. Twórz atrakcyjny literacko opis w stylu publicystycznym, unikając wszelkich trywialnych sformułowań. Podsumowanie ma być angażujące, przemyślane i zachęcające do zgłębienia tematu, a jednocześnie precyzyjnie oddawać esencję tekstu.""",
        'system_prompt_title': """Jesteś pomocnym asystentem, który generuje chwytliwe i informacyjne tytuły dla artykułów w języku polskim.""",
        'user_prompt_title': """Wygeneruj chwytliwy i informacyjny tytuł dla tego artykułu w maksymalnie 10 słowach."""
    }

# Model selection
st.header("Model OpenAI")
models = [
    'gpt-4',
    'gpt-4-0125-preview',
    'gpt-4-turbo-preview',
    'gpt-3.5-turbo'
]
selected_model = st.selectbox(
    "Wybierz model:",
    models,
    index=models.index(st.session_state.settings['model'])
)
st.session_state.settings['model'] = selected_model

# Prompts configuration
st.header("Konfiguracja promptów")

# Summary prompts
st.subheader("Prompty dla podsumowania")
with st.expander("System prompt dla podsumowania", expanded=True):
    system_prompt_summary = st.text_area(
        "Ten prompt definiuje rolę AI przy generowaniu podsumowań:",
        value=st.session_state.settings['system_prompt_summary'],
        height=200,
        key="system_prompt_summary"
    )
    st.session_state.settings['system_prompt_summary'] = system_prompt_summary

with st.expander("User prompt dla podsumowania", expanded=True):
    user_prompt_summary = st.text_area(
        "Ten prompt zawiera instrukcje dla każdego podsumowania:",
        value=st.session_state.settings['user_prompt_summary'],
        height=200,
        key="user_prompt_summary"
    )
    st.session_state.settings['user_prompt_summary'] = user_prompt_summary

# Title prompts
st.subheader("Prompty dla tytułów")
with st.expander("System prompt dla tytułu", expanded=True):
    system_prompt_title = st.text_area(
        "Ten prompt definiuje rolę AI przy generowaniu tytułów:",
        value=st.session_state.settings['system_prompt_title'],
        height=200,
        key="system_prompt_title"
    )
    st.session_state.settings['system_prompt_title'] = system_prompt_title

with st.expander("User prompt dla tytułu", expanded=True):
    user_prompt_title = st.text_area(
        "Ten prompt zawiera instrukcje dla każdego tytułu:",
        value=st.session_state.settings['user_prompt_title'],
        height=200,
        key="user_prompt_title"
    )
    st.session_state.settings['user_prompt_title'] = user_prompt_title

# Save settings button
if st.button("Zapisz ustawienia"):
    st.success("Ustawienia zostały zapisane!")
    st.balloons()

# Display current settings
with st.expander("Aktualne ustawienia", expanded=False):
    st.json(st.session_state.settings)