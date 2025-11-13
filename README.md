
 🤖 RAG Assistant Agent

Chat with any GitHub repository using uAgents ChatProtocol and Fetch.ai ASI:One LLM

A smart conversational agent that allows you to:
- 📥 Download and index any GitHub repository  
- 💬 Ask intelligent questions about the code  
- 🧠 Get answers powered by Fetch.ai ASI:One LLM  
- 🔄 Have natural multi-turn conversations with repositories  
- ⚡ Communicate via ASI 1 ChatProtocol  

---

 ✨ Features

✅ **Repository Indexing** – Downloads and processes GitHub repositories with semantic chunking  
✅ **Vector Search** – Uses ChromaDB for fast semantic similarity search  
✅ **ASI:One LLM** – Intelligent analysis powered by Fetch.ai’s ASI:One model  
✅ **ChatProtocol** – Follows ASI 1 standard for agent communication  
✅ **Mailbox Support** – Reliable async message delivery between agents  
✅ **Multi-turn Conversations** – Persistent chat history per session  
✅ **Real-time Acknowledgements** – Message delivery confirmation system  

---

🚀 Quick Start

 1️⃣ Clone and Setup
```bash
cd /Users/abhi/projects/rag-assistant-agent
cp .env.example .env
````

 2️⃣ Configure Environment

Edit `.env` with your API keys:

```env
FETCH_AI_API_KEY=your_fetch_ai_api_key_here
GITHUB_TOKEN=your_github_token_here
AGENT_PORT=8001
AGENT_SEED=rag_assistant_seed_2025
```

 3️⃣ Install Dependencies

```bash
poetry install
```

 4️⃣ Run the Agent

```bash
poetry run python agent.py
```

**Expected Output:**

```
======================================================================
🤖 RAG ASSISTANT AGENT
Chat with any GitHub Repository
======================================================================

📬 Agent Address: agent1q2w3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j8k9l0m1n2b3v4c5x6z7a8
🌐 Mailbox: ENABLED
💬 Protocol: ChatProtocol (ASI 1)
🧠 LLM: Fetch.ai ASI:One

🔥 Flow:
  GitHub URL → Download → Index → Store Embeddings → Chat via ASI:One

🚀 Features:
  • Download and index any GitHub repository
  • Semantic search via ChromaDB
  • Intelligent conversation with Fetch.ai ASI:One
  • ChatProtocol (ASI 1) for agent communication
  • Multi-turn conversation memory
  • Real-time message acknowledgements
======================================================================
```

---

 💬 Usage Examples

 🧩 Start a Session

```
User: StartSessionContent
Agent: 🤖 RAG Assistant - Chat with GitHub Repositories...
```

 📦 Index a Repository

```
User: index https://github.com/fetchai/uagents uagents
Agent: ✅ Repository Indexed Successfully!
        📊 Statistics:
        • Files: 120
        • Snippets: 1,450
        🎯 You can now query this repository!
```

 🔍 Query a Repository

```
User: query uagents How does authentication work?
Agent: ✅ Answer from uagents:

        Authentication in this framework uses...
        [Detailed AI-generated code explanation]
        
        💡 Ask another question or try a different repository!
```

 📚 List Indexed Repositories

```
User: list
Agent: 📂 Indexed Repositories:
        • uagents
        • fetch-ai-docs
        • example-repo
```

 🆘 Get Help

```
User: help
Agent: 📖 Available Commands:
        • index <repo_url> <repo_name> - Download and index a GitHub repo
        • query <repo_name> <question> - Ask a question about repo
        • list - Show all indexed repos
        • help - Display command list
        • exit - Stop the agent
```

---

 📁 Project Structure

```
rag-assistant-agent/
├── agent.py                 # Main RAG Assistant Agent (ChatProtocol logic)
├── src/
│   ├── rag_engine.py        # LLM integration (Fetch.ai ASI:One)
│   └── repo_handler.py      # Repository indexing, embeddings, and storage
├── pyproject.toml           # Poetry dependencies
├── .env.example             # Environment variable template
└── README.md                # Documentation file
```

---

 🔧 Architecture

```
┌──────────────────────────────────────────────────────┐
│          ChatProtocol Client (ASI 1)                 │
│      (uAgents Agent / External Client)               │
└─────────────────────┬────────────────────────────────┘
                      │ ChatMessage
                      ▼
        ┌─────────────────────────────┐
        │   RAG Assistant Agent       │
        │   (Mailbox Enabled)         │
        │   Port 8001 (Configurable)  │
        └──┬──────────────────────┬───┘
           │                      │
    ┌──────▼────────┐      ┌──────▼────────┐
    │ Repo Handler  │      │   RAG Engine  │
    │ • GitHub DL   │      │ • ASI:One LLM │
    │ • Chunking    │      │ • Conversation│
    │ • Indexing    │      │ • Analysis    │
    └──────┬────────┘      └──────┬────────┘
           │                      │
           └──────────┬───────────┘
                      │
            ┌─────────▼──────────┐
            │     ChromaDB       │
            │  (Vector Storage)  │
            └────────────────────┘
```

---

 🎯 Commands

| Command   | Format                    | Example                                            |
| --------- | ------------------------- | -------------------------------------------------- |
| **Index** | `index <url> <name>`      | `index https://github.com/fetchai/uagents uagents` |
| **Query** | `query <name> <question>` | `query uagents What is an Agent?`                  |
| **List**  | `list`                    | `list`                                             |
| **Help**  | `help`                    | `help`                                             |
| **Exit**  | `exit`                    | `exit`                                             |

---

🔌 API Configuration

 🔑 Fetch.ai ASI:One

Get your key from: [https://console.fetch.ai](https://console.fetch.ai)

```
Base URL: https://api.fetch.ai/llm/v1
Model: asi1 or asi1-mini
```

 🧰 GitHub Token (Optional)

Get your token from: [https://github.com/settings/tokens](https://github.com/settings/tokens)

Used to avoid rate-limits during repository indexing.

---

 📊 Workflow

1. **Download** – Repository fetched using GitHub API
2. **Index** – Code is split and embedded into ChromaDB
3. **Retrieve** – Relevant code snippets found via semantic similarity
4. **Analyze** – Fetch.ai ASI:One generates a contextual answer
5. **Respond** – Sent back via ChatProtocol (ASI 1)

---


 📚 Technologies

* 🧠 **Fetch.ai ASI:One** – LLM for reasoning and answers
* 🧩 **uAgents Framework** – Agent creation and communication
* 💾 **ChromaDB** – Vector database for semantic search
* 🐍 **Python 3.10+** – Runtime
* 🌐 **GitHub API** – Repository fetching



 🚀 Next Steps

* [ ] Add Fetch.ai API key to `.env`
* [ ] Add GitHub token for better rate limits
* [ ] Run the agent
* [ ] Index a repository
* [ ] Start chatting with your code!




