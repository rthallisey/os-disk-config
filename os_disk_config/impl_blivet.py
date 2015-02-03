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

import logging

import blivet

from os_disk_config import impl_base


logger = logging.getLogger(__name__)


class BlivetDiskConfig(impl_base.DiskConfigBase):
    def __init__(self):
        super(BlivetDiskConfig, self).__init__()
        self._blivet = blivet.Blivet()
        self._blivet.reset()
        self._mounts = []
        self._initialized_disks = set()

    def disks(self):
        return [i.path for i in self._blivet.devices if len(i.parents) == 0]

    def add_standard_partition(self, obj):
        disks = []
        for i in obj.disks:
            dev = self._blivet.devicetree.getDeviceByName(i)
            # NOTE(bnemec): This will fail if dev already has partitions.
            # We will need to figure out whether to wipe partitions or just
            # fail in that case.
            if dev not in self._initialized_disks:
                self._blivet.initializeDisk(dev)
                self._initialized_disks.add(dev)
            disks.append(dev)
        partition = self._blivet.newPartition(size=blivet.Size(obj.size),
                                              parents=disks)
        self._blivet.createDevice(partition)
        blivet.partitioning.doPartitioning(self._blivet)
        logger.info('Creating partition %s', partition.path)

        if obj.filesystem is not None:
            filesystem = blivet.formats.getFormat(obj.filesystem,
                                                  device=partition.path)
            self._blivet.formatDevice(partition, filesystem)
            logger.info('Formatting %s as %s', partition.path, obj.filesystem)
            if obj.mountpoint is not None:
                self._mounts.append((partition.path, obj.mountpoint, obj.filesystem))
                logger.info('Mounting %s at %s', partition.path, obj.mountpoint)

    def apply(self, noop):
        if not noop:
            self._blivet.doIt()
            for i in self._mounts:
                blivet.util.mount(*i)
