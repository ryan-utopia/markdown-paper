import logging 
import argparse
import os 

from .utils import patternRecognizer, note_modified, get_update_content
from .renamer import rename_pdfs_in_directory

logging.basicConfig()
logger = logging.getLogger('md-paper')
logger.setLevel(logging.INFO)


def set_args():
    parser = argparse.ArgumentParser(description='md-paper')
    parser.add_argument('-i', '--input', required=True, type=str, default=None,
                        help="The path to the note file or note file folder.")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='The folder path to save paper pdfs and iamges. NOTE: MUST BE FOLDER')
    parser.add_argument('-r', '--rename', type=str, default=None,
                        help='The folder path that contains pdfs to be renamed.')
    parser.add_argument('-p', '--proxy', type=str, default=None, 
                        help='The proxy. e.g. 127.0.0.1:7890')
    args = parser.parse_args()
    
    return args 

def check_args():
    args = set_args()
    input_path = args.input
    output_path = args.output 
    proxy = args.proxy
    rename_dir = args.rename
        
    return input_path, output_path, proxy, rename_dir


def get_bib_and_pdf(note_file, output_path, proxy, paper_recognizer):
    
    pdfs_path = output_path
    if not os.path.exists(pdfs_path):
        os.makedirs(pdfs_path)
    
    with open(note_file, 'r') as f:
        content = f.read()
            
    m = paper_recognizer.findall(content)
    logger.info("Number of papers to download -  {}".format(len(m)))

    if not m:
        logger.info("No papers found to download, file {} not updated.".format(note_file))
    else:
        replace_dict = get_update_content(m, note_file, pdfs_path, proxy=proxy)
            
        return replace_dict


def file_update(input_path, output_path, proxy, paper_recognizer):
    
    replace_dict =  get_bib_and_pdf(input_path, output_path,
                                    proxy, paper_recognizer)
    
    if replace_dict:
        note_modified(paper_recognizer, input_path, **replace_dict)


def main():
    input_path, output_path, proxy, rename_dir = check_args()

    if rename_dir:
        rename_pdfs_in_directory(rename_dir, input_path, proxy)
    
    if output_path:
        paper_recognizer = patternRecognizer(r'- \{.{3,}\}')
        
        if os.path.isfile(input_path):
            logger.info("Updating file {}".format(input_path))
            file_update(input_path, output_path, proxy, paper_recognizer)
            
        elif os.path.isdir(input_path):
            note_paths = []
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith('md') or file.lower().endswith('markdown'):
                        note_paths.append(os.path.join(root, file))
            for note_path in note_paths:
                logger.info("Updating file {}".format(note_path))
                file_update(note_path, output_path, proxy, paper_recognizer)
        else:
            logger.info("input path {} is not exists".format(input_path))
            
        
    if not output_path and not rename_dir:
        logger.info("missing -o or -r, program did not run, please use -h for more information")


if __name__ == "__main__":
    main()