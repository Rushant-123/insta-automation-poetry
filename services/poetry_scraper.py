import asyncio
import httpx
import re
import random
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass

from .poetry_models import Poetry

logger = logging.getLogger(__name__)


@dataclass
class ScrapedPoetry:
    """Container for scraped poetry data."""
    lines: List[str]
    author: Optional[str] = None
    title: Optional[str] = None
    source: str = "scraped"
    url: Optional[str] = None


class PoetryScraper:
    """Service for scraping poetry from various online sources."""
    
    def __init__(self):
        """Initialize poetry scraper."""
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            },
            timeout=30.0
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
            
    async def scrape_reddit_poetry(self, subreddit: str = "Poetry", limit: int = 50) -> List[ScrapedPoetry]:
        """
        Scrape poetry from Reddit.
        
        Args:
            subreddit: Subreddit name to scrape from
            limit: Maximum number of posts to fetch
            
        Returns:
            List of scraped poetry
        """
        logger.info(f"Scraping poetry from r/{subreddit}")
        poems = []
        
        try:
            # Use Reddit JSON API (no auth required for public posts)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            params = {"limit": limit}
            
            response = await self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                for post_data in posts:
                    post = post_data.get("data", {})
                    
                    # Skip if not text post or too short
                    if not post.get("selftext") or len(post.get("selftext", "")) < 50:
                        continue
                        
                    # Parse the post
                    poem = await self._parse_reddit_post(post)
                    if poem and self._is_valid_poem(poem):
                        poems.append(poem)
                        
        except Exception as e:
            logger.error(f"Failed to scrape Reddit r/{subreddit}: {e}")
            
        logger.info(f"Scraped {len(poems)} poems from r/{subreddit}")
        return poems
        
    async def _parse_reddit_post(self, post: Dict) -> Optional[ScrapedPoetry]:
        """Parse a Reddit post into poetry."""
        try:
            title = post.get("title", "").strip()
            content = post.get("selftext", "").strip()
            author = post.get("author", "Unknown")
            url = f"https://reddit.com{post.get('permalink', '')}"
            
            # Clean up the content
            lines = self._clean_poetry_text(content)
            
            if not lines or len(lines) < 3:
                return None
                
            return ScrapedPoetry(
                lines=lines,
                author=author,
                title=title,
                source="reddit",
                url=url
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Reddit post: {e}")
            return None
            
    async def scrape_poetry_foundation(self, limit: int = 20) -> List[ScrapedPoetry]:
        """
        Scrape from Poetry Foundation (public domain poems).
        
        Args:
            limit: Maximum number of poems to fetch
            
        Returns:
            List of scraped poetry
        """
        logger.info("Scraping from Poetry Foundation")
        poems = []
        
        try:
            # Poetry Foundation's poem browser
            base_url = "https://www.poetryfoundation.org"
            search_url = f"{base_url}/poems/browse"
            
            # Get the browse page
            response = await self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find poem links
                poem_links = soup.find_all('a', href=re.compile(r'/poems/\d+/'))[:limit]
                
                for link in poem_links:
                    poem_url = base_url + link['href']
                    poem = await self._scrape_poetry_foundation_poem(poem_url)
                    if poem and self._is_valid_poem(poem):
                        poems.append(poem)
                        # Be respectful - small delay
                        await asyncio.sleep(0.5)
                        
        except Exception as e:
            logger.error(f"Failed to scrape Poetry Foundation: {e}")
            
        logger.info(f"Scraped {len(poems)} poems from Poetry Foundation")
        return poems
        
    async def _scrape_poetry_foundation_poem(self, url: str) -> Optional[ScrapedPoetry]:
        """Scrape a single poem from Poetry Foundation."""
        try:
            response = await self.session.get(url)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find poem content
            poem_div = soup.find('div', class_='o-poem')
            if not poem_div:
                return None
                
            # Extract title and author
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Untitled"
            
            author_elem = soup.find('span', class_='c-txt_attribution')
            author = author_elem.text.strip() if author_elem else "Unknown"
            
            # Extract poem lines
            lines = []
            for line_elem in poem_div.find_all(['div', 'p']):
                line_text = line_elem.get_text().strip()
                if line_text and len(line_text) > 2:
                    lines.append(line_text)
                    
            if not lines:
                return None
                
            # Clean and filter lines
            lines = self._clean_poetry_text('\n'.join(lines))
            
            if len(lines) < 3:
                return None
                
            return ScrapedPoetry(
                lines=lines,
                author=author,
                title=title,
                source="poetry_foundation",
                url=url
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape poem from {url}: {e}")
            return None
            
    async def scrape_poets_org(self, limit: int = 15) -> List[ScrapedPoetry]:
        """
        Scrape from Poets.org (Academy of American Poets).
        
        Args:
            limit: Maximum number of poems to fetch
            
        Returns:
            List of scraped poetry
        """
        logger.info("Scraping from Poets.org")
        poems = []
        
        try:
            # Poets.org poem search
            search_url = "https://poets.org/poems"
            
            response = await self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find poem links
                poem_links = soup.find_all('a', href=re.compile(r'/poem/'))[:limit]
                
                for link in poem_links:
                    poem_url = "https://poets.org" + link['href']
                    poem = await self._scrape_poets_org_poem(poem_url)
                    if poem and self._is_valid_poem(poem):
                        poems.append(poem)
                        await asyncio.sleep(0.5)  # Be respectful
                        
        except Exception as e:
            logger.error(f"Failed to scrape Poets.org: {e}")
            
        logger.info(f"Scraped {len(poems)} poems from Poets.org")
        return poems
        
    async def _scrape_poets_org_poem(self, url: str) -> Optional[ScrapedPoetry]:
        """Scrape a single poem from Poets.org."""
        try:
            response = await self.session.get(url)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find poem content
            poem_div = soup.find('div', class_='poem-content')
            if not poem_div:
                return None
                
            # Extract title and author
            title = "Untitled"
            author = "Unknown"
            
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.text.strip()
                
            author_elem = soup.find('a', href=re.compile(r'/poet/'))
            if author_elem:
                author = author_elem.text.strip()
                
            # Extract poem text
            poem_text = poem_div.get_text('\n').strip()
            lines = self._clean_poetry_text(poem_text)
            
            if len(lines) < 3:
                return None
                
            return ScrapedPoetry(
                lines=lines,
                author=author,
                title=title,
                source="poets_org",
                url=url
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape poem from {url}: {e}")
            return None
            
    def _clean_poetry_text(self, text: str) -> List[str]:
        """Clean and format poetry text into lines."""
        if not text:
            return []
            
        # Remove extra whitespace and split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Filter out very short lines and metadata
        cleaned_lines = []
        for line in lines:
            # Skip very short lines, URLs, metadata
            if (len(line) < 3 or 
                line.startswith(('http', 'www', '©', 'Copyright', 'Source:', 'Read more'))):
                continue
                
            # Remove markdown formatting
            line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Bold
            line = re.sub(r'\*(.*?)\*', r'\1', line)      # Italic
            line = re.sub(r'#{1,6}\s*', '', line)         # Headers
            
            cleaned_lines.append(line)
            
        return cleaned_lines
        
    def _is_valid_poem(self, poem: ScrapedPoetry) -> bool:
        """Check if scraped content is valid poetry."""
        if not poem or not poem.lines:
            return False
            
        # Check line count
        if len(poem.lines) < 3 or len(poem.lines) > 12:
            return False
            
        # Check if lines are reasonable length
        avg_length = sum(len(line) for line in poem.lines) / len(poem.lines)
        if avg_length < 10 or avg_length > 100:
            return False
            
        # Check for spam indicators
        spam_words = ['subscribe', 'follow', 'like', 'comment', 'share', 'click', 'buy']
        text = ' '.join(poem.lines).lower()
        if any(word in text for word in spam_words):
            return False
            
        return True
        
    async def scrape_all_sources(self, poems_per_source: int = 10) -> List[Poetry]:
        """
        Scrape poetry from all available sources.
        
        Args:
            poems_per_source: Number of poems to fetch from each source
            
        Returns:
            List of Poetry objects ready for use
        """
        logger.info("Starting comprehensive poetry scraping...")
        all_poems = []
        
        try:
            # Scrape from multiple Reddit communities
            reddit_subs = ["Poetry", "OCPoetry", "poems", "poetry_critics"]
            for sub in reddit_subs:
                poems = await self.scrape_reddit_poetry(sub, poems_per_source)
                all_poems.extend(poems[:poems_per_source//len(reddit_subs)])
                
            # Scrape from poetry websites
            foundation_poems = await self.scrape_poetry_foundation(poems_per_source)
            all_poems.extend(foundation_poems)
            
            poets_org_poems = await self.scrape_poets_org(poems_per_source)
            all_poems.extend(poets_org_poems)
            
        except Exception as e:
            logger.error(f"Error during comprehensive scraping: {e}")
            
        # Convert to Poetry objects
        poetry_objects = []
        for poem in all_poems:
            poetry_obj = Poetry(
                lines=poem.lines,
                author=poem.author,
                title=poem.title,
                source=poem.source
            )
            poetry_objects.append(poetry_obj)
            
        logger.info(f"Completed scraping: {len(poetry_objects)} poems collected")
        return poetry_objects 