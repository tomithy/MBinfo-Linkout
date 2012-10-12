__author__ = 'Tomithy'

#todo: Should I use regex to check if the table has provided correct information?
#todo: how to check if all returned url is valid?
#todo: search DB table to see which cell for outbound url is empty. (Selenium to check?)
#todo: handle null url in javascript
#todo: absolute way of handling url  :: Is there a signature?
#todo: add 0.json which stores null values for the files + notify curators + email address (lux@mechanobio.info)

import sqlite3 as lite
import sys

con = lite.connect('MCMBTEST.sqlite')

URL_TO_FILE = {
    "tableName" : "URL_Mapping",       #orginal: URL_Mapping
    "id"        : "Id",             #unique Id as key
    "fileName"  : "File_Name",      #name of downloaded file
    "url"       : "Url"             #url by which the file is downloaded from

    }

EXCEL_TO_DB = {                     # created to populate all the genes found in each .csv file along with their URL
    "tableName" : "Excel_To_DB",
    "fileName"  : "File_Name",      #name of downloaded file
    "geneId"    : "Gene_Id",         #Gene ID obtained from the excel file. For the rest, refer to the column headers in the downloaded excel files
    "geneName"  : "Gene_Name",
    "uniProtId" : "Uni_Prot_Id",
    "url"       : "Url",            #url by which the file is downloaded from
    "urlKey"    : "Url_Key",         #an integer representation that mappings unqiuely to URL, same as the "_#.csv" number found in the filenames of csv files
    "moleculeName" : "Molecule_Name",
    "proteinName" : "Official_Protein_Name"

}

#Note: Note all fields listed here are used in the table creation, old db = MCMB_X_HOMOLO
MCMB_X_HOMOLO = {                   #Ultimate table which contains all the necessary information for homo-gene out-link for each page.
    "tableName" : "MCMB_X_HOMOLO",
    "urlKey"    : "Url_Key",         #an integer representation that mappings unqiuely to URL, same as the "_#.csv" number found in the filenames of csv files
    "geneId"    : "Gene_Id",         #Gene ID obtained from the excel file. For the rest, we are using this to join Homologene and Excel_To_DB
    "hId"       : "HID",
    "taxoID"    : "Taxonomy_ID",
    "geneName"  : "Gene_Name",      #It's called Gene_Symbol in homologene
    "mcmbUrl"   : "MCMB_Url",            #url by which the file is downloaded from
    "outBoundUrl" : "OutBound_URL",   #URL that links to external model organism sites
    "geneSymbol": "Gene_Symbol",
    "geneKey"   : "Gene_Key",       #Stores the value(gene_id) of the gene that is originally present on the page, used for javascript identification

    #not used
    "proteinGI" : "Protein_GI",
    "uniProtId" : "Uni_Prot_Id",
    "moleculeName" : "Molecule_Name",
    "proteinName" : "Official_Protein_Name"     #From MCMB
}

HOMOLOGENE = {
    "tableName" : "homologene",
    "hId"       : "HID",
    "taxoID"    : "Taxonomy_ID",
    "geneId"    : "Gene_ID",
    "geneSymbol": "Gene_Symbol",
    "proteinGI" : "Protein_GI",
    "proteinAccession" : "Protein_Accession"
}


