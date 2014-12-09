#+
# Copyright 2014 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################

from task import Provider, Task, TaskException, query
from lib.system import system
from dispatcher.rpc import description, accepts, returns


@description("Provides access to volumes information")
class VolumeProvider(Provider):
    @query
    def query(self, filter=None, params=None):
        return [v['name'] for v in self.datastore.query('volumes')]

    def resolve_path(self, path):
        pass

    def get_config(self, vol):
        return self.datastore.get_one('volumes', ('name', '=', vol))

    def get_capabilities(self, vol):
        return {
            'vdev-types': {
                'disk': {
                    'min-devices': 1,
                    'max-devices': 1
                },
                'mirror': {
                    'min-devices': 2
                },
                'raidz1': {
                    'min-devices': 2
                },
                'raidz2': {
                    'min-devices': 3
                },
                'raidz3': {
                    'min-devices': 4
                },
                'spare': {
                    'min-devices': 1
                }
            },
            'vdev-groups': {
                'data': {
                    'allowed-vdevs': ['disk', 'file', 'mirror', 'raidz1', 'raidz2', 'raidz3', 'spare']
                },
                'log': {
                    'allowed-vdevs': ['disk', 'mirror']
                },
                'cache': {
                    'allowed-vdevs': ['disk']
                }
            }
        }

@description("Creates new volume")
@accepts({
    'type': 'string',
    'title': 'name'
}, {
    'type': 'string',
    'title': 'type'
}, {
    'type': 'object',
    'title': 'topology',
    'properties': {
        'groups': {'type': 'object'}
    }
})
class VolumeCreateTask(Task):
    def __init__(self, dispatcher):
        pass

    def __get_disks(self, topology):
        result = []
        for g in topology['groups'].values():
            for t in i['vdevs']:
                result += t['disks']

        return result

    def __get_vdevs(self, topology):
        result = []
        for name, grp in topology['groups'].items():
            if name in ('cache', 'log', 'spare'):
                result.append(name)

            for i in filter(lambda x: x['type'] == 'stripe', grp['vdevs']):
                result += i['disks']

            for i in filter(lambda x: x['type'] != 'stripe', grp['vdevs']):
                result.append(i['type'])
                result += i['disks']

        return result

    def verify(self, name, type, topology, params):
        # XXX
        return [i['name'] for i in self.__get_disks(topology)]

    def run(self, name, type, topology, params):
        subtasks = []
        mountpoint = params.pop('mountpoint', '/volumes/{0}'.format(name))
        altroot = params.pop('altroot', '/volumes')

        for i in self.__get_disks(topology):
            subtasks.append(self.run_subtask('disk.format.gpt', i, {
                'blocksize': params.pop('blocksize'),
                'swapsize': params['swapsize'] if i['group'] == 'data' else 0
            }))

        self.join_subtasks(subtasks)

        system(
            'zpool', 'create',
            '-o', 'cachefile=/data/zfs/zpool.cache',
            '-o', 'failmode=continue',
            '-o', 'autoexpand=on',
            '-o', 'altroot=' + altroot,
            '-O', 'compression=lz4',
            '-O', 'aclmode=passthrough',
            '-O', 'aclinherit=passthrough',
            '-f', '-m', mountpoint,
            name, self.__get_vdevs(topology)
        )


class VolumeUpdateTask(Task):
    def verify(self, name):
        pass


class VolumeImportTask(Task):
    pass


class VolumeDetachTask(Task):
    pass


class DatasetCreateTask(Task):
    pass


def _init(dispatcher):
    dispatcher.register_schema_definition('volume-vdev', {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'type': {
                'type': 'string',
                'enum': ['stripe', 'mirror', 'raidz1', 'raidz2', 'raidz3']
            },
            'disks': {
                'type': 'array',
                'items': {'type': 'string'}
            }
        }
    })

    dispatcher.register_schema_definition('volume-topology', {
        'type': 'object',
        'properties': {
            'groups': {'type': 'object'},
            'properties': {
                'data': {'$ref': '#/definitions/volume-vdev'},
                'logs': {'$ref': '#/definitions/volume-vdev'},
                'cache': {'$ref': '#/definitions/volume-vdev'},
                'spare': {'$ref': '#/definitions/volume-vdev'}
            }
        }
    })

    dispatcher.register_schema_definition('volume', {
        'type': 'object',
        'title': 'volume',
        'properties': {
            'name': {'type': 'string'},
            'topology': {'$ref': '#/definitions/volume-topology'},
            'params': {'type': 'object'}
        }
    })

    dispatcher.require_collection('volumes')
    dispatcher.register_provider('volume.info', VolumeProvider)
    dispatcher.register_task_handler('volume.create', VolumeCreateTask)
    dispatcher.register_task_handler('volume.import', VolumeImportTask)