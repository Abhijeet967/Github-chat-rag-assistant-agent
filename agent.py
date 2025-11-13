"""
RAG Assistant Agent
Chat with any GitHub repository using uAgents ChatProtocol and Fetch.ai ASI:One LLM

A smart assistant that:
1. Downloads and indexes GitHub repositories
2. Allows conversational interaction with repository code
3. Uses Fetch.ai ASI:One for intelligent code analysis
4. Communicates via ChatProtocol (ASI 1 standard)
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from src.rag_engine import RAGEngine, ContextRanker
from src.repo_handler import GitHubDownloader, EmbeddingStore, CodeChunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Initialize Agent with ChatProtocol and Mailbox
agent = Agent(
    name="RAG-Assistant",
    seed=os.getenv("AGENT_SEED", "rag_assistant_seed_2025"),
    port=int(os.getenv("AGENT_PORT", 8001)),
    mailbox=True,
    publish_agent_details=True,
)

# Initialize components
rag_engine = RAGEngine(api_key=os.getenv("FETCH_AI_API_KEY"), model="asi1-mini")
repo_downloader = GitHubDownloader(cache_dir=os.getenv("REPO_CACHE_PATH", "./repo_cache"))
embedding_store = EmbeddingStore(persist_dir=os.getenv("CHROMA_DB_PATH", "./chroma_db"))

# In-memory conversation tracking
conversations = {}
indexed_repos = {}

# Create ChatProtocol
rag_chat_proto = Protocol(spec=chat_protocol_spec)


def create_response(text: str, end_session: bool = False) -> ChatMessage:
    """Create a formatted chat response"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


# ============================================================================
# ChatProtocol Message Handler
# ============================================================================
@rag_chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming ChatProtocol messages"""
    session_id = str(ctx.session)
    ctx.storage.set(session_id, sender)

    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🟢 RAG Assistant: Session started from {sender}")
            
            # Initialize conversation
            conversations[session_id] = {
                "user": sender,
                "messages": [],
                "current_repo": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            
            await ctx.send(
                sender,
                create_response(
                    "🤖 **RAG Assistant - Chat with GitHub Repositories**\n\n"
                    "I help you understand any GitHub repository through intelligent conversation.\n\n"
                    "**Commands:**\n"
                    "• `index <repo_url> <repo_name>` - Index a GitHub repository\n"
                    "• `query <repo_name> <question>` - Ask a question about the repo\n"
                    "• `help` - Show available commands\n"
                    "• `exit` - End session\n\n"
                    "**Example:** `query fetchai-uagents How does authentication work?`"
                ),
            )
            continue

        elif isinstance(item, TextContent):
            user_input = item.text.strip()
            ctx.logger.info(f"🔍 RAG Assistant: Received from {sender}: {user_input}")

            try:
                # Parse command
                parts = user_input.split(maxsplit=2)
                command = parts[0].lower() if parts else ""

                if command == "help":
                    help_msg = (
                        "📖 **Available Commands:**\n\n"
                        "**Indexing:**\n"
                        "• `index <repo_url> <repo_name>` - Download and index a GitHub repo\n"
                        "  Example: `index https://github.com/fetchai/uagents fetchai-uagents`\n\n"
                        "**Querying:**\n"
                        "• `query <repo_name> <question>` - Ask about indexed repository\n"
                        "  Example: `query fetchai-uagents What are agents?`\n\n"
                        "**Management:**\n"
                        "• `list` - Show indexed repositories\n"
                        "• `help` - Show this help message\n"
                        "• `exit` - End session"
                    )
                    await ctx.send(sender, create_response(help_msg))

                elif command == "list":
                    if not indexed_repos:
                        await ctx.send(sender, create_response("📚 No repositories indexed yet."))
                    else:
                        repo_list = "\n".join([f"• {name}" for name in indexed_repos.keys()])
                        await ctx.send(
                            sender,
                            create_response(f"📚 **Indexed Repositories:**\n\n{repo_list}")
                        )

                elif command == "index":
                    if len(parts) < 3:
                        await ctx.send(
                            sender,
                            create_response(
                                "⚠️ Format: `index <repo_url> <repo_name>`\n"
                                "Example: `index https://github.com/fetchai/uagents uagents`"
                            ),
                        )
                        continue

                    repo_url = parts[1]
                    repo_name = parts[2]

                    ctx.logger.info(f"📥 Indexing repository: {repo_name}")
                    await ctx.send(sender, create_response(f"⏳ Downloading {repo_name}..."))

                    # Download repository
                    repo_data = repo_downloader.get_repo_structure(repo_url)
                    
                    if 'error' in repo_data:
                        await ctx.send(
                            sender,
                            create_response(f"❌ Error: {repo_data['error']}")
                        )
                        continue

                    file_count = len(repo_data.get('files', []))
                    await ctx.send(
                        sender,
                        create_response(f"📦 Processing {file_count} files...")
                    )

                    # Create snippets
                    snippets = CodeChunker.create_snippets(
                        repo_data['files'],
                        repo_downloader
                    )

                    # Store in ChromaDB
                    stored = embedding_store.store_code_snippets(repo_name, snippets)

                    indexed_repos[repo_name] = {
                        'url': repo_url,
                        'files': file_count,
                        'snippets': stored,
                        'indexed_at': datetime.now().isoformat()
                    }

                    success_msg = (
                        f"✅ **Repository Indexed Successfully!**\n\n"
                        f"📊 **Statistics:**\n"
                        f"• Repository: {repo_name}\n"
                        f"• Files: {file_count}\n"
                        f"• Snippets: {stored}\n\n"
                        f"🎯 You can now query this repository!\n"
                        f"Try: `query {repo_name} What does this project do?`"
                    )
                    await ctx.send(sender, create_response(success_msg))

                elif command == "query":
                    if len(parts) < 3:
                        await ctx.send(
                            sender,
                            create_response(
                                "⚠️ Format: `query <repo_name> <question>`\n"
                                "Example: `query uagents How does authentication work?`"
                            ),
                        )
                        continue

                    repo_name = parts[1]
                    question = parts[2]

                    if repo_name not in indexed_repos:
                        await ctx.send(
                            sender,
                            create_response(
                                f"❌ Repository '{repo_name}' not indexed.\n"
                                f"Use: `index <url> {repo_name}` to index it first."
                            ),
                        )
                        continue

                    ctx.logger.info(f"🔍 Querying {repo_name}: {question}")
                    await ctx.send(sender, create_response(f"⏳ Searching {repo_name}..."))

                    # Search for relevant code
                    search_results = embedding_store.search_snippets(
                        repo_name=repo_name,
                        query=question,
                        n_results=5
                    )

                    if not search_results.get('success'):
                        await ctx.send(
                            sender,
                            create_response(f"❌ Error searching: {search_results.get('error')}")
                        )
                        continue

                    contexts = search_results.get('documents', [])
                    if not contexts:
                        await ctx.send(
                            sender,
                            create_response(
                                f"❌ No relevant code found for your question in {repo_name}."
                            ),
                        )
                        continue

                    await ctx.send(
                        sender,
                        create_response(f"🧠 Analyzing {len(contexts)} code sections...")
                    )

                    # Generate answer with ASI:One
                    answer_result = rag_engine.chat_with_repo(
                        query=question,
                        contexts=contexts,
                        repo_name=repo_name,
                        conversation_history=conversations[session_id]["messages"]
                    )

                    if not answer_result.get('success'):
                        await ctx.send(
                            sender,
                            create_response(
                                f"⚠️ Error generating answer: {answer_result.get('error')}"
                            ),
                        )
                        continue

                    # Format response
                    answer = answer_result['answer']
                    response_text = (
                        f"✅ **Answer from {repo_name}:**\n\n"
                        f"{answer}\n\n"
                        f"---\n\n"
                        f"💡 **Ask another question or try a different repository!**"
                    )

                    # Store in conversation
                    conversations[session_id]["messages"].append({
                        "role": "user",
                        "content": question
                    })
                    conversations[session_id]["messages"].append({
                        "role": "assistant",
                        "content": answer
                    })
                    conversations[session_id]["current_repo"] = repo_name

                    await ctx.send(sender, create_response(response_text))

                elif command == "exit":
                    exit_msg = "👋 Thanks for using RAG Assistant! Goodbye!"
                    await ctx.send(sender, create_response(exit_msg, end_session=True))
                    
                    if session_id in conversations:
                        del conversations[session_id]

                else:
                    await ctx.send(
                        sender,
                        create_response(
                            f"❓ Unknown command: {command}\n\n"
                            "Type `help` for available commands."
                        ),
                    )

            except Exception as e:
                ctx.logger.error(f"❌ Error: {e}")
                await ctx.send(
                    sender,
                    create_response(f"⚠️ Error processing request: {str(e)}")
                )


@rag_chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements"""
    ctx.logger.info(f"✅ Message acknowledged from {sender}")


