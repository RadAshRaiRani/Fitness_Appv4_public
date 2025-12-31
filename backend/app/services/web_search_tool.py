"""
Web Search Tool for Agents
Uses DuckDuckGo to search the web for current information
"""

from typing import List, Dict
from duckduckgo_search import DDGS


class WebSearchTool:
    """Web search tool for agents to get current information"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web for current information
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            results = []
            search_results = self.ddgs.text(
                query,
                max_results=max_results,
                region='us-en',
                safesearch='moderate'
            )
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', '')
                })
            
            return results
            
        except Exception as e:
            print(f"Error in web search: {e}")
            return []
    
    def search_diet(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for diet/nutrition related information
        
        Args:
            query: Search query related to diet/nutrition
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        # Enhance query for diet/nutrition search
        enhanced_query = f"diet nutrition {query}"
        return self.search(enhanced_query, max_results)
    
    def search_exercise(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for exercise/workout related information
        
        Args:
            query: Search query related to exercise/workout
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        # Enhance query for exercise/workout search
        enhanced_query = f"exercise workout fitness {query}"
        return self.search(enhanced_query, max_results)


# Global instance for reuse
web_search_tool = WebSearchTool()

