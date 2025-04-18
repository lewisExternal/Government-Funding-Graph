# Government-Funding-Graph

Graph visualisation for UK Research and Innovation (UKRI) funding, including Networkx, Pyvis, and queryable via LlamaIndex graph RAG implementation. A working demo can be seen below. 

The inspiration for this project came from a desire to make better tooling for grant writing, namely to suggest research topics, funding bodies, research institutions, and researchers. I have made Innovate UK grant applications in the past, so I have had an interest in the government funding landscape for some time. 

Concretely, a lot of the recent political discourse focuses on government spending, namely Elon Musk's Department of Government Efficiency (DOGE) in the United States and similar sentiments echoed here in the UK, as Kier Starmer looks to integrate AI into government.
Perhaps the release of this project is quite timely. Albeit not the original intention, I hope as a secondary outcome of this article is that it inspires more exploration into open source datasets for public spending.

I have used NetworkX & PyVis for the graph visualisation of UKRI API data. Then, I detail a LlamaIndex graph RAG implementation. For completeness, I have also included my initial LangChain-based solution. The web framework is Streamlit, the demo is hosted on Streamlit community cloud.

If you are interested in more projects like this, there is a sign up form that you can use to subscribe to our [mailing list](https://docs.google.com/forms/d/e/1FAIpQLScMwyRLHUwc_qTqCPndJCudVQCn0zQl4upcHmqj26ZG5akl4g/viewform).


## What is UKRI?
UK Research and Innovation is a non-departmental public body sponsored by the Department for Science, Innovation and Technology (DSIT) that allocates funding for research and development. Generally, funding is awarded to research institutions and businesses.

"We invest £8 billion of taxpayers’ money each year into research and innovation and the people who make it happen. We work across a huge range of fields – from biodiversity conservation to quantum computing, and from space telescopes to innovative health care. We give everyone the opportunity to contribute and to benefit, bringing together people and organisations nationally and globally to create, develop and deploy new ideas and technologies." - [UKRI Website](https://www.ukri.org/)

## What is a Graph? 
A graph is a convenient data structure showing the relationships between different entities (nodes) and their relationships to each other (edges). In some instances, we also associate those relationships with a numerical value.

"In computer science, a graph is an abstract data type that is meant to implement the undirected graph and directed graph concepts from the field of graph theory within mathematics.

A graph data structure consists of a finite (and possibly mutable) set of vertices (also called nodes or points), together with a set of unordered pairs of these vertices for an undirected graph or a set of ordered pairs for a directed graph. These pairs are known as edges (also called links or lines), and for a directed graph are also known as edges but also sometimes arrows or arcs." - [Wikipedia](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))


## What is NetworkX?
NetworkX is a useful library in this project to construct and store our graph. Specifically, a digraph though the library supports many graph variants such as multigraphs, the library also supports graph-related utility functions.

"NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks." - [NetworkX Website](https://networkx.org/)

## What is Pyvis?
We use the PyVis Python package to create dynamic network views for our graph.

"The pyvis library is meant for quick generation of visual network graphs with minimal python code. It is designed as a wrapper around the popular Javascript visJS library" - [Pyvis Docs](https://pyvis.readthedocs.io/en/latest/tutorial.html)

## What is LlamaIndex?
LlamaIndex is a popular library for LLM applications, including support for agentic workflows, we use it to perform the graph RAG component of this project.

"LlamaIndex (GPT Index) is a data framework for your LLM application. Building with LlamaIndex typically involves working with LlamaIndex core and a chosen set of integrations (or plugins)." - [LlamaIndex Github](https://github.com/run-llama/llama_index)


## What is Graph RAG?
Retrieval-augmented generation, or RAG as it is commonly known, is an AI framework for which additional context from an external knowledge base is used to ground LLM answers. Graph RAG, by extension, pertains to the use of a Graph to provide this additional context.

"GraphRAG is a powerful retrieval mechanism that improves GenAI applications by taking advantage of the rich context in graph data structures... Basic RAG systems rely solely on semantic search in vector databases to retrieve and rank sets of isolated text fragments. While this approach can surface some relevant information, it fails to capture the context connecting these pieces. For this reason, basic RAG systems are ill-equipped to answer complex, multi-hop questions. This is where GraphRAG comes in. It uses knowledge graphs to represent and connect information to capture not only more data points but also their relationships. Thus, graph-based retrievers can provide more accurate and relevant results by uncovering hidden connections that aren’t often obvious but are crucial for correlating information." - [Neo4j Website](https://neo4j.com/blog/genai/what-is-graphrag/)

## What is Streamlit? 
Streamlit is a lightweight Python web framework we will use to create the web application for this project.

"Streamlit is an open-source Python framework for data scientists and AI/ML engineers to deliver dynamic data apps with only a few lines of code. Build and deploy powerful data apps in minutes." - [Streamlit website](https://docs.streamlit.io/)

## Medium Article  

You can read the accompanying Medium article here for additional context.  

## Live Demo  
To see the hosted solution on Streamlit cloud, please navigate to the link below:
https://governmentfundinggraph.streamlit.app/

## Run Locally  

### Run the Streamlit application  
Run the following from the root directory.  
```
docker compose up --build 
```
To see the Streamlit application, please navigate to:  
```
http://localhost:8501/
```
Once finished, be sure to run the following.
```
docker compose down
```

## Requirements  
Requires the following 
* Docker Desktop 
* Open AI API Key (Optional)

## Formatting
* python3 -m black utils/; python3 -m black main.py

## References 
* https://medium.com/@haiyangli_38602/make-knowledge-graph-rag-with-llamaindex-from-own-obsidian-notes-b20a350fa354
* https://medium.com/data-science-in-your-pocket/graphrag-using-langchain-31b1ef8328b9