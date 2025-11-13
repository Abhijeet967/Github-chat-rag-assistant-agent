"""
Repository Handler - Downloads and indexes GitHub repositories
Stores embeddings in ChromaDB for semantic search
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
import requests
import chromadb
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubDownloader:
    """Downloads files from GitHub repositories"""
    
    def __init__(self, cache_dir: str = "./repo_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_repo_structure(self, repo_url: str, branch: str = "main") -> Dict:
        """
        Fetch repository structure from GitHub API
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to fetch from (default: main)
        
        Returns:
            Repository structure with files and metadata
        """
        try:
            # Parse repo URL
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1].replace('.git', '')
            
            logger.info(f"Downloading repository: {owner}/{repo}")
            
            repo_data = {
                'repo_name': repo,
                'owner': owner,
                'url': repo_url,
                'files': []
            }
            
            # Fetch from GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            files = self._fetch_directory(api_url, branch)
            
            repo_data['files'] = files
            logger.info(f"Found {len(files)} code files")
            
            return repo_data
        
        except Exception as e:
            logger.error(f"Error downloading repository: {e}")
            return {'error': str(e)}
    
    def _fetch_directory(self, api_url: str, branch: str, path: str = "") -> List[Dict]:
        """Recursively fetch directory contents from GitHub API"""
        files = []
        
        try:
            headers = {}
            if os.getenv('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"
            
            params = {'ref': branch}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            items = response.json()
            
            for item in items:
                # Skip node_modules, .git, etc.
                if self._should_skip(item['name']):
                    continue
                
                if item['type'] == 'file' and self._is_code_file(item['name']):
                    files.append({
                        'name': item['name'],
                        'path': item['path'],
                        'url': item['download_url'],
                        'size': item.get('size', 0)
                    })
                elif item['type'] == 'dir' and len(files) < 500:
                    subfiles = self._fetch_directory(item['url'], branch, item['path'])
                    files.extend(subfiles)
        
        except Exception as e:
            logger.error(f"Error fetching directory: {e}")
        
        return files
    
    @staticmethod
    def _should_skip(name: str) -> bool:
        """Check if file/directory should be skipped"""
        skip_patterns = ['.git', 'node_modules', '__pycache__', '.env', 'dist', 'build', '.venv']
        return any(pattern in name for pattern in skip_patterns)
    
    @staticmethod
    def _is_code_file(filename: str) -> bool:
        """Check if file is a code file"""
        code_extensions = [
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c',
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
            '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.md'
        ]
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def fetch_file_content(self, download_url: str) -> Optional[str]:
        """Fetch content of a file from GitHub"""
        try:
            headers = {}
            if os.getenv('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"
            
            response = requests.get(download_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        
        except Exception as e:
            logger.error(f"Error fetching file: {e}")
            return None


class EmbeddingStore:
    """ChromaDB-based embedding storage for code"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
    
    def create_repo_collection(self, repo_name: str):
        """Create or get a collection for a repository"""
        collection_name = f"repo_{repo_name.lower().replace('/', '_')}"
        
        try:
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def store_code_snippets(self, repo_name: str, code_snippets: List[Dict]) -> int:
        """
        Store code snippets in ChromaDB
        
        Args:
            repo_name: Repository name
            code_snippets: List of code snippets with metadata
        
        Returns:
            Number of snippets stored
        """
        collection = self.create_repo_collection(repo_name)
        
        stored = 0
        for i, snippet in enumerate(code_snippets):
            try:
                collection.add(
                    ids=[f"{repo_name}_{i}"],
                    documents=[snippet['content']],
                    metadatas=[{
                        'file': snippet.get('file', ''),
                        'repo': repo_name,
                        'stored_at': datetime.now().isoformat()
                    }]
                )
                stored += 1
            except Exception as e:
                logger.error(f"Error storing snippet {i}: {e}")
        
        logger.info(f"Stored {stored} code snippets")
        return stored
    
    def search_snippets(self, repo_name: str, query: str, n_results: int = 5) -> Dict:
        """
        Search for relevant code snippets
        
        Args:
            repo_name: Repository name
            query: Search query
            n_results: Number of results to return
        
        Returns:
            Search results with documents and metadata
        """
        try:
            collection = self.client.get_collection(
                name=f"repo_{repo_name.lower().replace('/', '_')}"
            )
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            return {
                'success': True,
                'documents': results.get('documents', [[]])[0],
                'metadatas': results.get('metadatas', [[]])[0],
                'distances': results.get('distances', [[]])[0]
            }
        
        except Exception as e:
            logger.error(f"Error searching snippets: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class CodeChunker:
    """Splits code into meaningful chunks"""
    
    @staticmethod
    def chunk_code(content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split code into chunks with overlap
        
        Args:
            content: Code content
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of code chunks
        """
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def create_snippets(files: List[Dict], downloader: GitHubDownloader) -> List[Dict]:
        """
        Create code snippets from files
        
        Args:
            files: List of files to process
            downloader: GitHubDownloader instance
        
        Returns:
            List of code snippets
        """
        snippets = []
        
        for file_info in files:
            try:
                content = downloader.fetch_file_content(file_info['url'])
                
                if content:
                    chunks = CodeChunker.chunk_code(content)
                    
                    for i, chunk in enumerate(chunks):
                        snippets.append({
                            'file': file_info['path'],
                            'chunk_index': i,
                            'content': chunk
                        })
            
            except Exception as e:
                logger.error(f"Error processing file {file_info['path']}: {e}")
        
        logger.info(f"Created {len(snippets)} code snippets")
        return snippets
