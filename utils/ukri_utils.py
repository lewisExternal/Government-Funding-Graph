"""Utilities for interacting with UKRI data via their API and graph creation."""

import contextlib
import os
from itertools import chain
import math
import concurrent.futures
import uuid
import urllib.parse
import logging
import requests
from pyvis.network import Network
import networkx as nx
import streamlit as st
import utils.config as config  # pylint: disable=consider-using-from-import, import-error


def search_ukri_projects(args):
    """
    Search UKRI projects based on a search term page size and page number.
    More details can be found here: https://gtr.ukri.org/resources/api.html
    """
    search_term, page_size, page_number = args
    try:
        encoded_search_term = urllib.parse.quote(search_term)
        if (
            (
                response := requests.get(
                    f"https://gtr.ukri.org/api/search/project?term={encoded_search_term}&page={page_number}&fetchSize={page_size}&selectedSortableField=pro.am&selectedSortOrder=DESC&selectedFacets=&fields=project.abs",
                    timeout=10,
                )
            )
            and (response.status_code == 200)
            and (
                items := response.json()
                .get("facetedSearchResultBean", {})
                .get("results")
            )
        ):
            return items
    except Exception as error:
        logging.exception("ERROR search_ukri_projects: %s", error)
    return []


def search_ukri_paginate(search_term, number_of_results, page_size=100):
    """
    Asynchronous pagination requests for project lookup.
    """
    args = [
        (search_term, page_size, page_number + 1)
        for page_number in range(int(math.ceil(number_of_results / page_size)))
    ]
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        future = executor.map(search_ukri_projects, args)
    results = [result for result in future if result]
    return list(chain.from_iterable(results))[:number_of_results]


def parse_data(projects):
    """
    Parse project data into a usable format and validate.
    """
    data = []
    for project in projects:
        project_composition = project.get("projectComposition", {})
        project_data = project_composition.get("project", {})
        fund = project_data.get("fund", {})
        funder = fund.get("funder")
        value_pounds = fund.get("valuePounds")
        lead_research_organisation = project_composition.get("leadResearchOrganisation")
        person_roles = project_composition.get("personRoles")
        if all(
            [
                project_composition,
                project_data,
                fund,
                funder,
                value_pounds,
                lead_research_organisation,
            ]
        ):
            record = {}
            record["funder_name"] = funder.get("name")
            record["funder_link"] = funder.get("resourceUrl")
            record["project_title"] = project_data.get("title")
            record["project_grant_reference"] = project_data.get("grantReference")
            record["value"] = value_pounds
            record["lead_research_organisation"] = lead_research_organisation.get(
                "name", ""
            )
            record["lead_research_organisation_link"] = lead_research_organisation.get(
                "resourceUrl", ""
            )
            record["people"] = person_roles
            record["project_url"] = project_data.get("resourceUrl")
            data.append(record)
    return data


def get_ukri_project_data(project_grant_reference):
    """
    Search UKRI project data based on grant reference.
    """
    try:
        if (
            (
                response := requests.get(
                    f"https://gtr.ukri.org/api/projects?ref={project_grant_reference}",
                    timeout=10,
                )
            )
            and (response.status_code == 200)
            and (items := response.json().get("projectOverview", {}))
        ):
            return items
    except Exception as error:
        logging.exception("ERROR get_ukri_project_data: %s", error)
    return []


def get_project_data(data):
    """
    Asynchronously lookup project data.
    """
    args = list(
        {
            project.get("project_grant_reference")
            for project in data
            if project.get("project_grant_reference")
        }
    )
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        future = executor.map(get_ukri_project_data, args)
    results = [result for result in future if result]
    return {
        project.get("projectComposition", {})
        .get("project", {})
        .get("grantReference"): project
        for project in results
    }


def search_ukri_workflow(search_term, number_of_results):
    """
    Main workflow for searching UKRI data from a search term and limited by the number of search results.
    The results are then saved to state.
    """
    if (
        (projects := search_ukri_paginate(search_term, number_of_results))
        and (data := parse_data(projects))
        and (project_data_lookup := get_project_data(data))
    ):
        augmented_data = [
            {
                **project,
                **{
                    "project_data_lookup": project_data_lookup.get(
                        project.get("project_grant_reference", ""), {}
                    )
                },
            }
            for project in data
        ]
        st.session_state["data"] = augmented_data
    else:
        st.error("Request failed, please try again later.", icon="⚠️")


def get_link_html(link, text):
    """
    Helper function to construct a HTML link.
    """
    return f"""<a href="{link}" target="_blank">{text}</a>"""


