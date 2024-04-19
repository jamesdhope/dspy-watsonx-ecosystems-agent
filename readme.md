# watsonx.ai DSPy ReACT Single Agent Example

# Overview

![](overview.png)

This repo contains a demonstration of dspy Module and ReACT agentic-pattern with a watsonx.ai language model, local instance of MilvusDB and embeddings model.

# Quick Start

- install dependencies (requirements.txt TBC)
- export `WATSONX_URL`, `WATSONX_APIKEY`, `WATSONX_PROJECTID` as envars
- Launch Milvus `docker-compose up`
- Load the collection, go to `http://localhost:8010` and login with `http://milvus-standalone:19530`
- Load the data `load_data.py`
- Run the agent `agent.py`

