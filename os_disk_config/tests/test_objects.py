# -*- coding: utf-8 -*-

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

from oslotest import base

from os_disk_config import objects


class TestVersions(base.BaseTestCase):
    def test_matching_versions(self):
        d = dict(version=objects.CONFIG_VERSION)
        objects.check_version(d)

    def test_newer_version(self):
        d = dict(version='0.1.0')
        self.assertRaises(objects.InvalidConfigException,
                          objects.check_version, d)

    def test_older_version(self):
        d = dict(version='0.0.1')
        save_ver = objects.CONFIG_VERSION
        try:
            objects.CONFIG_VERSION = '0.1.0'
            objects.check_version(d)
        finally:
            objects.CONFIG_VERSION = save_ver

    def test_major_difference(self):
        d = dict(version='1.0.0')
        self.assertRaises(objects.InvalidConfigException,
                          objects.check_version, d)

    def test_no_version(self):
        d = dict()
        self.assertRaises(objects.InvalidConfigException,
                          objects.check_version, d)