def render_graphs(net):
    """
    Helper to render graph visualization from pyvis graph.
    """
    uuid4 = uuid.uuid4()
    file_name = f"./output/{uuid4}.html"
    with contextlib.suppress(FileNotFoundError):
        os.remove(file_name)
    net.save_graph(file_name)
    with open(file_name, "r", encoding="utf-8") as html_file:
        source_code = html_file.read()
    st.components.v1.html(source_code, height=650, width=650)
    os.remove(file_name)


def set_networkx_attribute(graph, node_label, attribute_name, value):
    """
    Helper to set attribute for networkx graph.
    """
    attrs = {node_label: {attribute_name: value}}
    nx.set_node_attributes(graph, attrs)


def append_networkx_value(graph, node_label, attribute_name, value):
    """
    Helper to append value to current node attribute scalar value.
    """
    current_map = nx.get_node_attributes(graph, attribute_name, default=0)
    current_value = current_map[node_label]
    current_value = current_value + value
    set_networkx_attribute(graph, node_label, attribute_name, current_value)


def calculate_total_funding_from_group(graph, group):
    """
    Helper to calculate total funding for a group.
    """
    return sum(
        [
            data.get("funding")
            for node_label, data in graph.nodes(data=True)
            if data.get("funding") and data.get("group") == group
        ]
    )


def set_weighted_size_helper(graph, node_label, totals, data):
    """
    Create normalized weights based on percentage funding amount.
    """
    if (
        (group := data.get("group"))
        and (total_funding := totals.get(group))
        and (funding := data.get("funding"))
    ):
        div = funding / total_funding
        funding_percentage = math.ceil(((100.0 * div)))
        set_networkx_attribute(graph, node_label, "size", funding_percentage)


def annotate_value_on_graph(graph):
    """
    Calculate normalized graph sizes and append to title.
    """
    totals = {}
    for group in ["lead_research_organisation", "funder_name"]:
        totals[group] = calculate_total_funding_from_group(graph, group)

    for node_label, data in graph.nodes(data=True):
        if (
            (funding := data.get("funding"))
            and (group := data.get("group"))
            and (title := data.get("title"))
        ):
            new_title = f"{title} | {'£ {:,.0f}'.format(funding)}"
            if total_funding := totals.get(group):
                div = funding / total_funding
                funding_percentage = math.ceil(((100.0 * div)))
                set_networkx_attribute(
                    graph,
                    node_label,
                    "size",
                    config.NODE_SIZE_SCALE_FACTOR * funding_percentage,
                )
                new_title += f" | {' {:,.0f}'.format(funding_percentage)} %"

            set_networkx_attribute(graph, node_label, "title", new_title)


def add_project_orgs(graph, project_data_lookup, project_title):
    """
    Add project organizations to graph.
    """
    organisation_roles = project_data_lookup.get("projectComposition", {}).get(
        "organisationRoles", []
    )
    for org in organisation_roles:
        org_name = org.get("name")
        org_link = org.get("resourceUrl")
        if not graph.has_node(org_name):
            link_html = get_link_html(org_link.replace("api/", ""), org_name)
            graph.add_node(org_name, title=link_html, group="organisation", size=50)
        for role in org.get("roles", []):
            role_name = role.get("name")
            if not graph.has_edge(org_name, project_title):
                graph.add_edge(org_name, project_title, title=role_name)


