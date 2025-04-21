"""Graph RAG and analysis for UK Research and Innovation Funding (UKRI)."""

import logging
import streamlit as st
import networkx as nx
import utils.ukri_utils as ukri_utils  # pylint: disable=consider-using-from-import, import-error
import utils.ui_utils as ui_utils  # pylint: disable=consider-using-from-import, import-error

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Main function for rendering the UI of the streamlit application.
    """
    st.title("[UK Research and Innovation Funding (UKRI) Graph](https://www.ukri.org/)")

    tab1, tab2, tab3 = st.tabs(["Graph Data", "Sign Up", "Disclaimer"])

    with tab1:
        with st.form("search_projects_form"):
            search_term = st.text_input(
                "Search for projects here", key="search_projects_term"
            )
            number_of_results = st.slider("Number of results?", 100, 400, 200, 50)
            if st.form_submit_button("Submit"):
                with st.spinner("Getting data please wait"):
                    ukri_utils.search_ukri_workflow(search_term, number_of_results)

        if data := st.session_state.get("data"):
            graph = ukri_utils.create_networkx(data)
            annotated_node_data = ukri_utils.annotate_networkx_data(graph)
            ukri_utils.render_filter_form(annotated_node_data, graph)
            graph = nx.subgraph_view(graph, filter_node=ukri_utils.filter_node)
            ukri_utils.annotate_value_on_graph(graph)
            net = ukri_utils.convert_graph(graph)

            if (filter_determinant := st.session_state.get("filter")) and (
                filter_determinant == "Filter results"
            ):
                if st.session_state.get("search_nodes_label"):
                    graph_ui, graph_rag = st.tabs(["Render graph", "Graph RAG"])
                    with graph_ui:
                        if st.button("Render graph"):
                            with st.spinner("Rendering graph, please wait"):
                                ukri_utils.render_graphs(net)
                    with graph_rag:
                        ui_utils.render_graph_rag_interface(graph)
                        ui_utils.render_chat_results()
            else:
                if st.button("Render graph"):
                    with st.spinner("Rendering graph, please wait"):
                        ukri_utils.render_graphs(net)

    with tab2:
        st.components.v1.iframe(
            "https://docs.google.com/forms/d/e/1FAIpQLScMwyRLHUwc_qTqCPndJCudVQCn0zQl4upcHmqj26ZG5akl4g/viewform",
            height=2000,
            width=1000,
        )

    with tab3:
        st.write(
            """
            This software application is provided "as is" without warranty of any kind, either express or implied, including, but not limited to, the implied warranties of merchantability,
            fitness for a particular purpose, or non-infringement.
            The developer shall not be liable for any direct, indirect, incidental, special, consequential, or punitive damages arising out of or in connection with the use of or inability to use this software,
            even if advised of the possibility of such damages.
            Your use of this software is at your own risk.
            """
        )


if __name__ == "__main__":
    main()
