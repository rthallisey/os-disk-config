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

import mock
from oslotest import base

from os_disk_config import impl_blivet

BLKID_OUT = '''50607425-3e50-48e2-846d-ed253d54c5c9
ext4
db17ca07-01'''

FSTAB = ['UUID=c3dbe26e-e200-496e-af8e-d3071afe1a29 /  ext4  defaults  1 1']
FSTAB_EXISTING = [
'UUID=c3dbe26e-e200-496e-af8e-d3071afe1a29 /  ext4  defaults  1 1',
'',
'# Entry added by os-disk-config.  Do not edit.',
'UUID=41a155bc-0032-4794-a321-d71402e8d7d3 /mnt/test ext4 defaults 1 1'
]
FSTAB_COMMENTED = [
'UUID=c3dbe26e-e200-496e-af8e-d3071afe1a29 /  ext4  defaults  1 1',
'',
'# Entry added by os-disk-config.  Do not edit.',
'#UUID=41a155bc-0032-4794-a321-d71402e8d7d3 /mnt/test ext4 defaults 1 1'
]



class TestBase(base.BaseTestCase):
    @mock.patch('blivet.Blivet')
    @mock.patch('subprocess.check_output')
    def test_get_uuid(self, mock_check_output, _):
        dc = impl_blivet.BlivetDiskConfig()
        mock_check_output.return_value = BLKID_OUT
        self.assertEqual(dc.get_uuid('/dev/vdb1'),
                         '50607425-3e50-48e2-846d-ed253d54c5c9')

    @mock.patch('blivet.Blivet')
    @mock.patch('subprocess.check_output')
    def test_add_to_fstab(self, mock_check_output, _):
        self._check_added(FSTAB, True, mock_check_output)
        self._check_added(FSTAB_COMMENTED, True, mock_check_output)

    @mock.patch('blivet.Blivet')
    @mock.patch('subprocess.check_output')
    def test_add_to_fstab_existing(self, mock_check_output, _):
        self._check_added(FSTAB_EXISTING, False, mock_check_output)

    def _check_added(self, data, added, mock_check_output):
        mock_check_output.return_value = BLKID_OUT
        m = mock.mock_open()
        m().readlines.return_value = data
        with mock.patch('os_disk_config.impl_base.open', m, create=True):
            dc = impl_blivet.BlivetDiskConfig()
            dc.add_to_fstab('/dev/sda1', '/mnt/test', 'ext4', 'defaults',
                            False)
            args = ['/etc/fstab']
            if added:
                args.append('a')
            m.assert_called_with(*args)
            self.assertTrue(m().readlines.called)
            self.assertEqual(added, m().write.called)
