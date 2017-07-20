#!/usr/bin/env python
"""
A simple and basic crawler implementation.
Multiple improvements are expected!
Installation requirement:
pip install bs4
Execution example:
python crawler.py -u http://www.example.com

"""
from urllib2 import urlopen
from urlparse import urljoin
from bs4 import BeautifulSoup
import argparse


def run_crawler(pending_links, visited_links, max_pages, visited_count):
    """
    :param list pending_links: A list of links to be visited and processed.
    :param list visited_links: A list of visited links, helping avoid revisiting.
    :param int max_pages: A maximum number of visited pages limit.
    :param int visited_count: A counter of visited pages.
    :return: None
    """
    while visited_count < max_pages and pending_links:
        try:
            curr_url = pending_links.pop(0)
            visited_links.append(curr_url)
            print "#", visited_count, "processing: ", curr_url, "\n\tFound:"
            link_parser(curr_url, pending_links, visited_links)
            visited_count += 1
        except (KeyboardInterrupt, SystemExit):
            exit(0)
        except Exception as msg:
            print "[ERROR]", msg, " in url: ", curr_url
            exit(9)
    print "DONE..."


def link_parser(url, pending_links, visited_links):
    """
    :param str url: The url to be processed and parsed for urls.
    :param list pending_links: A list of links to be visited and processed.
    :param list visited_links: A list of visited links, helping avoid revisiting.
    :return: None
    """
    try:
        # Open url with urlopen
        # More info on urllib2.urlopen:
        #       - https://docs.python.org/2/library/urllib2.html#urllib2.urlopen
        response = urlopen(url)

        # Check response Content-Type header. Ignore anything other
        # than HTML documents ('text/html').
        # CSS, javascript, images, etc are ignored.
        if 'text/html' in response.info().getheader('Content-Type'):
            # HTTP response codes other than 200 would indicate a problem.
            # More info:
            #           - https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
            if response.code == 200:
                # HTML page of the url may now be processed. Lets read it:
                html_page = response.read().decode("utf-8")
                # Parse html page with BeautifulSoup HTML Parser
                # More info on BeautifulSoup:
                #       - https://www.crummy.com/software/BeautifulSoup/bs4/doc/
                soup = BeautifulSoup(html_page, "html.parser")

                links = []
                # Find all link tags
                # html link example: <a href="http://www.example.com">example.com link</a>
                # More info:
                #           - https://www.tutorialspoint.com/html/html_text_links.htm
                #           - https://en.wikipedia.org/wiki/Hyperlink
                for link in soup.find_all('a'):

                    href = link.get('href')
                    # normalize href url
                    href = normalize_href(url, href)
                    if href:
                        # Update pending_links and visited_links accordingly:
                        if href not in pending_links and href not in visited_links:
                            pending_links.append(href)
                            links.append(href)
                            # Print the new url:
                            print "\t", href

    except (KeyboardInterrupt, SystemExit):
        print "Exited..."
        exit(0)
    except Exception as msg:
        print "[ERROR] ", msg, "\n parsing ", url


def normalize_href(current_url, href):
    """
    Very primitive and simple href normalization.
    (HINT: needs expansion)
    More info:
            - https://en.wikipedia.org/wiki/URL_normalization
    :param current_url: The url where a href is found.
    :param href: Stands for Hypertext REFerence. Url..
    :return: A normalized href, or None if href is a mailto link.
    """
    if href and ("mailto:" not in href):
        if href.startswith("www"):
            href = 'http://'+href
        elif href.startswith('//'):
            href = 'http:' + href
        elif not href.startswith('http'):
            href = urljoin(current_url, href)
        return href


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="A simple urllib + BeautifulSoup crawler.",
                                     epilog="Example usage: python crawler.py -u http://www.example.com")
    parser.add_argument('-u', '--url', type=str, required=True, help='The starting crawler URL')
    parser.add_argument('-m', '--maxpages', type=int, default=100, help='Maximum allowed number of crawled pages')
    args = parser.parse_args()
    # Starts the crawler. We user a single url as a starting point [args.url].
    # Visited urls list is empty: []. We define a maximum number of crawled
    # pages provided by maxpages command line argument.
    # We also initialize crawled pages counter with 0
    run_crawler([args.url], [], args.maxpages, 0)
