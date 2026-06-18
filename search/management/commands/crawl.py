from django.core.management.base import BaseCommand
from search.models import SearchIndex
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sys


class Command(BaseCommand):
    help = "Crawlt echte URLs und indexiert Titel, Beschreibung und Inhalt"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="Start-URL")
        parser.add_argument("--depth", type=int, default=1, help="Crawl-Tiefe (default: 1)")
        parser.add_argument("--delay", type=float, default=1.5, help="Sekunden zwischen Requests")
        parser.add_argument("--max", type=int, default=50, help="Max Seiten (default: 50)")

    def handle(self, *args, **options):
        start_url = options["url"]
        depth = options["depth"]
        delay = options["delay"]
        max_pages = options["max"]

        if not start_url.startswith("http"):
            start_url = "https://" + start_url

        visited = set()
        to_visit = [(start_url, 0)]
        indexed = 0
        errors = 0

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; JDSCrawler/1.0; +https://jds-search.de/bot)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }

        self.stdout.write(self.style.MIGRATE_HEADING(f"Crawler startet: {start_url} (Tiefe {depth}, max {max_pages})"))
        self.stdout.write("")

        while to_visit and indexed < max_pages:
            url, current_depth = to_visit.pop(0)
            url = url.split("#")[0].rstrip("/")

            if url in visited or current_depth > depth:
                continue

            visited.add(url)

            try:
                resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True, verify=True)
                if resp.status_code != 200:
                    self.stdout.write(f"  [{current_depth}] {url[:80]} -> HTTP {resp.status_code}")
                    if resp.status_code in (301, 302) and resp.headers.get("Location"):
                        new_url = urljoin(url, resp.headers["Location"])
                        if new_url not in visited:
                            to_visit.append((new_url, current_depth))
                    continue

                ct = resp.headers.get("Content-Type", "")
                if "text/html" not in ct and "text/plain" not in ct:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                title = ""
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()[:500]

                description = ""
                for meta in soup.find_all("meta"):
                    if meta.get("name", "").lower() in ("description", "og:description"):
                        content = meta.get("content", "").strip()
                        if content and (not description or len(content) > len(description)):
                            description = content[:1000]

                for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    tag.decompose()

                body = soup.get_text(separator=" ", strip=True)
                body = " ".join(body.split())[:10000]

                if not description and body:
                    description = body[:200]

                domain = urlparse(url).netloc.lower()
                category = "Web"
                if any(k in domain for k in ["github", "gitlab", "stackoverflow", "pypi", "npmjs"]):
                    category = "Entwicklung"
                elif any(k in domain for k in ["wikipedia", "wiki"]):
                    category = "Wissen"
                elif any(k in domain for k in ["amazon", "ebay", "etsy", "shop", "store"]):
                    category = "Shopping"
                elif any(k in domain for k in ["news", "bbc", "cnn", "spiegel", "zeit", "tagesschau"]):
                    category = "Nachrichten"
                elif any(k in domain for k in ["youtube", "netflix", "spotify", "twitch"]):
                    category = "Entertainment"
                elif any(k in domain for k in ["python", "django", "react", "vue", "nodejs", "rust"]):
                    category = "Entwicklung"
                elif any(k in domain for k in ["google", "microsoft", "apple", "meta", "openai"]):
                    category = "Technologie"

                obj, created = SearchIndex.objects.update_or_create(
                    url=url,
                    defaults={
                        "title": title or domain,
                        "description": description or "",
                        "content": body,
                        "category": category,
                    },
                )

                indexed += 1
                tag = "[NEU]" if created else "[UPD]"
                self.stdout.write(self.style.SUCCESS(f"  {tag} [{current_depth}] {title[:70]}"))
                self.stdout.write(f"         {url[:100]}")

                if current_depth < depth:
                    links = []
                    for link in soup.find_all("a", href=True):
                        href = link["href"].strip()
                        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                            continue
                        full = urljoin(url, href)
                        parsed = urlparse(full)
                        if parsed.scheme in ("http", "https") and full not in visited:
                            links.append(full)

                    links = list(dict.fromkeys(links))[:20]
                    for l in links:
                        to_visit.append((l, current_depth + 1))

                time.sleep(delay)

            except requests.Timeout:
                self.stdout.write(self.style.WARNING(f"  [TIMEOUT] {url[:80]}"))
                errors += 1
            except requests.ConnectionError:
                self.stdout.write(self.style.WARNING(f"  [CONN] {url[:80]}"))
                errors += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERR] {url[:80]}: {e}"))
                errors += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Fertig: {indexed} indexiert, {errors} Fehler, {len(visited)} URLs besucht"
        ))
        self.stdout.write(f"  python manage.py runserver -> http://localhost:8000/search/")
