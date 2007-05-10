# $Progeny$
#
#   Copyright 2005 Progeny Linux Systems, Inc.
#
#   This file is part of PDK.
#
#   PDK is free software; you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   PDK is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
#   License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PDK; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

'''Contains utility classes for managing metadata.
'''

class Entities(dict):
    '''A container class designed to hold entities, keyed by type and id.
    '''

class Entity(dict):
    '''Represents a single entity.

    Keys are tuples of (domain, predicate).

    The links attribute is a list to (type, id) tuples, referring to the
    keys of entities stored in an Entities class.

    No real checking is done to verify that all linked objects exist
    or anything like that.
    '''

    # To keep performance in some situations snappy, we keep
    # self.__hash precalculated, as too much activity during __hash__
    # calls can burn a lot of cpu cycles.
    #
    # This may be less of an issue as the code is refactored in the
    # future. If a profiler indicates that the complexity is needless,
    # anyone may remove the optimization.

    __slots__ = ('ent_type', '__ent_id', '__hash', 'links')

    def __init__(self, ent_type, ent_id):
        super(Entity, self).__init__()
        self.ent_type = ent_type
        self.links = []

        # Initializing to make pylint happy.
        self.__ent_id = None
        self.__hash = None
        self.ent_id = ent_id

    def set_ent_id(self, ent_id):
        '''Change the entity id'''
        self.__ent_id = ent_id
        self.__hash = hash(self.__ent_id)

    def get_ent_id(self):
        '''Retrieve the entity id.'''
        return self.__ent_id
    ent_id = property(get_ent_id, set_ent_id)

    def __hash__(self):
        return self.__hash

    def iter_by_domains(self, domains):
        '''Iterate over predicates and targets in the given domains.'''
        for key, value in self.iteritems():
            domain = key[0]
            if domain in domains:
                yield key[1], value

# vim:set ai et sw=4 ts=4 tw=75:
