"""Utilities for interacting with Langchain for Graph RAG."""

from langchain_community.chains.graph_qa.base import GraphQAChain
from langchain_community.graphs import NetworkxEntityGraph
from langchain_community.graphs.networkx_graph import KnowledgeTriple
from langchain_openai import ChatOpenAI
import utils.ui_utils as ui_utils  # pylint: disable=consider-using-from-import, import-error


def construct_graph_langchain(graph_nx, open_ai_api_key, question):
    """
    Construct a knowledge graph in Langchain and preform graph RAG.
    """
    graph = NetworkxEntityGraph()
    for node in graph_nx:
        graph.add_node(node)

    for subject_entity, object_entity in graph_nx.edges():
        predicate = graph_nx[subject_entity][object_entity].get("label", "relates to")
        graph.add_triple(KnowledgeTriple(subject_entity, predicate, object_entity))

    llm = ChatOpenAI(
        api_key=open_ai_api_key, model="gpt-4", temperature=0, max_retries=2
    )

    chain = GraphQAChain.from_llm(llm=llm, graph=graph, verbose=True)

    if response := chain.invoke({"query": question}):
        answer = response.get("result")
        ui_utils.add_result_to_state(question, answer)


if __name__ == "__main__":
    pass
