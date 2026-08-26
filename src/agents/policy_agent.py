from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.rag.policy_retriever import retrieve_policies

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


def answer_policy_question(question):

    # RAG: retrieve only the most relevant policies
    policies = retrieve_policies(
        question,
        limit=3
    )

    if not policies:
        return "I couldn't find a relevant policy."

    policy_text = "\n\n".join(
        [
            f"""
Policy Type: {p[1]}
Description: {p[2]}
Conditions: {p[3]}
Timeframe: {p[4]}
"""
            for p in policies
        ]
    )

    prompt = f"""
You are a SmartShop customer service assistant.

Answer the customer's question using ONLY the
retrieved policies below.

Customer Question:
{question}

Retrieved Policies:
{policy_text}

If the retrieved policies do not contain enough
information to answer the question, say that the
policy information is unavailable.

Give a clear and concise answer.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    question = "Can I return my laptop after 20 days?"

    print(
        answer_policy_question(question)
    )