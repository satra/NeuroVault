#REST webservice
import json
import os
import shutil
from socket import gethostname
import webbrowser

import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy import expose
import numpy as np

import lg_authority

from demos.neurovault import hash_infile, process_file

from mako.lookup import TemplateLookup, Template
from mako import exceptions


MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
FILE_DIR = os.path.join(os.getcwd(), 'files')

lookup = TemplateLookup(directories=[MEDIA_DIR], 
                        filesystem_checks=True, encoding_errors='replace',
                        strict_undefined=True)

if 'bips' in gethostname():
    url_prefix = '\/\/bips.incf.org:8080\/'
else:
    url_prefix = ''

class MyEncoder(json.JSONEncoder):
    def default(self, o):
        """Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).

        For example, to support arbitrary iterators, you could
        implement default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)

        """
        try:
            return super(MyEncoder, self).default(o)
        except TypeError:
            return ""

@lg_authority.groups('auth')
class BIPS(object):
    auth = lg_authority.AuthRoot()

    def __init__(self, *args, **kwargs):
        pass

    @expose
    def index(self):
        #with open(os.path.join(MEDIA_DIR, 'index.html')) as fp:
        #    msg = fp.readlines()
        indexTmpl = lookup.get_template("index.html")
        return indexTmpl.render()

    @expose
    def neurovault(self):
        demoTmpl = lookup.get_template("neurovault.html")
        return demoTmpl.render()

    @expose
    def testhandler(self, **kwargs):
        print kwargs
        myFile = kwargs['files[]'][0]
        print myFile.filename
        print dir(myFile)


    @expose
    def imageuploadhandler(self, **kwargs):
        if 'files[]' not in kwargs:
            return
        myFile = kwargs['files[]']
        md5sum = hash_infile(myFile.file)
        outfile = os.path.join(FILE_DIR, '%s' % md5sum)
        with open(outfile, 'wb') as fp:
            shutil.copyfileobj(myFile.file, fp)
        cherrypy.log('Saved file: %s' % outfile)
        if os.path.isfile(outfile):
            out = process_file(outfile, myFile.filename, md5sum)
        else:
            out = {}
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps([[out]])

def open_page():
    #pass
    webbrowser.open("http://127.0.0.1:8080")

def start_service():
    #configure ip address and port for web service
    if not os.path.exists(FILE_DIR):
        os.mkdir(FILE_DIR)
    config = {'/': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.getcwd(),
                    'tools.lg_authority.on': False,
                    'tools.lg_authority.site_storage': 'sqlite3',
                    'tools.lg_authority.site_storage_conf':
                            { 'file': os.path.abspath('test.db') }
                    },
              '/css': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': os.path.join(MEDIA_DIR, 'css')},
              '/js': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(MEDIA_DIR, 'js')},
              '/cors': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': os.path.join(MEDIA_DIR, 'cors')},
              '/img': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': os.path.join(MEDIA_DIR, 'img')},
              '/thumbnails': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': FILE_DIR},
              '/files': {'tools.staticdir.on': True,
                         'tools.staticdir.dir': FILE_DIR},
              '/scripts': {'tools.staticdir.on': True,
                         'tools.staticdir.dir': MEDIA_DIR},
              }
    #    #start webservice
    certfile = os.path.join(os.environ['HOME'], 'certinfo')
    if os.path.exists(certfile):
        cherrypy.log('Loading cert info: %s' % certfile)
        cherrypy.config.update(json.load(open(certfile)))
    else:
        cherrypy.log('Cert info unavailable')
    cherrypy.engine.subscribe('start', open_page)
    cherrypy.tree.mount(BIPS(), '/', config=config)
    cherrypy.engine.start()
    cherrypy.engine.block()
    #cherrypy.quickstart(BIPS())

if __name__ == "__main__":
    start_service()