var urltoGeneJson = "//storage.googleapis.com/static.mechanobio.info/gadget/json/";
var urltoURLKeyPairs = "//storage.googleapis.com/static.mechanobio.info/gadget/json/UrlKeyPairs.json";
var pathname = "Dynamic-Structures-in-Mechanosensing/integrin-syndecan-synergy/";
var geneSet = {};           //Stores the entire set of genes by geneKey
var geneKeyList = [];
var urlKeyList = {};        //Stores keyvalue pair for url
var urlParams = {}; //for holding url Parameters needed to detect the page

$(document).ready( function() {
    var titleAttr = $("div.mcmbTitle").attr("title");
    if (titleAttr == "notLoaded") {
        $("div.mcmbTitle").attr("title", "loaded");
        retrieveURLKeyPairs();
//                    console.log("Loading loading...");
    }



    //Setting up onchange or selector to display ensembl logo on change
    var ensemblURLMap = {
        "4530" : "http://plants.ensembl.org/Oryza_sativa/Gene/Summary?g=",
        "4896" : "http://fungi.ensembl.org/Schizosaccharomyces_pombe/Gene/Summary?g=",
        "5141" : "http://fungi.ensembl.org/Neurospora_crassa/Gene/Summary?g=",
        "5833" : "http://protists.ensembl.org/Plasmodium_falciparum/Gene/Summary?g=",
        "7165" : "http://metazoa.ensembl.org/Anopheles_gambiae/Gene/Summary?g=",
        "9031" : "http://ensembl.org/Gallus_gallus/Gene/Summary?g=",
        "9544"  :  "http://ensembl.org/Macaca_mulatta/Gene/Summary?g=",
        "9598" : "http://ensembl.org/Pan_troglodytes/Gene/Summary?g=",
        "9606" : "http://ensembl.org/Homo_sapiens/Gene/Summary?g=",
        "9615" : "http://ensembl.org/Canis_familiaris/Gene/Summary?g=",
        "9913" : "http://ensembl.org/Bos_taurus/Gene/Summary?g=",
        "148305": "http://fungi.ensembl.org/Magnaporthe_oryzae/Gene/Summary?g=",
        "284811"  :  0,
        "318829"    : "Magnaporthe oryzae"
    };

    $("#HomologsList").change( function(){
        var ensemblAnchor = $("#ensemblAnchor"),
            outGoingURL = $('#HomologsList :selected').val(),
            taxoId = $('#HomologsList :selected').attr("taxa"),
            ncbiSubstring = "gov/gene/?term=",
            indexOfNCBIURL = outGoingURL.indexOf(ncbiSubstring),
            geneId = outGoingURL.slice(indexOfNCBIURL + ncbiSubstring.length, outGoingURL.length);

//                    console.log("TaxoId:", taxoId);
        // if it's an NCBI url
        if( indexOfNCBIURL !== -1){
            var ensemblURL = ensemblURLMap[String(taxoId)]  + String(geneId);
//                       console.log("GeneId: ", geneId, "Url:", ensemblURL  );
            if (ensemblURLMap[String(taxoId)]){
                ensemblAnchor.show().attr("url", ensemblURL);
            }
            $("#gotoBtn").text("NCBI");
        } else {
            ensemblAnchor.hide();
            $("#gotoBtn").text("Go to GMOD / resource!");
        }
    });

});

function gotoEnsemblResource(){
    window.open($("#ensemblAnchor").attr("url") ,'_blank');
}

function gotoResource(){
    var outBoundUrl = $('#HomologsList').val();
    window.open(outBoundUrl,'_blank');
}

function onSelectHomoLogsList() {
    var outBoundUrl = $('#HomologsList').val();
//        console.log(outBoundUrl);
}

