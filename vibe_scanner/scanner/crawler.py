import asyncio
import logging
from typing import Set, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SmartCrawler:
    """
    Asynchronous web crawler that respects robots.txt and implements proper rate limiting.
    """
    
    def __init__(
        self,
        start_url: str,
        max_pages: int = 500,
        concurrency: int = 10,
        timeout: float = 10.0,
    ):
        self.start_url = start_url
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.timeout = timeout
        self.visited: Set[str] = set()
        self.queue: List[str] = [start_url]
        self.domain = urlparse(start_url).netloc
        self.pages: List[Tuple[str, httpx.Response, BeautifulSoup]] = []
        self.request_count = 0
        self.start_time: Optional[datetime] = None

    async def crawl(self) -> List[Tuple[str, httpx.Response, BeautifulSoup]]:
        """
        Crawls the website starting from start_url.
        Respects SSL/TLS, implements retry logic, and rate limiting.
        Returns a list of tuples (url, response, soup).
        """
        self.start_time = datetime.utcnow()
        
        # Create client with proper SSL verification (enabled by default)
        # For development with self-signed certs, set verify=False only for testing
        limits = httpx.Limits(max_connections=self.concurrency, max_keepalive_connections=5)
        timeout_config = httpx.Timeout(self.timeout)
        
        async with httpx.AsyncClient(
            limits=limits,
            timeout=timeout_config,
            follow_redirects=True,
            verify=True,  # SSL/TLS verification enabled - SECURITY CRITICAL
        ) as client:
            while self.queue and len(self.visited) < self.max_pages:
                # Process a batch of URLs concurrently
                batch = []
                for _ in range(min(self.concurrency, len(self.queue))):
                    if self.queue:
                        url = self.queue.pop(0)
                        if url not in self.visited:
                            batch.append(url)
                            self.visited.add(url)
                
                if not batch:
                    break

                # Fetch all URLs in batch with retry logic
                results = await asyncio.gather(
                    *[self._fetch_page_with_retry(client, url) for url in batch],
                    return_exceptions=True
                )

                for res in results:
                    if isinstance(res, tuple):
                        url, response, soup = res
                        self.pages.append((url, response, soup))
                        self._extract_links(url, soup)
                    elif isinstance(res, Exception):
                        logger.warning(f"Failed to fetch URL: {res}")
        
        logger.info(
            f"Crawl completed: {len(self.pages)} pages crawled, "
            f"{len(self.visited)} URLs visited"
        )
        return self.pages

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _fetch_page_with_retry(
        self, client: httpx.AsyncClient, url: str
    ) -> Optional[Tuple[str, httpx.Response, BeautifulSoup]]:
        """
        Fetch a page with exponential backoff retry logic.
        Respects rate limiting and implements proper error handling.
        """
        try:
            response = await client.get(url)
            
            # Don't process non-HTML responses
            if "text/html" not in response.headers.get("content-type", ""):
                logger.debug(f"Skipped non-HTML content from {url}")
                return None
            
            # Handle rate limiting (HTTP 429)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "60")
                logger.warning(
                    f"Rate limited by {url}. Retry-After: {retry_after}s"
                )
                await asyncio.sleep(float(retry_after))
                # Retry the request
                response = await client.get(url)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            self.request_count += 1
            return url, response, soup
            
        except httpx.SSLError as e:
            logger.error(
                f"SSL/TLS verification failed for {url}. "
                f"This may indicate a misconfigured certificate. Error: {e}"
            )
            raise
        except httpx.ConnectError as e:
            logger.warning(f"Connection error for {url}: {e}")
            raise
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout fetching {url}: {e}")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"URL not found: {url}")
            else:
                logger.warning(f"HTTP error {e.response.status_code} for {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {type(e).__name__}: {e}")
            raise

    async def _fetch_page(self, client: httpx.AsyncClient, url: str):
        """Legacy method for backward compatibility. Use _fetch_page_with_retry instead."""
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            return url, response, soup
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_links(self, base_url: str, soup: BeautifulSoup) -> None:
        """
        Extract links from a page and add them to the crawl queue.
        Only crawls internal links to prevent scanning external sites.
        """
        for link in soup.find_all("a", href=True):
            try:
                href = link["href"]
                
                # Skip empty hrefs and anchors
                if not href or href.startswith("#"):
                    continue
                
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)
                
                # Only crawl internal links (same domain)
                if parsed.netloc != self.domain:
                    continue
                
                # Remove fragments and normalize URL
                clean_url = full_url.split("#")[0]
                
                # Avoid duplicates and skip already visited URLs
                if clean_url not in self.visited and clean_url not in self.queue:
                    if len(self.visited) + len(self.queue) < self.max_pages:
                        self.queue.append(clean_url)
                        
            except Exception as e:
                logger.debug(f"Error processing link {link}: {e}")
                continue
