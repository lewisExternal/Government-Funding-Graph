"""Utilities for interacting with Llama Index for Graph RAG."""

from llama_index.core import KnowledgeGraphIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, MessageRole
import streamlit as st
import utils.ui_utils as ui_utils  # pylint: disable=consider-using-from-import, import-error


def init_llama_index_graph(graph_nx, open_ai_api_key):
    """
    Construct a knowledge graph using llama index.
    """
    llm = OpenAI(model="gpt-3.5-turbo", api_key=open_ai_api_key)
    embed_model = OpenAIEmbedding(api_key=open_ai_api_key)

    graph = KnowledgeGraphIndex(
        [], llm=llm, embed_model=embed_model, api_key=open_ai_api_key
    )

    for subject_entity, object_entity in graph_nx.edges():
        predicate = graph_nx[subject_entity][object_entity].get("label", "relates to")
        graph.upsert_triplet_and_node(
            (subject_entity, predicate, object_entity), TextNode(text=subject_entity)
        )
        graph.upsert_triplet_and_node(
            (object_entity, predicate, subject_entity), TextNode(text=subject_entity)
        )

    chat_engine = graph.as_chat_engine(
        include_text=True,
        response_mode="tree_summarize",
        embedding_mode="hybrid",
        similarity_top_k=5,
        verbose=True,
        llm=llm,
    )

    return chat_engine


def query_llama_index_graph(query_engine, question):
    """
    Query llama index knowledge graph using graph RAG.
    """
    graph_answers = st.session_state.get("graph_answers", [])
    chat_history = []
    for query, answer in graph_answers:
        chat_history.append(ChatMessage(role=MessageRole.USER, content=query))
        chat_history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=answer)
        )

    if response := query_engine.chat(question, chat_history):
        ui_utils.add_result_to_state(question, response.response)


if __name__ == "__main__":
    pass