function refreshHomologList() {
    $('#HomologsList').empty();
    var selection = $('#MCMBGeneList').val(),
        selectionText = $('#MCMBGeneList option:selected').text();

    // Adding Uniprot linkout
    $('#HomologsList').append($("<option />").val("http://www.uniprot.org/uniprot/?query=" + selectionText + "&sort=score").text( "Uniprot:  " + selectionText));

    // Adding GeneMANIA entry
    $('#HomologsList').append($("<option />").val("http://genemania.org/link?o=9606&g=" + selectionText).text( "GeneMANIA:  " + selectionText));

    // Adding wikipedia linkout
    $('#HomologsList').append($("<option />").val("http://en.wikipedia.org/wiki/" + selectionText).text( "Wikipedia:  " + selectionText));

    // Adding Information Div
    $('#HomologsList').append($("<option />").val("#" + selectionText).text( "------ Genome Databases: ------" ));
    // Adding genome database selection
    var homologGeneSet = geneSet[selection];
    $.each(homologGeneSet, function() {
        $('#HomologsList').append($("<option />").val(this.OutBound_URL)
            .text( this.Gene_Symbol + "  (" + taxoDict[this.Taxonomy_ID] + ")"  )
            .attr("taxa",this.Taxonomy_ID ) //hack to include taxonoic id
        );
    });

}

function populateDropDown(json){
//        console.log(json.toString());
    var urlTable = $.parseJSON(json);

    $.each(urlTable, function() {           //organizes gene set first
        var geneKey = (this[0].Gene_Key).toString();
        geneKeyList.push(geneKey);
        geneSet[geneKey] = this;
    });

    $.each(geneKeyList, function() {
        var geneKey = this;
        var homoGroup = geneSet[geneKey];
        $('#MCMBGeneList').append($("<option />").val(geneKey).text(homoGroup[0].Gene_Name)); //+ " (ID:" + homoGroup[0].Gene_Key + ")"
    });
    refreshHomologList()
}

function loadGenesJson(){

    $.ajax({
        url: urltoGeneJson,
        dataType: 'jsonp',
        success: function(json){
            populateDropDown(json);
        }
    });
}

function retrieveURLKeyPairs(){
    $.ajax({
        url: urltoURLKeyPairs,
        dataType: 'jsonp',
        success: function (json){
            setURLKey(json);
        }
    });
}

function setURLKey(json) {
    urlKeyList = $.parseJSON(json);
    getMCMBUrl();
    var urlKey = urlKeyList[pathname];
//            urlKey = 0;
    if ( urlKey == undefined ) {
        console.warn('json file not found for ' + pathname);
    }
    urltoGeneJson = urltoGeneJson + urlKey + ".json";
//        console.log("URL to gene Json:" +urltoGeneJson);
    loadGenesJson();
}

function getMCMBUrl() {
//            var url = $("iframe.igm").attr("src"); //for debug
    var url = document.URL;

//        console.log("URL:", url);

    var subStringStart = "parent=",
        subStringEnd = "?previewAsViewer",
        subStringDeploy = "#st=";

    var indexStart = url.indexOf(subStringStart),
        viewerURLIndex = url.indexOf(subStringEnd);

    var indexEnd = ( viewerURLIndex != -1) ? viewerURLIndex : url.indexOf(subStringDeploy) ;

    var testSiteURL = url.slice(indexStart + subStringStart.length, indexEnd) + "/";

    //URL replacements
    var specificURL = testSiteURL.replace(/https?:\/\/sites\.google\.com\/a\/mechanobio\.info\/\w+\/Home\//, "");  //replacing url slug for draft site
    specificURL = specificURL.replace("http://www.mechanobio.info/Home/", "" );  //replaces slug that appears on safari and chrome

    pathname = specificURL;
//        console.log("This is the url: ",specificURL);

    return specificURL;
}


var taxoDict = {
    "0"     :  "None",
    "3702"  :  "Arabidopsis thaliana",
    "4530"  :  "Oryza sativa",
    "4896"  :  "Schizosaccharomyces pombe",
    "4932"  :  "Saccharomyces cerevisiae",
    "5141"  :  "Red Bread Mold",
    "5833"  :  "Plasmodium falciparum",
    "6239"  :  "C.elegans",
    "7165"  :  "Anopheles gambiae",
    "7227"  :  "Drosophila melanogaster",
    "7955"  :  "Danio rerio",
    "9031"  :  "Gallus gallus",
    "9544"  :  "Macaca mulatta",
    "9598"  :  "Pan troglodytes",
    "9606"  :  "Homo spiens",
    "9615"  :  "Canis lupus familiaris",
    "9913"  :  "Bos Tarus",
    "10090" :  "Mus musculus",
    "10116" :  "Rattus norvegicus",
    "28985" :  "Kluyveromyces lactis",
    "33169" :  "Ashbya gossypii",
    "148305":  "Magnaporthe grisea",
    "284811":  "Ashbya gossypii ATCC",
    "318829":  "Magnaporthe oryzae"
}