class MCMBXHomologeneJoiner():

    urlKeyList = []     #list to store the list of URL used for adhoc querying

    def __init__(self):
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS %s" % MCMB_X_HOMOLO['tableName'])
            createTableTuple = (MCMB_X_HOMOLO["tableName"], MCMB_X_HOMOLO["urlKey"], MCMB_X_HOMOLO["geneKey"], MCMB_X_HOMOLO['geneId'], MCMB_X_HOMOLO["geneSymbol"]
                                , MCMB_X_HOMOLO['hId'], MCMB_X_HOMOLO["taxoID"], MCMB_X_HOMOLO["geneName"], MCMB_X_HOMOLO["outBoundUrl"], MCMB_X_HOMOLO["mcmbUrl"])
            cur.execute("CREATE TABLE %s(%s INT, %s INT, %s INT, %s VARCHAR,%s INT, %s INT, %s VARCHAR, %s VARCHAR, %s VARCHAR)" % createTableTuple)
            print "SpiderRawDB: Written to ", MCMB_X_HOMOLO["tableName"]
        self.getUrlKeyList()

    def joinTables(self):
        for key in self.urlKeyList:
            self.populateTable(key)

    def populateTable(self, urlKey):
        # this method takes in a urlKey and use a manual join to populate MCMB_X_HOMOLO by first getting the taxo_id of all the genes listed in a page and
        # then get the gene_id (X) of all homologous gene and lastly use X to generate a url (self.getOutBoundUrl) to the model organism webpage

        listOfDBrows = []               # list of DB rows for output to Json

        with con:
            cur = con.cursor()

            queryTupleExcel = (EXCEL_TO_DB["geneId"], EXCEL_TO_DB["geneName"], EXCEL_TO_DB["url"], EXCEL_TO_DB["moleculeName"] ,
                          EXCEL_TO_DB['tableName'], EXCEL_TO_DB["urlKey"], urlKey)
            cur.execute("SELECT %s, %s, %s, %s FROM %s WHERE %s=%s" % queryTupleExcel)
            print "\n\nFrom Database: " + URL_TO_FILE["tableName"] + " | Querying all homolodata for url: " + str(urlKey)
            geneListInUrl = cur.fetchall()           #This will return the list of genes for a particular URLkey and drain the query object

            for gene in geneListInUrl:          #each gene is a tuple of (geneID, geneName, URL, moleculeName)

                #first we need to get hID
                queryTupleHomoId = (HOMOLOGENE['hId'], HOMOLOGENE["tableName"], HOMOLOGENE["geneId"], gene[0])
                cur.execute("SELECT %s FROM %s WHERE %s=%s" % queryTupleHomoId)

                homologenesID = cur.fetchall()
                if len(homologenesID) != 0 and len(homologenesID[0]) != 0:
                    homologenesID = homologenesID[0][0]     #aka. hId.  |  It's stored as the first item of the tuple of the returned list
                else:
                    continue

                print "MCMBXHomologeneJoiner: JoinTables: Gene_ID = " + str(gene[0]) + " | HomoloID = " + str(homologenesID)
                queryTupleHomo = (HOMOLOGENE["geneId"], HOMOLOGENE["taxoID"], HOMOLOGENE["geneSymbol"],HOMOLOGENE["tableName"], HOMOLOGENE["hId"], homologenesID)
                cur.execute("SELECT %s, %s, %s FROM %s WHERE %s=%s" % queryTupleHomo)

                homologenes = cur.fetchall()

                for homolog in homologenes:         # homolog = ( geneId, taxoID, geneSymbol)
                    outboundurl = self.getOutBoundUrl(homolog[1], homolog[0], homolog[2])
                    homologRowValues = (urlKey, gene[0], homolog[0], homolog[2],homologenesID, homolog[1], gene[1], outboundurl,gene[2])
                                    #  (urlkey, geneKey, geneID,     geneSymbol, HID,          taxoID,     geneName,  outboundURL, MCMBURL)
                    cur.execute("INSERT INTO " + MCMB_X_HOMOLO["tableName"] + " (" + MCMB_X_HOMOLO["urlKey"] + ", " + MCMB_X_HOMOLO["geneKey"] + ", " + MCMB_X_HOMOLO["geneId"]
                                + ", " + MCMB_X_HOMOLO["geneSymbol"] + ", " + MCMB_X_HOMOLO["hId"] + ", " + MCMB_X_HOMOLO["taxoID"] + ", " + MCMB_X_HOMOLO["geneName"] + ", "
                                + MCMB_X_HOMOLO["outBoundUrl"] + ", " + MCMB_X_HOMOLO["mcmbUrl"]
                                 + " ) VALUES (?,?,?,?,?,?,?,?,?)", homologRowValues)
                    print "Gene Added:", homolog[2], homolog[1], homolog[0], outboundurl
                    listOfDBrows.append(homologRowValues)

                print "Homologenes:", homologenes
        self.saveToJson(urlKey, listOfDBrows)

    def saveToJson(self, urlKey, rows):

        fullGenelist = []

        geneSet = []        # a set genes by geneKey
        currentGeneKey = rows[0][1]
        print "Current Genekey:", currentGeneKey

        for row in rows:

            print "Next row:"
            gene = {    MCMB_X_HOMOLO["geneKey"]        : row[1],
                        MCMB_X_HOMOLO["geneId"]         : row[2],
                        MCMB_X_HOMOLO["geneSymbol"]     : row[3],
                        MCMB_X_HOMOLO["taxoID"]         : row[5],
                        MCMB_X_HOMOLO["geneName"]       : row[6],
                        MCMB_X_HOMOLO["outBoundUrl"]    : row[7]
                    }
            if row[1] == currentGeneKey:
                geneSet.append(gene)
            else:
                currentGeneKey = row[1]
                fullGenelist.append(geneSet)
                geneSet = [gene]
            print gene

        fullGenelist.append(geneSet)

        import json
        json_string = json.dumps(fullGenelist)
        json_string = "populateDropDown('" + json_string + "')"
        out_file = open("json/" + str(urlKey) + ".json", "wt")
        out_file.write(json_string)
        out_file.close()
        print "Json String:", json_string


    def getOutBoundUrl(self, tax_id, geneId, geneSymbol):
