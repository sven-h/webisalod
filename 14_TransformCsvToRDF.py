import csv
import ujson
from urllib import parse
import gzip
import time
from io import StringIO
import datetime
from rdflib import Graph, Literal, Namespace, URIRef, XSD, RDFS, RDF, OWL
from rdflib.namespace import VOID, FOAF, DCTERMS

from utilwebisadb import set_csv_field_size


#### write t-box

def write_t_box(rdf_file):
    PROV = Namespace("http://www.w3.org/ns/prov#")
    BASE = Namespace("http://isadb.webdatacommons.org/")
    BASEONT = Namespace("http://isadb.webdatacommons.org/ontology#")
    OV = Namespace("http://open.vocab.org/terms/")

    g = Graph()

    #Ontology

    g.add((BASEONT[""], RDF.type, OWL.Ontology))
    g.add((BASEONT[""], RDFS.label, Literal("WebIsALOD Ontology")))
    g.add((BASEONT[""], RDFS.comment, Literal("WebIsALOD ontology describing hypernymy relations with rich provenance information.")))
    g.add((BASEONT[""], OWL.versionInfo, Literal("1.0")))
    g.add((BASEONT[""], DCTERMS.created, Literal('2017-03-17', datatype=XSD.date)))
    # g.add((BASEONT[""], OWL.imports, ))

    g.add((BASEONT[""], OV.defines, BASEONT.hasRegex))
    g.add((BASEONT[""], OV.defines, BASEONT.hasType))
    g.add((BASEONT[""], OV.defines, BASEONT.hasHead))
    g.add((BASEONT[""], OV.defines, BASEONT.hasPreModifier))
    g.add((BASEONT[""], OV.defines, BASEONT.hasPostModifier))
    g.add((BASEONT[""], OV.defines, BASEONT.hasPidSpread))
    g.add((BASEONT[""], OV.defines, BASEONT.hasPldSpread))
    g.add((BASEONT[""], OV.defines, BASEONT.hasFrequency))
    g.add((BASEONT[""], OV.defines, BASEONT.hasConfidence))

    g.add((BASEONT.hasRegex, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasRegex, RDFS.label, Literal("has regex")))
    g.add((BASEONT.hasRegex, RDFS.comment, Literal("Java regex value for matching this pattern.")))
    g.add((BASEONT.hasRegex, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasRegex, RDFS.range, XSD.string))

    g.add((BASEONT.hasType, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasType, RDFS.label, Literal("has type")))
    g.add((BASEONT.hasType, RDFS.comment, Literal("the type of the pattern describing the format.")))
    g.add((BASEONT.hasType, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasType, RDFS.range, XSD.string))

    g.add((BASEONT.hasHead, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasHead, RDFS.label, Literal("has head")))
    g.add((BASEONT.hasHead, RDFS.comment, Literal(
        "The head noun of the concept.")))
    g.add((BASEONT.hasHead, RDFS.domain, OWL.Class))
    g.add((BASEONT.hasHead, RDFS.range, XSD.string))

    g.add((BASEONT.hasPreModifier, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasPreModifier, RDFS.label, Literal("has pre modifier")))
    g.add((BASEONT.hasPreModifier, RDFS.comment, Literal("The pre modifier of the concept.")))
    g.add((BASEONT.hasPreModifier, RDFS.domain, OWL.Class))
    g.add((BASEONT.hasPreModifier, RDFS.range, XSD.string))

    g.add((BASEONT.hasPostModifier, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasPostModifier, RDFS.label, Literal("has post modifier")))
    g.add((BASEONT.hasPostModifier, RDFS.comment, Literal("The post modifier of the concept.")))
    g.add((BASEONT.hasPostModifier, RDFS.domain, OWL.Class))
    g.add((BASEONT.hasPostModifier, RDFS.range, XSD.string))

    g.add((BASEONT.hasPidSpread, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasPidSpread, RDFS.label, Literal("has pid spread")))
    g.add((BASEONT.hasPidSpread, RDFS.comment,
           Literal("The amount of distinct patterns with which the concept relation was found.")))
    g.add((BASEONT.hasPidSpread, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasPidSpread, RDFS.range, XSD.integer))

    g.add((BASEONT.hasPldSpread, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasPldSpread, RDFS.label, Literal("has pld spread")))
    g.add((BASEONT.hasPldSpread, RDFS.comment, Literal(
        "The amount of distinct pay level domains where the concept relation was found.")))
    g.add((BASEONT.hasPldSpread, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasPldSpread, RDFS.range, XSD.integer))

    g.add((BASEONT.hasFrequency, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasFrequency, RDFS.label, Literal("has frequency")))
    g.add((BASEONT.hasFrequency, RDFS.comment, Literal("The absolute number of hyponym-hypernym pair occurrences.")))
    g.add((BASEONT.hasFrequency, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasFrequency, RDFS.range, XSD.integer))

    g.add((BASEONT.hasConfidence, RDF.type, OWL.DatatypeProperty))
    g.add((BASEONT.hasConfidence, RDFS.label, Literal("has confidence")))
    g.add((BASEONT.hasConfidence, RDFS.comment, Literal(
        "Confidence for maschine learning approaches to score resources.")))
    g.add((BASEONT.hasConfidence, RDFS.domain, PROV.Entity))
    g.add((BASEONT.hasConfidence, RDFS.range, XSD.float))



    # VOID
    ds = BASE['.well-known/void']
    g.add((ds, RDF.type, VOID.Dataset))
    g.add((ds, FOAF.homepage, URIRef('http://webdatacommons.org/isadb/index.html')))
    g.add((ds, DCTERMS.title, Literal('WebIsALOD')))
    g.add((ds, RDFS.label, Literal('WebIsALOD')))
    g.add((ds, DCTERMS.description, Literal(
        'WebIsALOD is a Linked Open Data version of the IsA database, containing 11.7M hyernymy relations, each provided with rich provenance information.')))
    g.add((ds, DCTERMS.created, Literal('2017-03-17', datatype=XSD.date)))
    g.add((ds, DCTERMS.source, URIRef('http://webdatacommons.org/isadb/')))
    g.add((ds, DCTERMS.creator, Literal('Julian Seitner')))
    g.add((ds, DCTERMS.publisher, Literal('Sven Hertling')))
    g.add((ds, DCTERMS.publisher, Literal('Heiko Paulheim')))
    g.add((ds, DCTERMS.contributor, Literal('Christian Bizer')))
    g.add((ds, DCTERMS.contributor, Literal('Kai Eckert')))
    g.add((ds, DCTERMS.contributor, Literal('Stefano Faralli')))
    g.add((ds, DCTERMS.contributor, Literal('Robert Meusel')))
    g.add((ds, DCTERMS.contributor, Literal('Heiko Paulheim')))
    g.add((ds, DCTERMS.contributor, Literal('Simone Paolo Ponzetto')))
    g.add((ds, VOID.sparqlEndpoint, URIRef('http://isadb.webdatacommons.org/sparql')))
    g.add((ds, VOID.exampleResource, URIRef('http://isadb.webdatacommons.org/concept/_Gmail_')))
    #g.add((ds, VOID.dataDump, URIRef('http://isadb.webdatacommons.org/sparql')))


    #further information about the patterns

    name_to_paper_uri = {
        "Hearst": "http://dx.doi.org/10.3115/992133.992154",
        # "Dominic":""
        "Ponzetto": "http://dx.doi.org/10.1016/j.artint.2011.01.003", # <http://dblp.uni-trier.de/rec/journals/ai/PonzettoS11>     <http://dblp.org/rec/journals/ai/PonzettoS11>
        "Orna-Montesinos": "http://dx.doi.org/10.14198/raei.2011.24.09",
        "Ando": "http://www.lrec-conf.org/proceedings/lrec2004/pdf/80.pdf",# <http://dblp.uni-trier.de/rec/conf/lrec/AndoSI04>    <http://dblp.org/rec/conf/lrec/AndoSI04>
        "Klaussner": "http://aclweb.org/anthology-new/R/R11/R11-2016.pdf" # <http://dblp.uni-trier.de/rec/conf/ranlp/KlaussnerZ11>  <http://dblp.org/rec/conf/ranlp/KlaussnerZ11>
    }

    pattern_id_to_regex = dict()
    with open("pattern_regex.csv") as p_regex:
        for row in csv.DictReader(p_regex):
            pattern_id_to_regex[row["pid"]] = row["pattern"]

    with open("pattern_details.csv") as p_details:
        for row in csv.DictReader(p_details):
            pid_activity = BASE["pattern/extract_{}_activity".format(row["ID"])]
            pattern = BASE["pattern/pattern_{}".format(row["ID"])]

            g.add((pid_activity, RDF.type, PROV.Activity))
            g.add((pid_activity, PROV.used, pattern))

            g.add((pattern, RDF.type, PROV.Entity))
            g.add((pattern, RDFS.label, Literal(row["ID"])))
            g.add((pattern, RDFS.comment, Literal(row["Pattern"])))
            g.add((pattern, BASEONT.hasRegex, Literal(pattern_id_to_regex[row["ID"]])))
            g.add((pattern, BASEONT.hasType, Literal(row["Type"])))

            if row["Source"] in name_to_paper_uri:
                g.add((pattern, PROV.wasDerivedFrom, URIRef(name_to_paper_uri[row["Source"]])))


    # write everything to file
    with gzip.open(rdf_file, "w") as output_file:
        output_file.write(b"\n".join(sorted(g.serialize(format='nt').splitlines())))



