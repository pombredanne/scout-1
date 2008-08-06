# Copyright (c) 2008 Pavol Rusnak
# see __init__.py for license details

import scout
import sys

try:
    satsolver = __import__('satsolver')
    import os
    from fnmatch import fnmatch
    from ConfigParser import SafeConfigParser
except:
    satsolver = None

class SolvParser(object):

    etcpath = '/etc/zypp/repos.d'
    solvfile = '/var/cache/zypp/solv/%s/solv'
    binpaths = ( '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/usr/games/', '/opt/kde3/bin/', '/opt/kde3/sbin/', '/opt/gnome/bin/', '/opt/gnome/sbin/' )

    def __init__(self):
        self.pool = satsolver.Pool()
        self.parser = SafeConfigParser()
        for repofile in filter(lambda x: fnmatch(x, '*.repo'), os.listdir(self.etcpath)):
            try:
                name = os.path.splitext(repofile)[0]
                self.parser.read( '%s/%s' % (self.etcpath, repofile) )
                if self.parser.get(name, 'enabled') == '1':
                    repo = self.pool.add_solv( self.solvfile % name )
                    repo.set_name(name)
#                print 'repo', name, '... added'
            except:
                pass

    def search(self, term):
         filematch = map(lambda x: x + term, self.binpaths)
         pkgmatch = []
         for solv in self.pool:
             filelist = None
             if solv.attr_exists('solvable:filelist'):
                 filelist = solv.attr('solvable:filelist')
             if not filelist:
                 continue
             for file in filelist:
                 if file in filematch:
                     row = ( 'zypp (%s)' % solv.repo().name(), term, file[:-len(term)-1] , solv.name() )
                     if not row in pkgmatch:
                         pkgmatch.append( row )
         return pkgmatch

class ScoutModule(object):

    name = "bin"
    desc = "Search for binaries contained in the packages."

    @classmethod
    def query_zypp(cls, term):
        if satsolver == None:
            return None
        s = SolvParser()
        return s.search(term)

    @classmethod
    def query_repo(cls, repo, term):
        db = scout.Database(cls.name + '-' + repo)
        r = db.execute('SELECT binary, path, package FROM binary LEFT JOIN path ON binary.id_path=path.id_path LEFT JOIN package ON binary.id_pkg=package.id_pkg WHERE binary=?', term)
        if r == None:
            return None
        if isinstance(r, list):
            return map( lambda x: [repo] + list(x), r)
        else:
            return [ [repo] + list(r) ]
        return r

    @classmethod
    def main(cls):

        p = scout.Parser(cls.name)
        p.add_repo('zypp')
        if not p.parse():
            return None
        term = p.args[0]

        result = scout.Result( ['repo', 'bin', 'path', 'pkg'], ['repository', 'binary', 'path', 'package']);

        for repo in p.get_repos():
            if repo == 'zypp':
                result.add_rows( cls.query_zypp(term) )
            else:
                result.add_rows( cls.query_repo(repo, term) )

        return result
