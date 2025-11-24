from setuptools import setup, find_packages 

with open('README.md', 'r', encoding='UTF-8') as f:
    README_MD = f.read()

setup(
    name="markdown-paper",
    version="1.0.0",
    description=" Helps you manage your literature notes locally written in Markdown format. ",
    long_description=README_MD,
    long_description_content_type='text/markdown',
    url="https://github.com/ryan-utopia/markdown-paper",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires=["beautifulsoup4>=4.11.1", "feedparser>=6.0.10", 
                      "urllib3>=1.26.11","requests>=2.28.1", 
                      "tqdm>=4.64.0", "Unidecode>=1.3.4"],
    entry_points={
        "console_scripts": [
            "md-paper = md_paper.md_paper:main",
        ]
    },
    packages=find_packages(),
    license="MIT",
    author="Jiayan Chen",
    author_email="ryan.utopia@outlook.com",
    download_url="https://github.com/ryan-utopia/markdown-paper/archive/refs/tags/v0.1.0.tar.gz",
    keywords=["bibtex", "arxiv", "doi", "science", "scientific-journals","literature","markdown"],
)
