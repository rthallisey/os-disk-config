# Copyright 2014 Red Hat, Inc.
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

import json

import blivet
import mock
from oslotest import base

from os_disk_config import impl_blivet
from os_disk_config import objects

STANDARD_PARTITION_JSON = '''
{
    "partitions": [
        {"name": "test_part",
         "disks": ["sda"],
         "filesystem": "ext4",
         "size": "1 TiB",
         "type": "standard",
         "mountpoint": "/mnt/test"
         }
    ],
    "version": "0.0.1"
}
'''
GET = 'os_disk_config.impl_blivet.BlivetDiskConfig._get_partition'
CREATE = 'os_disk_config.impl_blivet.BlivetDiskConfig._create_partition'
FORMAT = 'os_disk_config.impl_blivet.BlivetDiskConfig._format_partition'


class TestStandardPartition(base.BaseTestCase):
    def setUp(self):
        super(TestStandardPartition, self).setUp()
        self.blivet_instance = mock.Mock(spec=blivet.Blivet)
        self.patcher = mock.patch('blivet.Blivet')
        self.addCleanup(self.patcher.stop)
        self.mock_blivet = self.patcher.start()
        self.mock_blivet.return_value = self.blivet_instance
        self.dc = impl_blivet.BlivetDiskConfig()

    def test_constructor(self):
        self.blivet_instance.reset.assert_called_once_with()

    @mock.patch(GET)
    @mock.patch(CREATE)
    @mock.patch(FORMAT)
    def test_add_standard_partition(self, mock_format, mock_create, mock_get):
        obj_json = json.loads(STANDARD_PARTITION_JSON)
        obj = objects.StandardPartition.from_json(
            obj_json.get('partitions')[0])
        mock_part = mock.Mock()
        mock_get.return_value = mock_part

        self.dc.add_standard_partition(obj)

        mock_get.assert_called_once_with(obj)
        mock_create.assert_called_once_with(mock_part)
        mock_format.assert_called_once_with(obj, mock_part)
        self.assertEqual([(mock_part, obj.mountpoint)], self.dc._mounts)

    @mock.patch(GET)
    @mock.patch(CREATE)
    @mock.patch(FORMAT)
    def test_no_mountpoint(self, mock_format, mock_create, mock_get):
        obj_json = json.loads(STANDARD_PARTITION_JSON)
        del obj_json.get('partitions')[0]['mountpoint']
        obj = objects.StandardPartition.from_json(
            obj_json.get('partitions')[0])
        mock_part = mock.Mock()
        mock_get.return_value = mock_part

        self.dc.add_standard_partition(obj)

        mock_get.assert_called_once_with(obj)
        mock_create.assert_called_once_with(mock_part)
        mock_format.assert_called_once_with(obj, mock_part)
        self.assertEqual([], self.dc._mounts)

    @mock.patch(GET)
    @mock.patch(CREATE)
    @mock.patch(FORMAT)
    def test_no_filesystem(self, mock_format, mock_create, mock_get):
        obj_json = json.loads(STANDARD_PARTITION_JSON)
        del obj_json.get('partitions')[0]['filesystem']
        obj = objects.StandardPartition.from_json(
            obj_json.get('partitions')[0])
        mock_part = mock.Mock()
        mock_get.return_value = mock_part

        self.dc.add_standard_partition(obj)

        mock_get.assert_called_once_with(obj)
        mock_create.assert_called_once_with(mock_part)
        self.assertFalse(mock_format.called)
        self.assertEqual([], self.dc._mounts)

    def test_get_partition(self):
        obj_json = json.loads(STANDARD_PARTITION_JSON)
        obj = objects.StandardPartition.from_json(
            obj_json.get('partitions')[0])
        device = mock.Mock()
        self.blivet_instance.devicetree = mock.Mock()
        self.blivet_instance.devicetree.resolveDevice = mock.Mock(
            return_value=device)
        self.assertEqual(0, self.dc._next_weight)

        # Call it twice so we can verify the disk only gets initialized once
        self.dc._get_partition(obj)
        self.dc._get_partition(obj)

        self.blivet_instance.devicetree.resolveDevice.assert_called_with(
            'sda')
        self.blivet_instance.initializeDisk.assert_called_once_with(device)
        self.blivet_instance.newPartition.assert_called_with(
            size=blivet.Size('1 TiB'), parents=[device], weight=-100)
        self.assertEqual(-200, self.dc._next_weight)

    @mock.patch('blivet.partitioning.doPartitioning')
    def test_create_partition(self, mock_doPart):
        partition = mock.Mock()
        self.dc._create_partition(partition)
        self.blivet_instance.createDevice.assert_called_once_with(partition)
        mock_doPart.assert_called_once_with(self.blivet_instance)

    @mock.patch('blivet.formats.getFormat')
    def test_format_partition(self, mock_getFormat):
        obj_json = json.loads(STANDARD_PARTITION_JSON)
        obj = objects.StandardPartition.from_json(
            obj_json.get('partitions')[0])
        partition = mock.Mock()
        partition.path = '/dev/sda'
        mock_filesystem = mock.Mock()
        mock_getFormat.return_value = mock_filesystem

        self.dc._format_partition(obj, partition)

        mock_getFormat.assert_called_once_with(obj.filesystem,
                                               device='/dev/sda')
        self.blivet_instance.formatDevice.assert_called_once_with(
            partition, mock_filesystem)

    def _setup_for_apply(self):
        partition = mock.Mock()
        partition.format = mock.Mock()
        partition.format.mount = mock.Mock()
        mountpoint = mock.Mock()
        self.dc._mounts = [(partition, mountpoint)]

    def test_apply(self):
        self._setup_for_apply()
        self.dc.apply(False)
        self.blivet_instance.doIt.assert_called_once_with()
        self.dc._mounts[0][0].format.mount.assert_called_once_with(
            mountpoint=self.dc._mounts[0][1])

    def test_apply_noop(self):
        self._setup_for_apply()
        self.dc.apply(True)
        self.assertFalse(self.blivet_instance.doIt.called)
        self.assertFalse(self.dc._mounts[0][0].format.mount.called)

    def test_disks(self):
        sda = mock.Mock()
        sda.path = '/dev/sda'
        sda.parents = []
        sda1 = mock.Mock()
        sda1.path = '/dev/sda1'
        sda1.parents = [sda]
        sdb = mock.Mock()
        sdb.path = '/dev/sdb'
        sdb.parents = []
        self.blivet_instance.devices = [sda, sda1, sdb]
        self.assertEqual(['/dev/sda', '/dev/sdb'], self.dc.disks())
