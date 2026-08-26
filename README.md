# 🛍️ SmartShop AI

SmartShop AI is a multi-agent shopping assistant designed to help customers discover products, compare prices, understand product reviews, and get answers about store policies through a conversational interface.

The project demonstrates how an agentic AI application can combine LLM reasoning, specialized agents, structured data, RAG, APIs, and containerized services into one end-to-end system.

---

## 🎯 Purpose

The goal of SmartShop AI is to provide customers with a single conversational interface for common shopping needs instead of requiring them to manually search through products, reviews, pricing, and policy information.

Customers can ask questions such as:

- "Find me a laptop under $900"
- "Recommend products with 5-star ratings"
- "Compare laptop prices"
- "What do customers say about this product?"
- "What is the return policy?"
- "Can I return a laptop after 14 days?"

---

## 🏗️ Architecture Overview

SmartShop uses a multi-agent architecture where a Supervisor determines which specialized agent should handle each customer request.

```text
Customer
   │
   ▼
Streamlit UI
   │
   ▼
FastAPI
   │
   ▼
LangGraph
   │
   ▼
Supervisor Agent
   │
   ├──► Recommendation Agent
   │       └── PostgreSQL Products
   │
   ├──► Price Agent
   │       └── PostgreSQL Products
   │
   ├──► Review Agent
   │       └── Reviews + LLM
   │
   ├──► Policy Agent
   │       └── RAG + pgvector + LLM
   │
   └──► General Agent
           └── General conversation / fallback
```

---

## 🔄 Request Flow

A typical request moves through the system like this:

```text
User Question
      ↓
Streamlit
      ↓
FastAPI
      ↓
LangGraph Supervisor
      ↓
Intent / Agent Selection
      ↓
Specialized Agent
      ↓
Database / Vector Search / LLM
      ↓
Generated Response
      ↓
FastAPI
      ↓
Streamlit UI
```

### Example

Customer asks:

> "Find me a laptop under $900"

The request flows through:

```text
Streamlit
   ↓
FastAPI
   ↓
Supervisor
   ↓
Recommendation Agent
   ↓
Extract category + price filters
   ↓
PostgreSQL
   ↓
Matching products
   ↓
Customer
```

---

## 🤖 Agents

### Supervisor Agent
Analyzes the customer's request and routes it to the appropriate specialized agent.

### Recommendation Agent
Finds products based on criteria such as category, budget, rating, and availability.

### Price Agent
Handles product and price comparison requests.

### Review Agent
Retrieves product review information and uses an LLM to provide a concise customer-friendly summary.

### Policy Agent
Uses Retrieval-Augmented Generation (RAG) to retrieve relevant store policies and generate grounded answers.

### General Agent
Handles greetings, casual conversation, and requests outside SmartShop's supported shopping capabilities.

---

## 🧠 RAG Policy Flow

Store policy questions use semantic retrieval instead of relying only on the LLM.

```text
Policy Question
      ↓
Embedding
      ↓
pgvector Similarity Search
      ↓
Relevant Store Policies
      ↓
LLM
      ↓
Grounded Policy Answer
```

This allows responses to be based on SmartShop's policy data rather than information invented by the model.

---

## 🛠️ Technology Stack

- Python
- LangChain
- LangGraph
- OpenAI
- FastAPI
- Pydantic
- PostgreSQL
- pgvector
- Retrieval-Augmented Generation (RAG)
- Streamlit
- Docker
- Docker Compose

---

## 🐳 Container Architecture

The application is containerized using Docker Compose.

```text
Docker Compose
│
├── smartshop-ui
│     └── Streamlit
│
├── smartshop-api
│     └── FastAPI + LangGraph + Agents
│
└── smartshop-db
      └── PostgreSQL + pgvector
```

The services communicate through the Docker network rather than depending on local machine configuration.

---

## 📁 Project Structure

```text
SmartShop_AI/
│
├── app/
│   └── app.py
│
├── data/
│   ├── products/
│   ├── reviews/
│   └── policies/
│
├── src/
│   ├── agents/
│   ├── api/
│   ├── database/
│   ├── rag/
│   └── graph.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔐 Configuration

Sensitive configuration is managed through environment variables and is not committed to source control.

Examples include:

```text
OPENAI_API_KEY
SMARTSHOP_API_KEY
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

---

## 🚀 Project Status

**SmartShop AI v1**

Current capabilities include:

- Multi-agent request routing
- Product recommendations
- Price comparison
- Review summarization
- RAG-based policy questions
- General conversational handling
- PostgreSQL and pgvector integration
- FastAPI backend
- Streamlit user interface
- Dockerized application environment

Future versions can expand routing intelligence, conversation memory, observability, testing, additional agents, and deployment capabilities.
