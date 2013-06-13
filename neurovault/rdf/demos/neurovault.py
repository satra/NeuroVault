__author__ = 'satra'

import os

from hashlib import md5
import rdflib
from rdflib.namespace import Namespace, NamespaceManager, RDF, FOAF, XSD
from rdflib import URIRef, BNode, Literal
from uuid import uuid1
from socket import getfqdn

db_location = os.path.join(os.getcwd(), 'database.ttl')

nv = Namespace('http://neurovault.org/terms/0.1/core#')
nvid = Namespace('http://neurovault.org/id/')
prov = Namespace('http://www.w3.org/prov/#')
local = Namespace('#')
namespace_manager = NamespaceManager(rdflib.Graph())
namespace_manager.bind('nv', nv, override=False)
namespace_manager.bind('nvid', nvid, override=False)
namespace_manager.bind('prov', prov, override=False)
namespace_manager.bind('', local, override=False)

query_prefix = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX nv: <http://neurovault.org/terms/0.1/core#>
PREFIX nvid: <http://neurovault.org/id/>
PREFIX prov: <http://www.w3.org/prov/#>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX : <#>

"""

def hash_infile(afile, chunk_len=8192):
    """ Computes md5 hash of a file"""
    md5hex = None
    md5obj = md5()
    fp = afile
    while True:
        data = fp.read(chunk_len)
        if not data:
            break
        md5obj.update(data)
    fp.seek(0)
    md5hex = md5obj.hexdigest()
    return md5hex

def process_file(filename, orig_name, md5sum):
    hexid = uuid1().hex
    objid = URIRef(nvid[hexid])
    size = os.path.getsize(filename)
    location = URIRef('http://%s/image/%s' % (getfqdn(), hexid))
    g = rdflib.Graph()
    if os.path.exists(db_location):
        g.parse(db_location, format='turtle')
    g.namespace_manager = namespace_manager
    g.add((objid, RDF.type, nv['image']))
    g.add((objid, prov['atLocation'], location))
    g.add((objid, nv['filesize'], Literal(size, datatype=XSD.integer)))
    g.add((objid, nv['md5sum'], Literal(md5sum, datatype=XSD.string)))
    g.add((objid, nv['originalName'], Literal(orig_name, datatype=XSD.string)))
    g.serialize(db_location, format='turtle')
    return {'id': objid}

def get_image_ids():
    g = rdflib.Graph()
    if not os.path.exists(db_location):
        return {}
    g.parse(db_location, format='turtle')
    query = query_prefix + """
SELECT ?id WHERE { ?id a nv:image . }
"""
    results = g.query(query)
    out = []
    for row in results:
        out.append({'id': row[0].split('#')[-1]})
    return out

def get_id_rdf(objid):
    g = rdflib.Graph()
    if not os.path.exists(db_location):
        return {}
    g.parse(db_location, format='turtle')
    query = query_prefix + """
SELECT * WHERE { nvid:%s ?p ?o . }
""" % objid
    results = g.query(query)
    return results

def get_image(objid):
    g = rdflib.Graph()
    if not os.path.exists(db_location):
        return {}
    g.parse(db_location, format='turtle')
    query = query_prefix + """
SELECT ?url WHERE
{ :%s a nv:image .
  :%s prov:atLocation ?url }
""" % (objid, objid)
    results = g.query(query)
    out = {}
    for row in results:
        out = {'id': objid, 'atLocation': str(row[0])}
    return out
