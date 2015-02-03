# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc

import six

@six.add_metaclass(abc.ABCMeta)
class DiskConfigBase(object):
    """Base class for disk configuration implementations"""
    @abc.abstractmethod
    def disks(self):
        """Return a list of paths to disks on the system"""
        pass

    def add_object(self, obj):
        """Convenience method to add any type of object to the disk config.
           See objects.py.

        :param obj: The object to add.
        """
        pass

    @abc.abstractmethod
    def apply(self, noop):
        """Apply the disk configuration.

        :param noop: A boolean which indicates whether this is a no-op.
        :returns: a dict of the format: filename/data which contains info
            for each file that was changed (or would be changed if in --noop
            mode).
        """
        pass