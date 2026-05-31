import httpx
from loguru import logger
import re
from typing import List

class DuckDuckGoSearcher:
    """
    Performs web searches using DuckDuckGo's HTML interface.
    No API key required.
    Supports restricting results to specific trusted domains.
    """
    SEARCH_URL = "https://html.duckduckgo.com/html/"

    async def search(self, query: str, trusted_sites: List[str] = None, max_results: int = 5) -> list[dict]:
        """
        Executes a search and returns a list of snippets with source site identification.
        """
        full_query = query
        if trusted_sites:
            site_filter = " " + " OR ".join([f"site:{site}" for site in trusted_sites])
            full_query += site_filter

        logger.info(f"Performing restricted snippet search: {full_query}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.SEARCH_URL,
                    data={"q": full_query},
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
                    timeout=10.0
                )
                response.raise_for_status()
                
                body = response.text
                results = []
                
                # Extract snippets, titles, and display URLs
                snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', body, re.DOTALL)
                titles = re.findall(r'<a class="result__a".*?>(.*?)</a>', body, re.DOTALL)
                urls = re.findall(r'<span class="result__url">(.*?)</span>', body, re.DOTALL)
                
                for i in range(min(len(snippets), max_results)):
                    clean_snippet = re.sub(r'<.*?>', '', snippets[i]).strip()
                    clean_title = re.sub(r'<.*?>', '', titles[i]).strip()
                    display_url = re.sub(r'<.*?>', '', urls[i]).strip() if i < len(urls) else "Trusted Web Source"
                    
                    # Extract domain name for easier citation
                    domain = display_url.replace("www.", "").split("/")[0]
                    
                    results.append({
                        "text": clean_snippet,
                        "metadata": {
                            "source_file": f"WEB: {domain}",
                            "source_title": clean_title,
                            "document_type": "web_search",
                            "site_name": domain
                        },
                        "similarity": 0.8 # Standard fallback score
                    })
                
                return results
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
