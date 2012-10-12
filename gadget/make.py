__author__ = 'Tomithy'

import os

inFile = "public/gadget.html"
outFile = "public/gadget.xml"

# for padding xml around the html
with open(outFile, "wt") as out:
    with open(inFile, "r") as f:
        content = f.read()

        header = '<?xml version="1.0" encoding="UTF-8" ?> <Module> <ModulePrefs/> <Content type="html"> \n<![CDATA[ \n'
        end = ']]> </Content> </Module>'

        content = header + content + end

        out.writelines(content)
        print content

os.system("git add .")
os.system("git commit -m 'Updating html'")

#  http://mcmb.herokuapp.com/json/mcmb_gadget.xml