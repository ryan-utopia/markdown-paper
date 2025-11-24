import os 
import logging
import re 
from tqdm import tqdm 
from .downloads import get_paper_info_from_paperid, get_paper_pdf_from_paperid

logging.basicConfig()
logger = logging.getLogger('utils')
logger.setLevel(logging.INFO)


class patternRecognizer(object):
    def __init__(self, regular_rule):
        self.pattern = re.compile(regular_rule)

    def match(self, string):
        return self.pattern.match(string)
    
    def findall(self, string):
        return self.pattern.findall(string)

    def multiple_replace(self, content, **replace_dict):
        def replace_(value):
            match = value.group()
            if match in replace_dict.keys():
                return replace_dict[match]
            else:
                return match+" **Not Correct, Check it**"
        
        replace_content = self.pattern.sub(replace_, content)
        
        return replace_content
    

def note_modified(pattern_recog, md_file, **replace_dict):
    with open(md_file, 'r') as f:
        content = f.read()
    
    replaced_content = pattern_recog.multiple_replace(content, **replace_dict)

    with open(md_file, 'w') as f:
        f.write(''.join(replaced_content))

def classify_identifier(identifier):
    """Not need to download PDF file 
    """
    if identifier.endswith("}}"):
        return True 
    else: 
        return False 


def get_update_content(m, note_file, pdfs_path, proxy):
    
    replace_dict = dict()
    for literature in tqdm(m):
        pdf = classify_identifier(literature)
        
        literature_id = literature.split('{')[-1].split('}')[0]
        bib = get_paper_info_from_paperid(literature_id, proxy=proxy)
        
        try:
            pdf_name = '_'.join(bib['title'].split(' ')) + '.pdf'
            # rep specific symbol with '_'
            pdf_name = re.sub(r"[<>:\"/\\|?*\n\r\x00-\x1F\x7F']", '_', pdf_name)
            pdf_path = os.path.join(pdfs_path, pdf_name)
            
            if pdf:
                if not os.path.exists(pdf_path):
                    get_paper_pdf_from_paperid(literature_id, pdf_path, direct_url=bib['pdf_link'], proxy=proxy)
                    if not os.path.exists(pdf_path):
                        get_paper_pdf_from_paperid(literature_id, pdf_path, proxy=proxy)

            # venue short name (conference abbreviation or journal name)
            venue_short = bib.get('venue_short', bib.get('journal', ''))

            cited_count = bib.get('cited_count', None)
            if cited_count is None:
                cited_str = ''
            else:
                cited_str = ' (citations: {})'.format(cited_count)

            if os.path.exists(pdf_path):
                replaced_literature = "- **{}**. {} et.al. **{}**, **{}** ([pdf]({}))([link]({})).{}".format(
                                    bib['title'], bib["author"].split(" and ")[0], venue_short or bib['journal'], 
                                    bib['year'],
                                    os.path.relpath(pdf_path, note_file).split('/',1)[-1], 
                                    bib['url'], cited_str)
            else:
                replaced_literature = "- **{}**. {} et.al. **{}**, **{}** ([link]({})).{}".format(
                                    bib['title'], bib["author"].split(" and ")[0], venue_short or bib['journal'], 
                                    bib['year'],
                                    bib['url'], cited_str
                                    )
            replace_dict[literature] = replaced_literature
        except:
            logger.info("Failed to download paper, skipped {}".format(literature_id))
        
    return replace_dict 