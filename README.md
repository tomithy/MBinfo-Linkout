README FOR SPIDER

Depdendencies (python):
- SQLite
- Scrappy

Important Files:
- Spider/DatabaseProcesses :: Coverts crawled URL into finalized json for gadget by crossing gene_id 
with homologene and with database references.
- Spider/spiders.py ::	Defines what information the spider should retrieve from the website
- gadget/public/js/gadget.js	:: Provide functionality to the gadget, including loading of information and user interactivity
- gadget/public/gadget.html	:: html of the gadget. 