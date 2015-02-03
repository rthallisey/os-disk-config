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

import logging

from openstack.common import strutils
from os_disk_config import utils


logger = logging.getLogger(__name__)

_NUMBERED_NICS = None


class InvalidConfigException(ValueError):
    pass


def object_from_json(json):
    obj_type = json.get("type")
    if obj_type == "standard":
        return StandardPartition.from_json(json)


def _get_required_field(json, name, object_name):
    field = json.get(name)
    if not field:
        msg = '%s JSON objects require \'%s\' to be configured.' \
              % (object_name, name)
        raise InvalidConfigException(msg)
    return field


class _BaseOpts(object):
    """Base abstraction for partition options."""

    def __init__(self, name, disks, size, filesystem, mountpoint):
        self.name = name
        self.disks = disks
        self.size = size
        self.filesystem = filesystem
        self.mountpoint = mountpoint

    @staticmethod
    def base_opts_from_json(json):
        disks = _get_required_field(json, 'disks', 'All')
        size = _get_required_field(json, 'size', 'All')
        filesystem = json.get('filesystem')
        mountpoint = json.get('mountpoint')
        return (disks, size, filesystem, mountpoint)


class StandardPartition(_BaseOpts):
    """Class for representing partitions."""
    def __init__(self, name, disks, size, filesystem, mountpoint):
        super(StandardPartition, self).__init__(name, disks, size, filesystem,
                                                mountpoint)


    @staticmethod
    def from_json(json):
        name = _get_required_field(json, 'name', 'StandardPartition')
        opts = _BaseOpts.base_opts_from_json(json)
        return StandardPartition(name, *opts)