def create_networkx(data):
    """
    Create networkx graph from UKRI data.
    """
    graph = nx.DiGraph()
    for row in data:
        if (
            (funder_name := row.get("funder_name"))
            and (project_title := row.get("project_title"))
            and (lead_research_organisation := row.get("lead_research_organisation"))
        ):

            project_data_lookup = row.get("project_data_lookup", {})

            # TODO remove, too many nodes.
            # add_project_orgs(graph, project_data_lookup, project_title)

            if not graph.has_node(funder_name):
                graph.add_node(
                    funder_name, title=funder_name, group="funder_name", size=100
                )
            if not graph.has_node(project_title):
                link_html = get_link_html(
                    row.get("project_url", "").replace("api/", ""), project_title
                )
                graph.add_node(
                    project_title,
                    title=link_html,
                    group="project_title",
                    project_data_lookup=project_data_lookup,
                    size=25,
                )
            if not graph.has_edge(funder_name, project_title):
                graph.add_edge(
                    funder_name,
                    project_title,
                    value=row.get("value"),
                    title=f"{'£{:,.2f}'.format(row.get('value'))}",
                    label=f"{'£{:,.2f}'.format(row.get('value'))}",
                )

        if not graph.has_node(lead_research_organisation):
            link_html = get_link_html(
                row.get("lead_research_organisation_link").replace("api/", ""),
                lead_research_organisation,
            )
            graph.add_node(
                lead_research_organisation,
                title=link_html,
                group="lead_research_organisation",
                size=50,
            )
        if not graph.has_edge(lead_research_organisation, project_title):
            graph.add_edge(
                lead_research_organisation, project_title, title="RELATES TO"
            )

        append_networkx_value(graph, funder_name, "funding", row.get("value", 0))
        append_networkx_value(graph, project_title, "funding", row.get("value", 0))
        append_networkx_value(
            graph, lead_research_organisation, "funding", row.get("value", 0)
        )

        # TODO Too many nodes are added if all relations are added
        person_roles = row.get(
            "people", []
        )  # + project_data_lookup.get("projectComposition").get("personRoles",[])

        for person in person_roles:
            if (
                (person_name := person.get("fullName"))
                and (person_link := person.get("resourceUrl"))
                and (project_title := row.get("project_title"))
                and (roles := person.get("roles"))
            ):
                if not graph.has_node(person_name):
                    link_html = get_link_html(
                        person_link.replace("api/", ""), person_name
                    )
                    graph.add_node(
                        person_name, title=link_html, group="person_name", size=10
                    )
                for role in roles:
                    if (not graph.has_edge(person_name, project_title)) or (
                        not graph[person_name][project_title]["title"]
                        == role.get("name")
                    ):
                        graph.add_edge(
                            person_name,
                            project_title,
                            title=role.get("name"),
                            label=role.get("name"),
                        )
    return graph


def annotate_networkx_data(graph):
    """
    Annotate number of neighbors for filtering.
    """
    annotated_node_data = {}
    for node_label, data in graph.nodes(data=True):
        if group := data.get("group"):
            if group not in annotated_node_data:
                annotated_node_data[group] = {}
            neighbors = graph.neighbors(node_label)
            neighbor_len = len(list(neighbors))
            annotated_node_data[group][f"{node_label} ({neighbor_len})"] = {
                "neighbor_len": neighbor_len,
                "label": node_label,
            }
    return annotated_node_data


def convert_graph(graph):
    """
    Convert networkx to pyvis graph.
    """
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=True,
    )
    net.barnes_hut()
    net.from_nx(graph)
    return net


def find_neighbor_nodes_helper(node_list, graph):
    """
    Find unique node neighbors and flatten.
    """
    successors_generator_array = [
        # pylint: disable=unnecessary-comprehension
        [item for item in graph.successors(node)]
        for node in node_list
    ]
    predecessors_generator_array = [
        # pylint: disable=unnecessary-comprehension
        [item for item in graph.predecessors(node)]
        for node in node_list
    ]
    neighbors = successors_generator_array + predecessors_generator_array
    flat = sum(neighbors, [])
    return list(set(flat))


def render_filter_form(annotated_node_data, graph):
    """
    Render form to allow the user to define search nodes.
    """
    st.session_state["filter"] = st.radio(
        "Filter", ["No filter", "Filter results"], index=0, horizontal=True
    )
    if (filter_determinant := st.session_state.get("filter")) and (
        filter_determinant == "Filter results"
    ):
        st.session_state["node_group"] = st.selectbox(
            "Entity type", list(annotated_node_data.keys())
        )
        if node_group := st.session_state.get("node_group"):
            ordered_lookup = dict(
                sorted(
                    annotated_node_data[node_group].items(),
                    key=lambda item: item[1].get("neighbor_len"),
                    reverse=True,
                )
            )
            st.session_state["search_nodes_label"] = st.multiselect(
                "Filter projects", list(ordered_lookup.keys())
            )
        if search_nodes_label := st.session_state.get("search_nodes_label"):
            filter_nodes = [
                ordered_lookup[label].get("label") for label in search_nodes_label
            ]
            search_nodes_neighbors = find_neighbor_nodes_helper(filter_nodes, graph)
            search_nodes = find_neighbor_nodes_helper(search_nodes_neighbors, graph)
            st.session_state["search_nodes"] = list(
                set(search_nodes + filter_nodes + search_nodes_neighbors)
            )


def filter_node(node):
    """
    Check to see if the filter term is in the nodes selected.
    """
    if (
        (filter_term := st.session_state.get("filter"))
        and (filter_term == "Filter results")
        and (search_nodes := st.session_state.get("search_nodes"))
    ):
        if node not in search_nodes:
            return False
    return True


if __name__ == "__main__":
    pass
