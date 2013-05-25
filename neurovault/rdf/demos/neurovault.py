__author__ = 'satra'

import os

from hashlib import md5
import rdflib
from rdflib.namespace import Namespace, NamespaceManager, RDF, FOAF, XSD
from rdflib import URIRef, BNode, Literal
from uuid import uuid1
from socket import getfqdn

db_location = os.path.join(os.getcwd(), 'database.ttl')

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
    nv = Namespace('http://neurovault.org/terms/0.1/core#')
    prov = Namespace('http://www.w3.org/prov/#')
    void = Namespace('http://rdfs.org/ns/void#')
    local = Namespace('#')
    namespace_manager = NamespaceManager(rdflib.Graph())
    namespace_manager.bind('nv', nv, override=False)
    namespace_manager.bind('prov', prov, override=False)
    namespace_manager.bind('void', void, override=False)
    namespace_manager.bind('', local, override=False)

    id = local[uuid1().hex]
    size = os.path.getsize(filename)
    location = URIRef('http://%s/image/%s' % (getfqdn(), id))
    g = rdflib.Graph()
    g.namespace_manager = namespace_manager
    if os.path.exists(db_location):
        g.parse(db_location, format='turtle')
    g.add((id, RDF.type, nv['image']))
    g.add((id, prov['atLocation'], location))
    g.add((id, nv['filesize'], Literal(size, datatype=XSD.integer)))
    g.add((id, nv['md5sum'], Literal(md5sum, datatype=XSD.string)))
    g.add((id, nv['originalName'], Literal(orig_name, datatype=XSD.string)))
    g.serialize(db_location, format='turtle')
    return {'id': id}

def get_image(id):
    out = {"name": myFile.filename,
                   "size": size,
                   "url": "%sfiles\/%s" % (url_prefix, md5sum)
            }
    return out
