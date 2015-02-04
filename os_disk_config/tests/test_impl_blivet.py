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

import blivet
import mock
from oslotest import base

from os_disk_config import impl_blivet

class TestStandardPartition(base.BaseTestCase):
    def setUp(self):
        super(TestStandardPartition, self).setUp()
        self.blivet_instance = mock.Mock(spec=blivet.Blivet)
        self.patcher = mock.patch('blivet.Blivet')
        self.addCleanup(self.patcher.stop)
        self.mock_blivet = self.patcher.start()
        self.mock_blivet.return_value = self.blivet_instance

    def test_constructor(self):
        dc = impl_blivet.BlivetDiskConfig()
        self.blivet_instance.reset.assert_called_once_with()