#        print "getOutBoundUrl: Tax_Id", tax_id, "GeneId: ", geneId, "geneSymbol", geneSymbol
        geneId = str(geneId)
        url = ""
        if tax_id == 3702:          # Arabidopsis thaliana
            url ="http://gbrowse.arabidopsis.org/cgi-bin/gbrowse/arabidopsis/?name=" + geneSymbol
        elif tax_id == 4530:           # Oryza sativa (Rice)
            url = "http://www.ncbi.nlm.nih.gov/gene/?term="  + geneId
#            url = "http://plants.ensembl.org/Oryza_sativa/Gene/Summary?g=" + geneId
        elif tax_id == 4896:        # Schizosaccharomyces pombe (Fisson Yeast)
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://fungi.ensembl.org/Schizosaccharomyces_pombe/Gene/Summary?g=" + geneId
        elif tax_id == 4932:        # Baker's Yeast
            url = "http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name=" + geneSymbol
        elif tax_id == 5141:        # Red Bread Mold
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://fungi.ensembl.org/Neurospora_crassa/Gene/Summary?g=" + geneId
        elif tax_id == 5833:        # Plasmodium falciparum
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://protists.ensembl.org/Plasmodium_falciparum/Gene/Summary?g=" + geneId
        elif tax_id == 6239:        # C.elegans
            url = "http://www.wormbase.org/db/gb2/gbrowse/c_elegans/?name=" + geneSymbol
        elif tax_id == 7165:        # Anopheles gambiae, African malaria mosquito
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://metazoa.ensembl.org/Anopheles_gambiae/Gene/Summary?g=" + geneId
        elif tax_id == 7227:        # Drosophila melanogaster
            url ="http://flybase.org/cgi-bin/gbrowse/dmel/?name=" + geneSymbol
        elif tax_id == 7955:        # Zebra fish; LOC{d}+ genes cannot be found
            url ="http://zfin.org/cgi-perl/gbrowse/current/?name=" + geneSymbol
        elif tax_id == 9544:        # 9544 Macaca mulatta
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
        elif tax_id == 9031:        # Gallus gallus chicken #has uscs
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://ensembl.org/Gallus_gallus/Gene/Summary?g=" + geneId
        elif tax_id == 9598:        # Pan troglodytes, chimpanzee
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://ensembl.org/Pan_troglodytes/Gene/Summary?g=" + geneId
        elif tax_id == 9606:        # Homo Spiens
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://ensembl.org/Homo_sapiens/Gene/Summary?g=" + geneSymbol
        elif tax_id == 9615:        # Canis lupus familiaris, dog
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://ensembl.org/Canis_familiaris/Gene/Summary?g=" + geneId
        elif tax_id == 9913:        # Bos Tarus
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://ensembl.org/Bos_taurus/Gene/Summary?g=" + geneId
        elif tax_id == 10090:       #Mus musculus
            url = "http://gbrowse.informatics.jax.org/cgi-bin/gbrowse/mouse_current/?name=" + geneSymbol
        elif tax_id == 10116:       #Rattus norvegicus, Norway Rat
            url = "http://www.rgd.mcw.edu/fgb2/gbrowse/rgd_904/?name=" + geneSymbol #
        elif tax_id == 28985:       #Kluyveromyces lactis
            url = "http://www.genolevures.org/cgi-bin/gbrowse/genomes/?name=" + geneSymbol
        elif tax_id == 33169:       #Ashbya gossypii, type of fungi; http://agd.vital-it.ch/ uses proprietary non callable view
            url = "http://fungi.ensembl.org/Ashbya_gossypii/Gene/Summary?g=" + geneId
        elif tax_id == 148305:      #Magnaporthe grisea, used pubmed
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
#            url = "http://fungi.ensembl.org/Magnaporthe_oryzae/Gene/Summary?g=" + geneId
        elif tax_id == 284811:      #Ashbya gossypii ATCC
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId
        elif tax_id == 318829:      #Magnaporthe oryzae
            url = "http://www.ncbi.nlm.nih.gov/gene/?term=" + geneId

        return url


    def modelOrganismConsistencyTest(self):
        pass
#        Select Distinct Taxonomy_ID from Homologene       this statement will check if all the model organism have been represented in the dic for outbound URL

    def getUrlKeyList(self):
        inFile = open("urlKey.txt", "rt")
        for key in inFile.readline().split(","):
            self.urlKeyList.append(int(key))
        inFile.close()
        print self.urlKeyList





#if __name__ == '__main__':
#
##    import os           # clear the directory of previous json
##    from glob import glob
##    for f in glob ('json/*.json'):
##        os.unlink (f)
#
#    mxhJoiner = MCMBXHomologeneJoiner()
#    mxhJoiner.joinTables()

    print "Complete"
#    mxhJoiner.populateTable(274)   #for debugging








# Populates the data from each excel file into a table
class ExcelToDB():

    urlKeyList = []     #list to store the list of URL used for adhoc querying
    urlKeyPairs = {}

    #Not populating protein name and type because they have commas in their terms.
    def __init__(self):
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS %s" % EXCEL_TO_DB['tableName'])
            createTableTuple = (EXCEL_TO_DB["tableName"], EXCEL_TO_DB["urlKey"], EXCEL_TO_DB['geneId'], EXCEL_TO_DB["geneName"],
                                EXCEL_TO_DB["uniProtId"], EXCEL_TO_DB["moleculeName"], EXCEL_TO_DB["url"], EXCEL_TO_DB["fileName"])
#            createTableTuple = (EXCEL_TO_DB["tableName"], EXCEL_TO_DB['geneId'] ,EXCEL_TO_DB["url"], EXCEL_TO_DB["geneName"],
#                                EXCEL_TO_DB["uniProtId"], EXCEL_TO_DB["moleculeName"], EXCEL_TO_DB["proteinName"],
#                                EXCEL_TO_DB["fileName"])
            cur.execute("CREATE TABLE %s(%s INT, %s INT, %s VARCHAR, %s VARCHAR, %s VARCHAR, %s VARCHAR, %s VARCHAR)" % createTableTuple)
            print "SpiderRawDB: Written to ", EXCEL_TO_DB["tableName"]

    def populateDB(self):

        con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')          #this command ignores of unusual unicode character encoding which may be present in the fies
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM %s" % URL_TO_FILE['tableName'])
            fileList = cur.fetchall()
            print "Excel To DB: populateDB:"


            for file in fileList:
                print file[1]
                inFile = open("../../downloadedFiles/" + file[1], "rt")
                next(inFile)
                urlKey = self.getUrlKeyFromCsvFileName(file[1])
                self.urlKeyList.append(urlKey)
                print file

                self.urlKeyPairs[str(file[2]).replace("https://sites.google.com/a/mechanobio.info/mbinfo/Home/", "")] = file[0]             # saving urlKey - Url pairs to dic --> For json conversion
                for line in inFile:
                    line = line.split(",")
                    line[1] = filter(lambda x: x.isdigit(), line[1])  #removing all none numbers from the gene_id string
                    row = (urlKey, line[1], line[0], line[2], line[3], file[2], file[1])
                    print row
                    cur.execute("INSERT INTO " + EXCEL_TO_DB["tableName"] + " VALUES(?,?,?,?,?,?,?)", row)

        self.writeUrlKeyPairsToJson()


    def getUrlKeyFromCsvFileName(self, filename):
        print "filename:", filename
        filename = str(filename)[::-1].rsplit("_")[0]         #rightmost part after the file name will return ##.csv, am inverting the string, because its safest to get from the back
        urlKey = filename[::-1].replace(".csv", "")         #invert again and remove .csv by replacing it with ''
        print urlKey
        return int(urlKey)
    
    def writeUrlKeyToFile(self):
       
        out_file = open("urlKey.txt", "wt")
        listString = ",".join(["%s" % key for key in self.urlKeyList])
