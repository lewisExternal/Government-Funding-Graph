"""Utilities for Streamlit UI components."""

# pylint: disable = unused-import
import re
import streamlit as st
import utils.llama_index_utils as llama_index_utils  # pylint: disable=consider-using-from-import, import-error
import utils.config as config  # pylint: disable=consider-using-from-import, import-error
import utils.langchain_utils as langchain_utils  # pylint: disable=consider-using-from-import, import-error


def add_result_to_state(question, response):
    """
    Add model output to state.
    """
    if response:
        graph_answers = st.session_state.get("graph_answers") or []
        graph_answers.append((question, response))
        st.session_state["graph_answers"] = graph_answers
    else:
        st.error("Query failed, please try again later.", icon="⚠️")


def render_chat_results():
    """
    Render chat interface from state.
    """
    if graph_answers := st.session_state.get("graph_answers"):
        for question, result in graph_answers:
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("Assistant"):
                st.write(result)
        if st.button("Delete chat history"):
            del st.session_state["graph_answers"]
            st.rerun()


def render_graph_rag_interface(graph):
    """
    Render interface for Graph RAG.
    """
    open_ai_api_key = st.text_input("Enter Open AI API key", type="password")

    if open_ai_api_key:

        query_engine = llama_index_utils.init_llama_index_graph(graph, open_ai_api_key)
        entity_str = ", ".join(st.session_state.get("search_nodes_label", []))
        options = [
            re.sub(r"(\(.*?\))", "", question.replace("[entity]", entity_str))
            for question in config.SAMPLE_QUESTIONS
        ] + ["Other option..."]
        if question := st.selectbox(
            "Question from template:",
            options=options,
        ):
            value = "" if question == "Other option..." else question

        with st.form("search_rag_form"):
            final_question = st.text_input("Type your query:", value=value)

            if st.form_submit_button("Submit") and final_question:
                with st.spinner("Ask Question"):

                    if question:
                        # langchain_utils.construct_graph_langchain(graph, open_ai_api_key, question)
                        llama_index_utils.query_llama_index_graph(
                            query_engine, final_question
                        )
                    else:
                        st.toast("Please submit a question")


if __name__ == "__main__":
    pass
