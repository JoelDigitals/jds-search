from django.core.management.base import BaseCommand
from search.models import SearchIndex
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


class Command(BaseCommand):
    help = "Sucht bei Google und indexiert die Top-Ergebnisse"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Suchbegriff")
        parser.add_argument("--max", type=int, default=10)
        parser.add_argument("--delay", type=float, default=1.5)

    def handle(self, *args, **options):
        query = options["query"]
        max_results = options["max"]
        delay = options["delay"]

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        indexed = 0
        urls = []

        try:
            resp = requests.get(
                f"https://www.google.com/search?q={query}&num={max_results}",
                headers=headers, timeout=15
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a"):
                href = link.get("href", "")
                if href.startswith("/url?q=") and "webcache" not in href:
                    url = href.split("/url?q=")[1].split("&")[0]
                    if url.startswith("http") and url not in urls:
                        urls.append(url)
        except Exception:
            pass

        if not urls:
            search_urls = [
                f"https://de.wikipedia.org/wiki/{query.replace(' ', '_')}",
                f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            ]
            urls = search_urls

        self.stdout.write(f"Google-Index: {query} ({len(urls)} URLs)")

        for url in urls[:max_results]:
            try:
                resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string.strip()[:500] if soup.title and soup.title.string else ""
                desc = ""
                for meta in soup.find_all("meta"):
                    if meta.get("name", "").lower() in ("description", "og:description"):
                        d = meta.get("content", "").strip()
                        if d and (not desc or len(d) > len(desc)):
                            desc = d[:1000]
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                body = " ".join(soup.get_text(separator=" ", strip=True).split())[:5000]
                if not desc and body:
                    desc = body[:200]
                domain = urlparse(url).netloc.lower()
                cat = "Wissen" if "wiki" in domain else "Web"

                SearchIndex.objects.update_or_create(url=url, defaults={
                    "title": title or domain, "description": desc, "content": body,
                    "category": cat, "domain": domain,
                })
                indexed += 1
                self.stdout.write(f"  [{indexed}] {title[:70]}")
                time.sleep(delay)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  [ERR] {url[:60]}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nFertig: {indexed} Seiten indexiert"))