# ============================================================================
# Agent Events
# ============================================================================
@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup banner"""
    ctx.logger.info("=" * 70)
    ctx.logger.info("🤖 RAG ASSISTANT AGENT")
    ctx.logger.info("💬 Chat with any GitHub Repository")
    ctx.logger.info("⚡ Powered by Fetch.ai ASI:One + ChromaDB + uAgents")
    ctx.logger.info("=" * 70)
    ctx.logger.info(f"📬 Agent Address: {agent.address}")
    ctx.logger.info(f"🌐 Mailbox: ENABLED")
    ctx.logger.info(f"💬 Protocol: ChatProtocol (ASI 1 Compatible)")
    ctx.logger.info(f"🧠 LLM: Fetch.ai ASI:One (asi1-mini)")
    ctx.logger.info("")
    ctx.logger.info("Ready to analyze GitHub repositories!")
    ctx.logger.info("=" * 70)


@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    ctx.logger.info("🤖 Shutting down RAG Assistant...")


# Include ChatProtocol
agent.include(rag_chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 RAG ASSISTANT AGENT")
    print("Chat with any GitHub Repository")
    print("=" * 70)
    print(f"\n📬 Agent Address: {agent.address}")
    print(f"🌐 Mailbox: ENABLED")
    print(f"💬 Protocol: ChatProtocol (ASI 1)")
    print(f"🧠 LLM: Fetch.ai ASI:One\n")
    print("🔥 Flow:")
    print("  GitHub URL → Download → Index → Store Embeddings → Chat via ASI:One")
    print(f"\n🚀 Features:")
    print("  • Download and index any GitHub repository")
    print("  • Semantic search via ChromaDB")
    print("  • Intelligent conversation with Fetch.ai ASI:One")
    print("  • ChatProtocol (ASI 1) for agent communication")
    print("  • Multi-turn conversation memory")
    print("  • Real-time message acknowledgements")
    print("=" * 70 + "\n")

    agent.run()
