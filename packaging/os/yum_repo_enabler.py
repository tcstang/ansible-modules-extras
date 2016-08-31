#!/usr/bin/python
# encoding: utf-8

# (c) 2016, Timothy Tang <tcstang@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import os
import ConfigParser
from ConfigParser import NoSectionError

DOCUMENTATION = '''
---
module: yum_repo_enabler
extends_documentation_fragment: files
description:
    - Enables/disables repository files contained in a yum directory.
version_added: 1.1
options:
    directory:
        description:
            - The directory where the Yum repo files are contained.
        required: false
        default: '/etc/yum.repos.d'
    name:
        description:
            - The name of the unique Yum repository (config section which is bracketed in .repo files)
        required: true
        default: null
    enabled:
        description:
            - The boolean state of the enabled value in the Yum repository
        required : true
        default: null
notes:
    - This module assumes that the Yum repositories are configured properly and repository
      names are unique as per normally required by Yum
'''

EXAMPLES = '''
- name: enable EPEL repository (some .repo file with contents [epel]
  yum_repo_enabler:
      name=epel
      enabled=True

- name: disable custom repo in custom directory
  yum_repo_enabler:
      name=custom
      enabled=False
      directory='/tmp/custom'
'''

def do_yum_enable(check_mode, directory, name, enabled):
    repo_found = False
    repo_changed = False
    msg = "Yum repo " + name + " was not found."
    if not os.path.isdir(directory):
        msg="Yum repository directory '%s' does not exist." % directory
    else:
        # get list of repo files to look for target repo
        files_to_check = []
        for file in os.listdir(directory):
            # yum module only loads files ending with .repo
            if file[-5:] == '.repo':
                files_to_check += [ os.path.join(directory, file) ]

        # look for unique repository name
        for file in files_to_check:
            config = ConfigParser.ConfigParser()
            try:
                with open(file) as config_in:
                    config.readfp(config_in)
                    if config.get(name, 'enabled') == enabled:
                        msg = 'OK'
                    else:
                        config.set(name, 'enabled', enabled)
                        repo_changed = True
                        msg = "Yum repository " + name + " has successfully been changed"
                        if not check_mode:
                            with open(file, 'wb') as config_out:
                                config.write(config_out)
                    repo_found = True
                    break
            except NoSectionError:
                continue
    return (repo_changed, repo_found, msg)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            directory = dict(default='/etc/yum.repos.d', type='path'),
            name = dict(required=True),
            enabled = dict(required=True, type='bool')
        ),
        supports_check_mode = True
    )

    repo_enabled = str(int(module.params['enabled']))
    repo_name = module.params['name']
    repo_directory = module.params['directory']

    repo_changed, repo_found, message = do_yum_enable(module.check_mode, repo_directory, repo_name, repo_enabled)
    if repo_found == True:
        module.exit_json(
            directory=repo_directory,
            changed=repo_changed,
            msg=message
        )
    else:
        module.fail_json(
            directory=repo_directory,
            changed=repo_changed,
            msg=message
        )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
        main()
