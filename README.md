# RAG Assistant Agent 🤖

**Chat with any GitHub repository using uAgents ChatProtocol and Fetch.ai ASI:One LLM**

A smart conversational agent that allows you to:
- 📥 Download and index any GitHub repository  
- 💬 Ask intelligent questions about the code
- 🧠 Get answers powered by Fetch.ai ASI:One LLM
- 🔄 Have natural multi-turn conversations with repositories
- ⚡ Communicate via ASI 1 ChatProtocol

---

## ✨ Features

✅ **Repository Indexing** - Downloads and processes GitHub repositories with semantic chunking  
✅ **Vector Search** - ChromaDB for fast semantic similarity search  
✅ **ASI:One LLM** - Intelligent analysis using Fetch.ai's ASI:One model  
✅ **ChatProtocol** - ASI 1 standard for agent communication  
✅ **Mailbox Support** - Reliable async message delivery  
✅ **Multi-turn Conversations** - Session-based chat history  
✅ **Real-time Acknowledgements** - Message delivery confirmation  

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /Users/abhi/projects/rag-assistant-agent
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your API keys:

```env
FETCH_AI_API_KEY=your_fetch_ai_api_key_here
GITHUB_TOKEN=your_github_token_here
AGENT_PORT=8001
AGENT_SEED=rag_assistant_seed_2025
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Run the Agent

```bash
poetry run python agent.py
```

**Output:**
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

## 💬 Usage Examples

### Start a Session

```
Send: StartSessionContent
Agent: "🤖 RAG Assistant - Chat with GitHub Repositories..."
```

### Index a Repository

```
User: index https://github.com/fetchai/uagents uagents
Agent: ✅ Repository Indexed Successfully!
        📊 Statistics:
        • Files: 120
        • Snippets: 1,450
        🎯 You can now query this repository!
```

### Query a Repository

```
User: query uagents How does authentication work?
Agent: ✅ Answer from uagents:

        Authentication in this framework uses...
        [Detailed answer from code analysis]
        
        💡 Ask another question or try a different repository!
```

### List Indexed Repositories

```
User: list
Agent: 📚 Indexed Repositories:
        • uagents
        • fetch-ai-docs
        • example-repo
```

### Get Help

```
User: help
Agent: 📖 Available Commands:
        Indexing:
        • index <repo_url> <repo_name> - Download and index a GitHub repo
        ...
```

---

## 📁 Project Structure

```
rag-assistant-agent/
├── agent.py                 # Main RAG Assistant Agent with ChatProtocol
├── src/
│   ├── rag_engine.py        # Fetch.ai ASI:One LLM integration
│   └── repo_handler.py      # Repository indexing & storage
├── pyproject.toml           # Poetry dependencies
├── .env.example             # Environment template
└── README.md               # This file
```

---

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────┐
│         ChatProtocol Client (ASI 1)                 │
│      (uAgents Agent or HTTP Client)                 │
└─────────────────────┬───────────────────────────────┘
                      │ ChatMessage
                      ↓
        ┌─────────────────────────────┐
        │   RAG Assistant Agent       │
        │  (Mailbox Enabled)          │
        │  Port 8001 (configurable)   │
        └──┬──────────────────────┬───┘
           │                      │
    ┌──────▼────────┐    ┌────────▼────────┐
    │  Repo Handler │    │   RAG Engine    │
    │               │    │                 │
    │ • GitHub DL   │    │ • ASI:One LLM   │
    │ • Chunking    │    │ • Conversation │
    │ • Indexing    │    │ • Analysis      │
    └──────┬────────┘    └────────┬────────┘
           │                      │
           └──────────┬───────────┘
                      │
            ┌─────────▼──────────┐
            │   ChromaDB         │
            │  (Vector Store)    │
            │  (Embeddings)      │
            └────────────────────┘
```

---

## 🎯 Commands

| Command | Format | Example |
|---------|--------|---------|
| **Index** | `index <url> <name>` | `index https://github.com/fetchai/uagents uagents` |
| **Query** | `query <name> <question>` | `query uagents How does it work?` |
| **List** | `list` | `list` |
| **Help** | `help` | `help` |
| **Exit** | `exit` | `exit` |

---

## 🔌 API Configuration

### Fetch.ai ASI:One

Get your API key from: https://fetch.ai

The agent uses the OpenAI-compatible API endpoint:
```
Base URL: https://api.fetch.ai/llm/v1
Model: asi1-mini
```

### GitHub Token (Optional)

For higher API rate limits, add your GitHub token:
https://github.com/settings/tokens

---

## 📊 How It Works

1. **Download** - Repository files fetched from GitHub API
2. **Index** - Code is chunked and stored as embeddings in ChromaDB
3. **Search** - User queries retrieve semantically similar code
4. **Analyze** - Fetch.ai ASI:One LLM generates intelligent answers
5. **Respond** - Answer sent via ChatProtocol to user

---

## 🔐 Security

- Never commit `.env` file (git ignores it)
- Keep API keys private
- Use environment variables for secrets
- ChatProtocol messages are protocol-level secure

---

## 🐛 Troubleshooting

### Agent Not Starting

**Issue:** Port already in use  
**Solution:** Change `AGENT_PORT` in `.env`

### API Key Errors

**Issue:** FETCH_AI_API_KEY not found  
**Solution:** Add key to `.env` file

### Repository Not Found

**Issue:** GitHub API rate limit  
**Solution:** Add `GITHUB_TOKEN` to `.env`

### Empty Search Results

**Issue:** Repository not indexed yet  
**Solution:** Run `index <url> <name>` first

---

## 📚 Technologies

- **uAgents** - Agent framework
- **ChatProtocol** - ASI 1 communication standard
- **Fetch.ai ASI:One** - LLM for code analysis
- **ChromaDB** - Vector database for semantic search
- **Python 3.10+** - Runtime

---

## 📝 Example Session

```
User: index https://github.com/SylphAI-Inc/AdaiFlow AdaiFlow
Agent: ✅ Repository Indexed Successfully!
       📊 Statistics:
       • Repository: AdaiFlow
       • Files: 45
       • Snippets: 1,250
       🎯 You can now query this repository!
       Try: query AdaiFlow What is this project?

User: query AdaiFlow How to use embedder with openai client?
Agent: ✅ Answer from AdaiFlow:

       To use the Embedder with the OpenAI client, you can set it up as follows:
       
       from adalflow.core.embedder import Embedder
       embedder = Embedder(model_client=OpenAIClient())
       
       [Detailed explanation from code analysis]

User: exit
Agent: 👋 Thanks for using RAG Assistant! Goodbye!
```

---

## 🚀 Next Steps

- [ ] Configure your Fetch.ai API key
- [ ] Add GitHub token for higher rate limits
- [ ] Run the agent
- [ ] Index a repository
- [ ] Start asking questions!

---

## 📞 Support

For issues or questions:
- Check `.env.example` for configuration
- Review agent logs for detailed errors
- Ensure API keys are valid

---

**Built with** 🤖 **uAgents** + **ChatProtocol (ASI 1)** + **Fetch.ai ASI:One**

**Learn fast. Chat with code.** 💬