#        print listString
        out_file.write(listString)
        out_file.close()

    def writeUrlKeyPairsToJson(self):
        import json

        print self.urlKeyPairs
        data_string = json.dumps(self.urlKeyPairs)
        data_string = "setURLKey('" + data_string + "')"
        out_file = open("json/UrlKeyPairs.json", "wt")
        out_file.write(data_string)
        out_file.close()


#
#if __name__ == '__main__':
#
#    excelToDB = ExcelToDB()
#    excelToDB.populateDB()
#    excelToDB.writeUrlKeyToFile()








# Stores raw item crawled by the spider to DB
class SpiderRawToDB():

    spiderURLFileItem = []

    def __init__(self):
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS %s" % URL_TO_FILE['tableName'])
            createTableTuple = (URL_TO_FILE["tableName"], URL_TO_FILE["id"], URL_TO_FILE["fileName"], URL_TO_FILE["url"])
            cur.execute("CREATE TABLE %s(%s INT, %s VARCHAR, %s VARCHAR)" % createTableTuple)
            print "SpiderRawDB: Written to", URL_TO_FILE["tableName"]


            # Here we will attemp to update the entire table in one shot to minimise db read/write. This is feasible because
            # the number of files is relatively little  <1000~

    def addItem(self, spiderFileURLItem):

        print "SpiderRawToDB.addItem: " + str(spiderFileURLItem)

        with con:
            cur = con.cursor()
            for item in spiderFileURLItem:

                item[2] = self.cleanUrl(item[2], item[1])
                print item

                cur.execute("INSERT INTO " + URL_TO_FILE["tableName"] + " VALUES(?,?,?)", item)

            con.commit()

            cur = con.cursor()
            cur.execute("SELECT * FROM %s" % URL_TO_FILE['tableName'])
            print "From Database: %s" % URL_TO_FILE["tableName"]
            rows = cur.fetchall()
            for row in rows:
                print row

    def cleanUrl(self, url, filename):
        #URL contains the .csv extension so it must be clean to point to the page, by removing the filename from the end
        filename = str(filename).split("_")[0]; filename = filename[::-1]
        fileNameIndex = str(url[::-1]).find(filename)
        return url[:-(fileNameIndex + len(filename))]

    def readSpiderSessionFile(self):

        inFile = open("../../downloadedFiles/listOfCsv.txt", "rt")

        for line in inFile:
            items = line.split(",")
            items[2] = items[2][:-2]
            self.spiderURLFileItem.append(items)
        inFile.close()






if __name__ == '__main__':
    import os           # clear the directory of previous json
    from glob import glob
    for f in glob ('json/*.json'):
        os.unlink (f)

    #    Test for SpiderRawToDB
    spiderRaw = SpiderRawToDB()
    spiderRaw.readSpiderSessionFile()
    spiderRaw.addItem(spiderRaw.spiderURLFileItem)

    excelToDB = ExcelToDB()
    excelToDB.populateDB()
    excelToDB.writeUrlKeyToFile()

    mxhJoiner = MCMBXHomologeneJoiner()
    mxhJoiner.joinTables()

    with open("json/0.json", "wt") as f:    # recreate 0.json file
        f.writelines("populateDropDown('" + '[[{"Gene_Id": 0, "Gene_Symbol": "None", "Gene_Key": 0, "Taxonomy_ID": 0, "OutBound_URL": "#", "Gene_Name": "This Page Does not contain any gene .csv file"}]]' + "')")

#    spiderRaw.addItem(
#        [
#          (1, "a_001.txt", "http://example.com/02"),
#          (2, "a_002.txt", "http://example.com/dsds"),
#          (3, "a_002.txt", "http://example.com/dsds")
#        ]
#    )
#
#    spiderRaw.addItem(
#        [
#            (9, 'IPbasicdescription_proteins_9.csv', 'https://sites.google.com/a/mechanobio.info/mbinfo/Home/Dynamic-Structures-in-Mechanosensing/invadopodia/IPbasicdescription_proteins.csv?attredirects=0&d=1'),
#            (10, 'FMMyosinX_proteins_10.csv', 'https://sites.google.com/a/mechanobio.info/mbinfo/Home/Dynamic-Structures-in-Mechanosensing/functionalmodule_myosinx/FMMyosinX_proteins.csv?attredirects=0&d=1')
#        ]
#    )