#### write a-box

def get_local_name_for_resource(premod, lemma, postmod):
    return parse.quote_plus("_".join([premod, lemma, postmod]))#join with underscore so that it is clear where premod lemma and postmod is
    #return slugify("_".join([premod, lemma, postmod]))
    #return "_".join([slugify(premod), slugify(lemma), slugify(postmod)])

# http://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex-in-python
# http://stackoverflow.com/questions/9907085/python-using-re-sub-to-replace-multiple-substring-multiple-times
def escape_literals(str):
    # search for rdf literal escape
    # from http://www.rubydoc.info/github/ruby-rdf/rdf/RDF%2FLiteral%3Aescape#
    return str.replace('\\', '\\\\').replace('\t', '\\t').replace('\b', '\\b').replace('\n', '\\n').replace('\r', '\\r').replace('\f', '\\f').replace('"', '\\"')


def split_semicolon(str):
    return [x for x in str.split(';') if x]

#@profile
def get_named_graph_rdf_representation(row):
    graph = row[0]
    full_instance, full_class = row[1], row[2]
    frequency, pidspread, pldspread = row[3], row[4], row[5]
    ipremod, instanceLemma, ipostmod = row[6], row[7], row[8]
    cpremod, classLemma, cpostmod = row[9], row[10], row[11]
    pids = split_semicolon(row[12])
    sentence_metas = ujson.loads(row[14])#row 13 is pld which is also contained in row[14]
    confidence = row[16]
    instance_dbpedia_mapping = ujson.loads(row[19])
    clazz_dbpedia_mapping = ujson.loads(row[21])
    yago_page_mapping = row[23]
    yago_clazz_mapping = row[24]


    with StringIO() as out:
        base = "http://webisa.webdatacommons.org/"
        prov = "http://www.w3.org/ns/prov#"
        rdfs = "http://www.w3.org/2000/01/rdf-schema#"
        rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        skos = "http://www.w3.org/2004/02/skos/core#"
        owl = "http://www.w3.org/2002/07/owl#"

        full_instance_uri = get_local_name_for_resource(ipremod, instanceLemma, ipostmod)
        full_class_uri = get_local_name_for_resource(cpremod, classLemma, cpostmod)

        out.write("""<{base}concept/{full_instance_uri}> <{skos}broader> <{base}concept/{full_class_uri}>  <{base}prov/{graph}>.
<{base}concept/{full_instance_uri}> <{rdfs}label> "{full_instance_label}".
<{base}concept/{full_instance_uri}> <{base}ontology#hasHead> "{instanceLemma}".
<{base}concept/{full_class_uri}> <{rdfs}label> "{full_class_label}".
<{base}concept/{full_class_uri}> <{base}ontology#hasHead> "{classLemma}".
""".format(base=base,
           rdf=rdf,
           rdfs=rdfs,
           skos=skos,
           full_instance_uri=full_instance_uri,
           full_class_uri=full_class_uri,
           graph=graph,
           full_instance_label=escape_literals(full_instance),
           instanceLemma = escape_literals(instanceLemma),
           full_class_label=escape_literals(full_class),
           classLemma=escape_literals(classLemma)))

        if ipremod.strip():
            out.write('<{base}concept/{full_instance_uri}> <{base}ontology#hasPreModifier> "{ipremod}".\n'
                      .format(base=base,full_instance_uri=full_instance_uri,ipremod = escape_literals(ipremod)))

        if ipostmod.strip():
            out.write('<{base}concept/{full_instance_uri}> <{base}ontology#hasPostModifier> "{ipostmod}".\n'
                      .format(base=base,full_instance_uri=full_instance_uri,ipostmod = escape_literals(ipostmod)))

        if cpremod.strip():
            out.write('<{base}concept/{full_class_uri}> <{base}ontology#hasPreModifier> "{cpremod}".\n'
                      .format(base=base,full_class_uri=full_class_uri,cpremod = escape_literals(cpremod)))

        if cpostmod.strip():
            out.write('<{base}concept/{full_class_uri}> <{base}ontology#hasPostModifier> "{cpostmod}".\n'
                      .format(base=base,full_class_uri=full_class_uri,cpostmod = escape_literals(cpostmod)))

        out.write(
"""<{base}prov/{graph}> <{rdf}type> <{prov}Entity>.
<{base}prov/{graph}> <{base}ontology#hasPidSpread> "{pidspread}"^^<http://www.w3.org/2001/XMLSchema#integer>.
<{base}prov/{graph}> <{base}ontology#hasPldSpread> "{pldspread}"^^<http://www.w3.org/2001/XMLSchema#integer>.
<{base}prov/{graph}> <{base}ontology#hasFrequency> "{frequency}"^^<http://www.w3.org/2001/XMLSchema#integer>.
<{base}prov/{graph}> <{base}ontology#hasConfidence> "{confidence}"^^<http://www.w3.org/2001/XMLSchema#float>.
""".format(base=base,graph=graph,rdf=rdf,prov=prov,pidspread = pidspread,pldspread = pldspread,frequency = frequency, confidence=confidence))

        for pid in pids:
            out.write("<{base}prov/{graph}> <{prov}wasGeneratedBy> <{base}extract_{pid}_activity>.\n"
                .format(base=base, graph=graph, prov = prov,pid = pid))

        for (provid, sentence, pld) in sentence_metas:
            out.write(
"""<{base}prov/{graph}> <{prov}wasDerivedFrom> <{base}{provid}>.
<{base}{provid}> <{rdf}type> <{prov}Entity>.
<{base}{provid}> <{prov}value> "{sentence}".
<{base}{provid}> <{prov}wasQuotedFrom> <{pld}>.
""".format(base=base, rdf=rdf, prov=prov, graph=graph, provid=provid, sentence=escape_literals(sentence), pld=pld))

        for dbpedia_page in instance_dbpedia_mapping:
            out.write("<{base}concept/{full_instance_uri}> <{owl}sameAs> <{dbpedia_page}>.\n".format(
                base=base, full_instance_uri=full_instance_uri, owl=owl, dbpedia_page=dbpedia_page))
        for dbpedia_page in clazz_dbpedia_mapping:
            out.write("<{base}concept/{full_class_uri}> <{owl}sameAs> <{dbpedia_page}>.\n".format(
                base=base, full_class_uri=full_class_uri, owl=owl, dbpedia_page=dbpedia_page))

        if len(yago_page_mapping) > 0:
            out.write("<{base}concept/{full_instance_uri}> <{owl}sameAs> <{yago_page_mapping}>.\n".format(
                base=base, full_instance_uri=full_instance_uri, owl=owl, yago_page_mapping=yago_page_mapping))
        if len(yago_clazz_mapping) > 0:
            out.write("<{base}concept/{full_class_uri}> <{owl}sameAs> <{yago_clazz_mapping}>.\n".format(
                base=base, full_class_uri=full_class_uri, owl=owl, yago_clazz_mapping=yago_clazz_mapping))

        #for provid in split_semicolon(provids):
        #    out.write("<{base}{graph}> <{prov}wasDerivedFrom> <{base}{provid}>.\n"
        #        .format(base=base, graph=graph, prov = prov, provid = provid))

        #sameas links

        out.write("\n")

        return out.getvalue()

def write_a_box(csv_file, rdf_file):
    with open(csv_file) as f, gzip.open(rdf_file, "w") as output_file:
        reader = csv.reader(f)
        for i,row in enumerate(reader):
            output_file.write(get_named_graph_rdf_representation(row).encode('utf-8'))
            if i % 100000 == 0:
                print("{} - {}".format(datetime.datetime.now(), i))
            #if i > 100000:
            #    print(i)
            #    break



if __name__ == "__main__":
    set_csv_field_size()
    startTime = time.time()
    write_t_box('webisalod-ontology.nq.gz')
    write_a_box("webisa_1_final_with_mapping_yago.csv", "webisalod-instances.nq.gz")

    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format("Test", int(elapsedTime * 1000)))
    #rdflib
    #[Test] finished in 33803 ms
    #[Test] finished in 33033 ms
    #string processing
    #[Test] finished in  2140 ms
    #[Test] finished in  2144 ms