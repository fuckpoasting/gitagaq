from gitagqa.predict import retrieve
import logging
import streamlit as st
import streamlit.components.v1 as components
import time

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)


# Define functions
def generate_text():
    if not query:
        return
    logging.info(query)

    if len(query) == 0:
        st.session_state.text_error = "Have you considered typing something?"
        return

    if st.session_state.n_requests >= 5:
        st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another Tweet."
        logging.info(f"Session request limit reached: {st.session_state.n_requests}")
        st.session_state.n_requests = 1
        return

    result = retrieve(query)

    st.session_state.response = result.response
    st.session_state.relevant_prose = result.relevant_prose
    st.session_state.text_error = ""
    st.session_state.n_requests += 1
    st.session_state.response_loading = False


# Configure Streamlit page and state
st.set_page_config(page_title="gitagqa", page_icon="🤖")

if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0
if "response" not in st.session_state:
    st.session_state.response = ""
if "relevant_prose" not in st.session_state:
    st.session_state.relevant_prose = []
if "response_loading" not in st.session_state:
    st.session_state.response_loading = False


# Force responsive layout for columns also on mobile
st.write(
    """<style>
    [data-testid="column"] {
        width: calc(50% - 1rem);
        flex: 1 1 calc(50% - 1rem);
        min-width: calc(50% - 1rem);
    }
    </style>""",
    unsafe_allow_html=True,
)

# Render Streamlit page
st.title("GitaGQA")
st.markdown(
    "Built in 3 hrs. Shoot me a dm [@fuckpoasting](https://twitter.com/fuckpoasting) if it breaks, or you want to sponsor credits."
)


query = st.text_input(label="Don't you want to ask a question, anon?")
if st.session_state.text_error:
    st.warning(st.session_state.text_error)

st.button(label="Ask", on_click=generate_text)

if st.session_state.response:
    st.success(st.session_state.response)

if st.session_state.relevant_prose:
    st.header("Relevant Prose")

    for chap in st.session_state.relevant_prose:

        st.subheader(chap.title)
        st.markdown(chap.prose)
