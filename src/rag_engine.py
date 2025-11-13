"""
RAG Engine with Fetch.ai ASI:One LLM
Enables intelligent conversation with GitHub repositories
"""
import logging
import os
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) Engine
    Uses Fetch.ai ASI:One LLM for conversational repository analysis
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "asi1-mini"):
        """Initialize RAG engine with Fetch.ai ASI:One LLM"""
        self.api_key = api_key or os.getenv('FETCH_AI_API_KEY') or os.getenv('ASI_ONE_API_KEY')
        self.model = model  # ASI:One model
        
        # Initialize Fetch.ai OpenAI-compatible client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=os.getenv("FETCH_AI_BASE_URL", "https://api.asi1.ai/v1")
        )
        
        if not self.api_key:
            logger.warning("FETCH_AI_API_KEY not set - RAG functionality will be limited")
    
    def chat_with_repo(
        self,
        query: str,
        contexts: List[str],
        repo_name: str = "",
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Have a conversation with the repository using ASI:One LLM
        
        Args:
            query: User's question about the repository
            contexts: Relevant code contexts retrieved from the repo
            repo_name: Name of the repository being analyzed
            conversation_history: Previous conversation messages for context
        
        Returns:
            Dict with success status, answer, and metadata
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'FETCH_AI_API_KEY not configured',
                'answer': None
            }
        
        try:
            # Build context string from retrieved code (limit size to avoid token overflow)
            limited_contexts = contexts[:3]  # Use only top 3 contexts
            context_str = "\n\n---\n\n".join([
                f"[Context {i+1}]\n{ctx[:1500]}" 
                for i, ctx in enumerate(limited_contexts)
            ])
            
            # Create conversational system prompt
            system_prompt = f"""You are a friendly and intelligent assistant helping developers understand GitHub repositories.

Repository: {repo_name}

Code Contexts:
{context_str}

Be concise, helpful, and focus on answering the user's question using the provided code."""
            
            # Build message history - limit to recent messages
            messages = []
            
            # Add recent conversation history if available (limit to last 5 exchanges)
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages = 5 exchanges
            
            # Add current user query
            messages.append({"role": "user", "content": query})
            
            # Call Fetch.ai ASI:One LLM with proper error handling
            logger.info(f"Calling Fetch.ai ASI:One API with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,  # asi1-mini
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            
            return {
                'success': True,
                'answer': answer,
                'model': self.model,
                'repo_name': repo_name,
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error generating answer: {error_msg}")
            
            # Provide helpful error messages
            if "404" in error_msg:
                error_msg = f"Fetch.ai API Error (404): Check your API key is valid. Full error: {error_msg}"
            elif "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = f"Fetch.ai API Error: Invalid API key. Please verify FETCH_AI_API_KEY in .env"
            elif "429" in error_msg:
                error_msg = "Fetch.ai API: Rate limit exceeded. Please try again later."
            
            return {
                'success': False,
                'error': error_msg,
                'answer': None
            }
    
    def analyze_repo_overview(self, repo_info: Dict, sample_files: List[str]) -> Dict:
        """
        Generate an overview analysis of the repository
        
        Args:
            repo_info: Repository metadata
            sample_files: Sample file names from the repo
        
        Returns:
            Analysis of what the repository does
        """
        if not self.api_key:
            return {
                'success': True,
                'overview': f"Repository '{repo_info.get('repo_name')}' with {repo_info.get('file_count', 0)} files. Key files: {', '.join(sample_files[:5])}",
                'repo_name': repo_info.get('repo_name')
            }
        
        try:
            prompt = f"""Analyze this GitHub repository and provide a brief overview:

Repository: {repo_info.get('repo_name', 'Unknown')}
File Count: {repo_info.get('file_count', 0)}
Sample Files: {', '.join(sample_files[:10])}

Provide a 1-2 sentence summary of what this repository appears to do."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            return {
                'success': True,
                'overview': response.choices[0].message.content,
                'repo_name': repo_info.get('repo_name')
            }
        
        except Exception as e:
            logger.error(f"Error analyzing repository overview: {e}")
            # Provide fallback overview
            return {
                'success': True,
                'overview': f"Repository '{repo_info.get('repo_name')}' with {repo_info.get('file_count', 0)} files indexed. Main files: {', '.join(sample_files[:5])}",
                'repo_name': repo_info.get('repo_name')
            }


class ContextRanker:
    """Ranks and filters code contexts for relevance"""
    
    @staticmethod
    def rank_by_relevance(
        query: str,
        contexts: List[str],
        metadatas: List[Dict],
        distances: List[float],
        threshold: float = 0.3
    ) -> Dict:
        """
        Rank contexts by relevance to the query
        
        Args:
            query: User's query
            contexts: Code contexts
            metadatas: Metadata for each context
            distances: Similarity distances
            threshold: Minimum similarity threshold
        
        Returns:
            Ranked contexts with similarity scores
        """
        ranked = []
        
        for context, metadata, distance in zip(contexts, metadatas, distances):
            # Convert distance to similarity (0-1, where 1 is most similar)
            similarity = 1 - min(distance, 1.0)
            
            if similarity >= threshold:
                ranked.append({
                    'context': context,
                    'file': metadata.get('file_path', 'unknown'),
                    'similarity': similarity,
                    'distance': distance
                })
        
        # Sort by similarity descending
        ranked.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'ranked_contexts': ranked,
            'total_found': len(ranked),
            'threshold': threshold
        }
