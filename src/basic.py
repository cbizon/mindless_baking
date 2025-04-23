import os
import shutil
import asyncio
import sys
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling.filters import FilterChain,URLPatternFilter,ContentTypeFilter

class URLPatternExcluder:
    #Wraps a URLPatternFilter to negate its results

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def apply(self,url):
        # Call A's _apply and negate the result
        return not self._wrapped.apply(url)

    def __getattr__(self, name):
        # Delegate all other attributes/methods to the wrapped instance
        return getattr(self._wrapped, name)

def get_paths(url):
    """
    Given a URL, return the path components as a list.
    """
    parsed_url = urlparse(url)
    paths = parsed_url.path.split('/')
    # Remove empty strings from the list
    paths = [path for path in paths if path]
    print("Paths:",paths)
    return paths

async def run_advanced_crawler(input_url,sitename):
    #paths
    paths = get_paths(input_url)
    keywords = ["download", "data", "about", "cite", "citation", "faq", "help", "license", "legal", "terms",
                "publication", "fair", "docs", "readme", "info", "privacy"]
    keywords += paths

    # Create a relevance scorer
    keyword_scorer = KeywordRelevanceScorer(
        keywords=keywords,
        weight=0.7
    )

    # Perhaps it would make sense to have a filter based on domain to some degree?  e.g. if the site is at github,
    # then exclude issues, actions, pulls, branches, release, and so on...  Most sites are their own domain though
    # and we don't want to build this for every site, that misses the point.
    url_filter = URLPatternFilter(patterns=["*jsessionid*", "*#*", "*search*", "*Search", "*gz", "*tar", "*zip",
                                            "*tsv", "*csv", "*xml", "*commit*", "*action*", "*issues*", "*sql",
                                            "*obo", "*owl", "*tool*","*event*", "*jobs*", "*meeting*", "*sdf"])
    url_excluder = URLPatternExcluder(url_filter)
    content_filter = ContentTypeFilter(allowed_types=["text/html", "application/javascript"])
    #These are here for specific sites: jsp is BindingDB, io is for het.io.  These aren't great
    # but content type filter only allows you to accept, not exclude.  I think it would be better to exclude things like
    # gz's etc.
    #content_filter._MIME_MAP["jsp"] = "application/javascript"
    #content_filter._MIME_MAP["io"] = "text/html"
    #filter_chain = FilterChain([url_excluder,content_filter] )
    filter_chain = FilterChain([url_excluder] )

    # Set up the configuration
    config = CrawlerRunConfig(
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=2,
            max_pages=100,
            include_external=False,
            url_scorer=keyword_scorer,
            filter_chain=filter_chain,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        stream=True,
        verbose=False,
        #Two things: this only looks for e.g. <nav> and not <span id="nav"> so fails on e.g. CTD
        # 2. I think that it is causing links to be prematurely excluded, i.e. this removes the elements
        # before pulling links.
        #excluded_tags=['form', 'header', 'footer', 'nav']
    )

    # If the directory exists, remove it
    outpath = f"crawls/{sitename}"
    if os.path.exists(outpath):
        shutil.rmtree(outpath)
    os.makedirs(outpath)

    with open(f"{outpath}/index.txt", 'w') as index_file:
        index_file.write("filename\turl\tscore\tdepth\n")
        # Execute the crawl
        last_file = 0
        async with AsyncWebCrawler() as crawler:
            async for result in await crawler.arun(input_url, config=config):
                if result.status_code != 200:
                    continue
                score = result.metadata.get("score", 0)
                #if score == 0:
                #    continue
                #index_file.write("filename\turl\tscore\tdepth\n")
                filename = f"{outpath}/output_{last_file}.md"
                with open(filename, 'w') as md_file:
                    md_file.write(result.markdown)
                depth = result.metadata.get("depth", 0)
                index_file.write(f"{filename}\t{result.url}\t{score:.2f}\t{depth}\n")
                #hrefs=[ x["href"] for x in result.links["internal"]]
                #for h in hrefs:
                #    index_file.write( " " + h +"\n")
                last_file += 1
                #print(f"Depth: {depth} | Score: {score:.2f} | {result.url}")
    print("Crawl finished. Results saved in:", sitename)


async def go(input_file, concurrent_tasks = 5):
    with open(input_file, "r") as inf:
        sites = []
        for line in inf:
            if line.startswith("#"):
                continue
            line = line.strip().split()
            sites.append( (line[1], line[0]) )
        #tasks = [ asyncio.create_task(run_advanced_crawler(url, sitename)) for url, sitename in sites]
        ##All at once is too much, lets limit
        #semaphore = asyncio.Semaphore(concurrent_tasks)
        #async with semaphore:
        #    await asyncio.gather(*tasks)
        for url, sitename in sites:
            print(f"Running {sitename} at {url}")
            await run_advanced_crawler(url, sitename)
            #await asyncio.sleep(1)


if __name__ == "__main__":
    #asyncio.run(run_advanced_crawler("https://github.com/GauravPandeyLab/KiNet", "Kinace"))
    asyncio.run(run_advanced_crawler("https://drugcentral.org/", "DrugCentral"))
    #asyncio.run(run_advanced_crawler("http://bindingdb.org","BDB"))
    #asyncio.run(run_advanced_crawler("http://het.io","hetio"))
    #Inputs should be a 2 column (space delim) with the first column being the site name and the second being the URL
    #asyncio.run(go("robokop_inputs.txt"))