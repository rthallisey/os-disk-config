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
import logging
import subprocess

import six

from os_disk_config import objects


logger = logging.getLogger(__name__)


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
        if isinstance(obj, objects.StandardPartition):
            self.add_standard_partition(obj)

    @abc.abstractmethod
    def add_standard_partition(self, obj):
        """Add a StandardPartition object to the disk config"""
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

    def add_to_fstab(self, device, path, filesystem, options, dump):
        """Add an entry to /etc/fstab for the specified partition

        Checks to see if an entry already exists, and if not adds one.

        :param device: The path to the partition device file, e.g. /dev/sda1.
        :param path: The path at which to mount the partition.
        :param filesystem: The filesystem on the partition.
        :param options: The options for mounting the filesystem.
        :param dump: Boolean indicating whether the filesystem will be
            included in dump(8) backups.
        """
        uuid = self.get_uuid(device)
        dump = 1 if dump else 0
        newline = 'UUID=%s %s %s %s %s 1' % (uuid, path, filesystem, options,
                                             dump)
        with open('/etc/fstab') as fstab:
            lines = fstab.readlines()
            for line in lines:
                split_line = line.split()
                if (len(split_line) > 2 and
                        not split_line[0].startswith('#') and
                        split_line[1] == path):
                    logger.warning('Found existing fstab entry for %s. '
                                   'Will not add a duplicate.', path)
                    return
        with open('/etc/fstab', 'a') as fstab:
            fstab.write('\n# Entry added by os-disk-config.  Do not edit.\n')
            fstab.write(newline + '\n')

    def get_uuid(self, device):
        output = subprocess.check_output(['blkid', '-o', 'value', device])
        return output.split()[0]
