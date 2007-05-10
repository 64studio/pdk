#
# Copyright (c) 2004 Conectiva, Inc.
#
# Written by Gustavo Niemeyer <niemeyer@conectiva.com>
#
# This file is part of Smart Package Manager.
#
# Smart Package Manager is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# Smart Package Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Smart Package Manager; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from smart.backends.deb.loader import DebTagLoader, getControl
from smart.backends.deb.base import DEBARCH
from smart.util.tagfile import TagFile
from cStringIO import StringIO
from smart.channel import PackageChannel
from smart import *
import os
import string

from pdk.workspace import current_workspace
from pdk.package import Package

class PdkDebLoader(DebTagLoader):

    def __init__(self, path):
        DebTagLoader.__init__(self, "pdk:///")
        self._path = path
        ws = current_workspace()
        descriptor = ws.get_component_descriptor(self._path)
        cache = ws.world.get_backed_cache(ws.cache)
        self._component = descriptor.load(cache)
        self._contents = {}
        iterator_fn = self._component.iter_raw_ordered_contents
        refs = iterator_fn((Package,), True, None, None)
        i = 0
        types = ['deb', 'udeb']
        archs = [DEBARCH, 'all']
        for index, ref in enumerate(refs):
            if (ref.type in types) and (ref.arch in archs):
                self._contents[i] = ref
                i += 1
        
    def getLoadSteps(self):

        return len(self._contents)
    
    def getSections(self, prog):

        i = 0

        for package in self._contents.values():
            apt_fields = {}
            apt_fields['package'] = package.name
            apt_fields['version'] = package.version.full_version
            apt_fields['architecture'] = package.arch

            for predicate, value in package.iter_by_domains(('deb')):
                if predicate == 'arch':
                    continue
                apt_fields[string.lower(predicate)] = value

            yield (apt_fields, i)
            i += 1
            prog.add(1)
            prog.show()

    def getDict(self, pkg):

        index = pkg.loaders[self]        
        package = self._contents[index]

        apt_fields = {}
        apt_fields['package'] = package.name
        apt_fields['version'] = package.version.full_version
        apt_fields['architecture'] = package.arch

        for predicate, value in package.iter_by_domains(('deb')):
            if predicate == 'arch':
                continue
            apt_fields[predicate] = value

        return apt_fields

    def getFileName(self, info):
        pkg = info.getPackage()
        filepath = os.path.join(self._path)
        while filepath.startswith("/"):
            filepath = filepath[1:]
        return filepath

    def getSize(self, info):
        pkg = info.getPackage()
        filename = self._filenames[pkg.loaders[self]]
        return os.path.getsize(os.path.join(self._dir, filename))


class PdkDebChannel(PackageChannel):

    def __init__(self, path, *args):
        super(PdkDebChannel, self).__init__(*args)
        self._path = path

    def fetch(self, fetcher, progress):
        digest = os.path.getmtime(self._path)
        if digest == self._digest:
            return True
        self.removeLoaders()
        loader = PdkDebLoader(self._path)
        loader.setChannel(self)
        self._loaders.append(loader)
        self._digest = digest
        return True

def create(alias, data):
    if data["removable"]:
        raise Error, _("%s channels cannot be removable") % data["type"]
    return PdkDebChannel(data["path"],
                         data["type"],
                         alias,
                         data["name"],
                         data["manual"],
                         data["removable"],
                         data["priority"])
