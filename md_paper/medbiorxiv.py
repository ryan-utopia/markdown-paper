import logging
import requests

from .crossref import crossrefInfo

logging.basicConfig()
logger = logging.getLogger('biorxiv')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class BMxivInfo(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.base_url = "https://api.biorxiv.org/details/"
        self.servers = ["biorxiv", "medrxiv"]
    
    
    def set_proxy(self, proxy=False):
        """set proxy for session
        
        Args:
            proxy (str): The proxy adress. e.g 127.0.1:1123
        Returns:
            None
        """
        if proxy:
            self.sess.proxies = {
                "http": proxy,
                "https": proxy, }
            
    
    def extract_json_info(self, item):
        """Extract bib json information from requests.get().json()
        
        Args:
            item (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
        paper_url = f"https://www.biorxiv.org/content/{item['doi']}"
        title = item["title"]
        journal = item["server"]
        published = item["date"].split('-')
        if len(published) > 1:
            year = published[0]
        else: 
            year = ' '

        authors = item['authors'].split("; ")
        if len(authors) > 0:
            authors = " and ".join([author for author in authors])
        else:
            authors = authors

        bib_dict = {
            "title": title,
            "author": authors,
            "journal": journal,
            "year": year,
            "url": paper_url,
            "pdf_link": f"{paper_url}.full.pdf",
            "cited_count": None
        }
        
        return bib_dict


    def get_info_by_bmrxivid(self, bmrxivid):
        """Get the meta information by the given paper biorxiv_id or medrxiv_id. 
        
        Args:
            doi (str): The biorxiv or medrxiv Id
            
        Returns:
            A dict containing the paper information. 
            {
                "title": xxx,
                "author": xxx,
                "journal": xxx,
                etc
            } 
            OR
            None
        """
        urls = [self.base_url + server + "/" + bmrxivid for server in self.servers]
        for url in urls:
            try:
                r = self.sess.get(url)

                bib = r.json()['collection'][-1]
                
                if "published" in bib.keys() and bib['published'] != "NA":
                    doi = bib["published"]
                    print(doi)
                    crossref_info = crossrefInfo()
                    if len(self.sess.proxies) > 0:
                        crossref_info.set_proxy(self.sess.proxies['http'].split('//')[-1])
                    return crossref_info.get_info_by_doi(doi)
                 
                return self.extract_json_info(bib)
                
            except:
                logger.error("DOI: {} is error.".format(bmrxivid)) 
            
            
if __name__ == "__main__":
    
    arxivId = "10.1101/2022.07.28.22277637"

    arxiv_info = BMxivInfo()
    arxiv_info.set_proxy(proxy="127.0.0.1:7890")
    
    bib_arxiv = arxiv_info.get_info_by_bmrxivid(arxivId)

    
    print(bib_arxiv)
    print("\n")
