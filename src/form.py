import time
import streamlit as st

from retrieve import qa_bot


# def qa_bot(prompt):
#     time.sleep(2)
#     return f"You asked : {prompt}"


def main():
    st.title("FAQ Genie")

    courses = [
        "data-engineering-zoomcamp",
        "machine-learning-zoomcamp",
        "mlops-zoomcamp",
    ]

    selected_course_option = st.selectbox(
        "Select a zoomcamp", options=courses, help="As of July 2024"
    )

    with st.form(key="rag_form"):
        prompt = st.text_input("What is your question?")
        response_placeholder = st.empty()

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        response_placeholder.markdown("Loading...")
        response = qa_bot(prompt, selected_course_option)
        response_placeholder.markdown(response)


if __name__ == "__main__":
    main()
