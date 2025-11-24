import logging
import re
import requests 

logging.basicConfig()
logger = logging.getLogger('crossref')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class crossrefInfo(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.base_url = "http://api.crossref.org/"

    def set_proxy(self, proxy=None):
        """set proxy for session
        
        Args:
            proxy (str): The proxy adress. e.g 127.0.0.1:7890
        Returns:
            None
        """
        if proxy:
            self.sess.proxies = {
                "http": proxy,
                "https": proxy, }
            
    
    def extract_json_info(self, bib):
        """Extract bib json information from requests.get().json()

        Args:
            bib (json object): obtained by requests.get().json()

        Returns:
            A dict containing the paper information.
        """
        pub_date = [str(i) for i in bib['published']["date-parts"][0]]
        pub_date = '-'.join(pub_date)

        if 'author' in bib.keys():
            authors = ' and '.join([i["family"]+" "+i['given'] for i in bib['author'] if "family" and "given" in i.keys()])
        else:
            authors = "No author"

        # get journal / conference name
        journal = "No journal"
        short_titles = bib.get('short-container-title') or []
        if short_titles:
            journal = short_titles[0]
        else:
            container_titles = bib.get('container-title') or []
            if container_titles:
                journal = container_titles[0]

        # determine venue type: journal vs conference
        venue_type = "unknown"
        # CrossRef type field, e.g. "journal-article", "proceedings-article"
        cr_type = bib.get("type", "")
        if cr_type:
            if "journal" in cr_type:
                venue_type = "journal"
            elif "proceedings" in cr_type or "conference" in cr_type:
                venue_type = "conference"

        # derive a short venue name (mainly for conferences)
        venue_short = journal
        # If the name contains an abbreviation in parentheses, e.g., "... (ICRA)", prefer the abbreviation in parentheses
        if "(" in journal and ")" in journal:
            try:
                abbrev = journal.split("(")[-1].split(")")[0].strip()
                compact = re.sub(r"[^A-Za-z0-9]", "", abbrev)
                if 2 <= len(compact) <= 15:
                    # allow CamelCase (e.g., RoboSoft) or typical all-caps abbreviations
                    venue_short = abbrev
            except Exception:
                pass

        bib_dict = {
            "title": bib['title'][0],
            "author": authors,
            "journal": journal,
            "venue_short": venue_short,
            "year": pub_date,
            "url": bib["URL"],
            "pdf_link": bib["link"][0]["URL"],
            "cited_count": bib["is-referenced-by-count"],
            "venue_type": venue_type,
        }

        return bib_dict


    def get_info_by_doi(self, doi):
        """Get the meta information by the given paper DOI number. 
        
        Args:
            doi (str): The paper DOI number
            
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
        url = "{}works/{}"
        url = url.format(self.base_url, doi)
        
        try:
            r = self.sess.get(url)

            bib = r.json()['message']
            return self.extract_json_info(bib)
            
        except:
            logger.error("DOI: {} is error.".format(doi))
            
if __name__ == "__main__":

    doi = "10.1038/s41467-022-29269-6"
    
    crossref_info = crossrefInfo()
    crossref_info.set_proxy(proxy="127.0.1:7890")
    
    bib_doi = crossref_info.get_info_by_doi(doi)
    
    print(bib_doi)
    print("\n")
