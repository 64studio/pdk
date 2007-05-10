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

'''
Display a progress meter on the console.
'''

import sys

class SizeCallbackAdapter(object):
    '''Adapt a serise of "size" calls to the curl progress callback.

    Give the expected total in the contructor.

    Call the object with the length of each new frame.
    '''
    def __init__(self, progress, total):
        self.progress = progress
        self.total = total
        self.current = 0

    def __call__(self, frame_size):
        self.current += frame_size
        self.progress.write_bar(self.total, self.current)

class CurlAdapter(object):
    '''Adapt the ConsoleProgress class to handle the curl progress
    callback
    '''

    def __init__(self, progress):
        self.progress = progress

    def callback(self, down_total, down_now, up_total, up_now):
        '''Call progress methods as appropriate.

        total - total amount of work to be done. 0 for unbounded.
        current - current amount of work accomplished.

        When unbounded, non-zero implies still working, zero implies
        done.
        '''
        total = down_total + up_total
        now = down_now + up_now

        if total == 0:
            self.progress.write_spin()
        else:
            self.progress.write_bar(total, now)

class ConsoleProgress(object):
    '''Display a progress meter on the console.

    Call start before write_bar or write_spin.
    Use write_bar for bounded.
    Use write_spin for unbounded work.
    Call done when finished.
    '''
    def __init__(self, name, output_file = sys.stderr):
        self.name = name
        self.output_file = output_file
        self.bar_len = 60

        self.spinner = { '-': '+', '+': '-' }
        self.spinner_current = '-'

    def start(self):
        '''Write the name of this bar to the handle if neccessary.'''
        if self.name:
            self.output_file.write(self.name + '\n')
            self.output_file.flush()

    def done(self):
        '''Insert a real line break.'''
        self.output_file.write('\n')
        self.output_file.flush()

    def write_bar(self, total, current):
        '''Write the current progress to the handle.

        total - total amount of work to be done. 0 for unbounded.
        current - current amount of work accomplished.

        When unbounded, non-zero implies still working, zero implies
        done.
        '''
        ticks = int(self.bar_len * float(current) / float(total))
        if ticks < 0:
            ticks = 0
        if ticks > self.bar_len:
            ticks = self.bar_len
        spaces = self.bar_len - ticks
        bar_string = '|' + ticks * '=' + spaces * ' ' + '|\r'

        self.output_file.write(bar_string)
        self.output_file.flush()

    def write_spin(self):
        '''Write a spinner to the handle.'''
        bar_string = '|' + self.bar_len * self.spinner_current + '|\r'
        self.spinner_current = self.spinner[self.spinner_current]

        self.output_file.write(bar_string)
        self.output_file.flush()

class ConsoleMassProgress(object):
    '''Organize a series of progress reported operations.

    size_map associates a "size" with each key in the map.

    Use get_single_progress to get an object which records progress
    of a single progress reported operation.

    After the operation is finished, call note_finished for the
    operation key and write_progress.
    '''
    def __init__(self, name, size_map, output_file = sys.stderr):
        self.name = name
        self.size_map = size_map
        self.total = sum(size_map.itervalues())
        self.current = 0
        self.output_file = output_file

    def get_size(self, key):
        '''Get the operation size associated with this key'''
        return self.size_map[key]

    def note_finished(self, key):
        '''Note that the operation for a given key has finished.'''
        self.current += self.size_map[key]

    def write_progress(self):
        '''Write a human readable indication of progress on the operations.
        '''
        percent = int((100 * self.current) / self.total)
        self.output_file.write('%s\nProgress: %d/%d %d%%\n'
                               % (self.name, self.current, self.total,
                                  percent))

    def get_single_progress(self, key, name = None):
        '''Get a progress object suitable for a single operation.

        Use the name field to override the displayed name of the operation.
        '''
        if not name:
            name = key
        return ConsoleProgress(name, self.output_file)

class NullProgress(object):
    '''Stub class for console progress.

    This class stands in for ConsoelProgress but is quiet.
    '''
    def __init__(self):
        pass

    def start(self):
        '''This method is a noop.'''
        pass

    def done(self):
        '''This method is a noop.'''
        pass

    def write_bar(self, *dummy):
        '''This method is a noop.'''
        pass

    def write_spin(self):
        '''This method is a noop.'''
        pass

class NullMassProgress(object):
    '''Stub class for console mass progress.

    This class stands in for ConsoelMassProgress but is quiet.
    '''
    def __init__(self):
        pass

    def get_size(self, dummy):
        '''Returns 1, otherwise is a noop.'''
        return 1

    def note_finished(self, dummy):
        '''This method is a noop.'''
        pass

    def write_progress(self):
        '''This method is a noop.'''
        pass

    def get_single_progress(self, *dummy):
        '''This method is a noop.'''
        return NullProgress()

# vim:set ai et sw=4 ts=4 tw=75:
