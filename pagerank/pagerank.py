import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    # dic = transition_model(corpus, '1.html', DAMPING)
    # print(random.choices(list(dic.keys()), weights=dic.values()))
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    num_pages = len(corpus)
    d = dict.fromkeys(corpus.keys(), (1-damping_factor)/num_pages)
    if corpus[page]:
        num_links = len(corpus[page])
        for link in corpus[page]:
            d[link] += damping_factor / num_links
    return d


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = dict.fromkeys(corpus.keys(), 0)
    current_page = random.choice(list(corpus.keys()))
    page_ranks[current_page] += 1

    for _ in range(1, n):
        tm = transition_model(corpus, current_page, damping_factor)
        next_page = random.choices(list(tm.keys()), tm.values())[0]
        current_page = next_page
        page_ranks[current_page] += 1

    for page in page_ranks:
        page_ranks[page] /= n

    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n  = len(corpus)
    current_pr = dict.fromkeys(corpus.keys(), 1 / n)
    converged = False
    while not converged:
        next_pr = {}
        converged = True
        for page in current_pr:
            pr_i = 0
            for i in corpus:
                if page in corpus[i]:
                    pr_i += current_pr[i] / len(corpus[i])
                # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself). 
                elif len(corpus[i]) == 0:
                    pr_i += current_pr[i] / n
            next_pr[page] = (1-damping_factor)/n + damping_factor * pr_i
            if abs(current_pr[page] - next_pr[page]) > 0.001:
                converged = False
        current_pr = next_pr
    return current_pr



if __name__ == "__main__":
    main()
