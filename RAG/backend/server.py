"""
This is the web version of main.py.

main.py asked questions on the command line in a loop.
This file does the exact same thing (retriever -> prompt -> model),
but answers questions that come in over HTTP from the React frontend
instead of typed into the terminal.

Run with:  python server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

app = Flask(__name__)
CORS(app)  # allows the React app (running on a different port) to call this API

model = OllamaLLM(model="gemma3:4b")

# The model only ever sees the chunks pulled from your university documents,
# so it can't make up answers from outside that data.
#
# PLACEHOLDER PERSONA — customize the tone, rules, and any specific behavior
# you want (e.g. how to handle off-topic questions) right here.
template = """
You are Sahayak, the official assistant for C.U. Shah University. You answer
student and visitor questions using ONLY the information found in the
university documents provided to you.

Here is relevant context from the university documents: {context}

Here is the question to answer: {question}

Answer using ONLY the information in the context above. If the context doesn't
cover the question, say so honestly instead of guessing — never invent
policies, dates, fees, or facts that aren't in the documents.
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please type a question."}), 400

    try:
        docs = retriever.invoke(question)
        answer = chain.invoke({"context": docs, "question": question})
        return jsonify({"answer": answer})

    except Exception as exc:
        # Most common cause locally: Ollama isn't running, or the model
        # hasn't been pulled yet (ollama pull gemma3:4b).
        print(f"[server] error answering question: {exc}")
        return jsonify({
            "error": "Couldn't reach the model. Make sure Ollama is running "
                     "and that you've pulled gemma3:4b and nomic-embed-text."
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Server running at http://localhost:5000")
    app.run(port=5000, debug=True)
