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


import argparse
import logging
import os
import sys
import yaml

import blivet

from os_disk_config import impl_blivet
from os_disk_config import objects
from os_disk_config import version


logger = logging.getLogger(__name__)


def parse_opts(argv):
    parser = argparse.ArgumentParser(
        description='Configure disk interfaces using a JSON config'
        ' file format.')
    parser.add_argument('-c', '--config-file', metavar='CONFIG_FILE',
                        help="""path to the configuration file.""",
                        default='/etc/os-disk-config/config.yaml')
    parser.add_argument('-p', '--provider', metavar='PROVIDER',
                        help="""The provider to use."""
                        """One of: blivet.""",
                        default=None)
    parser.add_argument(
        '-d', '--debug',
        dest="debug",
        action='store_true',
        help="Print debugging output.",
        required=False)
    parser.add_argument(
        '-v', '--verbose',
        dest="verbose",
        action='store_true',
        help="Print verbose output.",
        required=False)

    parser.add_argument('--version', action='version',
                        version=version.version_info.version_string())
    parser.add_argument(
        '--noop',
        dest="noop",
        action='store_true',
        help="Return the configuration commands, without applying them.",
        required=False)

    opts = parser.parse_args(argv[1:])

    return opts


def configure_logger(verbose=False, debug=False):
    LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
    DATE_FORMAT = '%Y/%m/%d %I:%M:%S %p'
    log_level = logging.WARN

    if verbose:
        log_level = logging.INFO
    elif debug:
        log_level = logging.DEBUG

    logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT,
                        level=log_level)


def main(argv=sys.argv):
    opts = parse_opts(argv)
    configure_logger(opts.verbose, opts.debug)
    logger.info('Using config file at: %s' % opts.config_file)
    part_array = []

    # NOTE(bnemec): Add alternate implementations here
    provider = impl_blivet.BlivetDiskConfig()

    disks = provider.disks()
    if len(disks) <= 1:
        logger.error('The system only has one disk')
        return 1
    logger.debug('Available disks: %s', disks)
    if os.path.exists(opts.config_file):
        with open(opts.config_file) as cf:
            part_array = yaml.load(cf.read()).get("partitions")
            logger.debug('partitions JSON: %s' % str(part_array))
    else:
        logger.error('No config file exists at: %s' % opts.config_file)
        return 1
    if not isinstance(part_array, list):
        logger.error('No interfaces defined in config: %s' % opts.config_file)
        return 1
    for part_json in part_array:
        obj = objects.object_from_json(part_json)
        provider.add_object(obj)
    files_changed = provider.apply(noop=opts.noop)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
