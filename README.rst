===============================
os-disk-config
===============================

disk configuration tool

The intention is for this code to be moved under the tripleo project in due course.

* Free software: Apache license

Features
--------

The core aim of this project is to be able to partition, format, and
mount a disk based on requested input.
The project consists of:

 * A CLI (os-disk-config) which provides configuration via a YAML or JSON
   file formats.  By default os-disk-config uses a YAML config file located
   at /etc/os-disk-config/config.yaml. This can be customized via the
   --config-file CLI option.

 * A python library which provides configuration via an object model.

YAML Config Examples
--------------------
 * Configure a 5G disk::

    partitions:
        - name: test1
          disks:
            - vdb
          filesystem: ext4
          size: 5 GiB
          type: standard
          mountpoint: /mnt/test
    version: 0.0.1
