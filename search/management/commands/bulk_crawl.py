from django.core.management.base import BaseCommand
from django.utils import timezone
from search.models import SearchIndex, CrawlQueue, CrawlLog, DomainVerification
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import time
import sys


CATEGORY_RULES = [
    (["wikipedia.org", "wiki"], "Wissen"),
    (["github.com", "gitlab.com", "stackoverflow.com", "pypi.org", "npmjs.com", "python.org", "django"], "Entwicklung"),
    (["amazon.", "ebay.", "etsy.com", "zalando", "shop", "store"], "Shopping"),
    (["spiegel.de", "zeit.de", "tagesschau.de", "bbc.com", "cnn.com", "news"], "Nachrichten"),
    (["youtube.com", "netflix.com", "spotify.com", "twitch.tv"], "Entertainment"),
    ([".gov", "bundesregierung", "bundestag", "verwaltung"], "Regierung"),
    (["university", "universit", ".edu", "hochschule", "schule"], "Bildung"),
    (["krankenhaus", "klinik", ".med", "gesundheit", "arzt"], "Gesundheit"),
    (["hotel", "restaurant", "gastro", "tourismus", "reise"], "Tourismus"),
    (["microsoft.com", "apple.com", "google.", "meta.com", "openai.com", "tesla"], "Technologie"),
    (["volkswagen", "bmw.de", "mercedes", "audi.de", "auto"], "Automobil"),
    (["bank", "finanz", "versicherung", "sparkasse", "volksbank"], "Finanzen"),
]


class Command(BaseCommand):
    help = "Massiver Crawler für tausende Seiten"

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=str, help="Seed-URLs (kommagetrennt)")
        parser.add_argument("--depth", type=int, default=1)
        parser.add_argument("--delay", type=float, default=1.0)
        parser.add_argument("--max", type=int, default=500)

    def classify(self, domain):
        for keywords, category in CATEGORY_RULES:
            if any(k in domain.lower() for k in keywords):
                return category
        if domain.endswith(".de"):
            return "Deutschland"
        return "Web"

    def handle(self, *args, **options):
        if not options["seed"]:
            self.stdout.write("Usage: --seed URL1,URL2,URL3 --depth 2 --max 500")
            return

        seeds = [s.strip() for s in options["seed"].split(",") if s.strip()]
        depth = options["depth"]
        delay = options["delay"]
        max_pages = options["max"]

        headers = {
            "User-Agent": "JDSCrawler/2.0 (+https://jds-search.de/bot)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }

        to_visit = [(url, 0) for url in seeds]
        visited = set()
        indexed = 0
        errors = 0
        start = time.time()

        self.stdout.write(self.style.MIGRATE_HEADING(f"Crawler: {len(seeds)} Seeds, max {max_pages}"))

        while to_visit and indexed < max_pages:
            url, d = to_visit.pop(0)
            url = url.split("#")[0].rstrip("/")

            if url in visited or d > depth:
                continue
            visited.add(url)

            try:
                resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                if resp.status_code != 200:
                    continue
                if "text/html" not in resp.headers.get("Content-Type", ""):
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string.strip()[:500] if soup.title and soup.title.string else ""

                desc = ""
                for meta in soup.find_all("meta"):
                    if meta.get("name", "").lower() in ("description", "og:description"):
                        d2 = meta.get("content", "").strip()
                        if d2 and (not desc or len(d2) > len(desc)):
                            desc = d2[:1000]

                for tag in soup(["script", "style", "nav", "footer", "noscript"]):
                    tag.decompose()
                body = " ".join(soup.get_text(separator=" ", strip=True).split())[:10000]
                if not desc and body:
                    desc = body[:200]

                domain = urlparse(url).netloc.lower()
                cat = self.classify(domain)

                SearchIndex.objects.update_or_create(url=url, defaults={
                    "title": title or domain, "description": desc, "content": body,
                    "category": cat, "domain": domain,
                })
                indexed += 1

                self.stdout.write(f"  [{indexed}] {title[:70] if title else domain}")
                self.stdout.write(f"       {url[:100]}")

                CrawlLog.objects.create(url=url, status_code=200, pages_indexed=1, pages_queued=0)

                if d < depth:
                    links = []
                    for link in soup.find_all("a", href=True):
                        href = link["href"].strip()
                        if not href or href[0] in "#jmt":
                            continue
                        full = urljoin(url, href)
                        p = urlparse(full)
                        if p.scheme in ("http", "https") and full not in visited:
                            links.append(full)

                    for link in list(dict.fromkeys(links))[:25]:
                        to_visit.append((link, d + 1))

                if indexed % 100 == 0:
                    elapsed = time.time() - start
                    self.stdout.write(f"  === {indexed} Seiten | {indexed/elapsed:.1f}/s | Queue: {len(to_visit)} ===")

                time.sleep(delay)

            except requests.Timeout:
                errors += 1
            except requests.ConnectionError:
                errors += 1
            except Exception as e:
                errors += 1

        elapsed = time.time() - start
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Fertig: {indexed} Seiten, {errors} Fehler, {elapsed:.0f}s, "
            f"Queue: {len(to_visit)} übrig"
        ))
