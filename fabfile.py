from __future__ import with_statement
import datetime
import shutil, os

from fabric.api import *
from fabric.operations import local
from fabric.contrib.console import confirm

import config

def set_target(role):
    target = getattr(config, role)
    env.hosts = target['hosts']
    return target

@task
def setup(role='staging'):
    target = set_target(role)
    cd(target['directory'])
    run('git clone ' + config.git['url'])
    run('mkdir %' % (config.backup_directory))

@task
def deploy(role='staging'):
    target = set_target(role)
    env.hosts = target['hosts']
    cd(target['directory'])
    execute(db_backup, role)
    

@task
def db_backup(role="staging"):
    target = set_target(role)
    cd('%/%' % (target['directory'], config.backup_directory))
    run('mysqldump --add-drop-table -h % -u % -p % | gzip > %.sql' % \
        (target['wordpress']['DB_HOST'], \
        target['wordpress']['DB_USER'], \
        target['wordpress']['DB_PASSWORD'], \
        str(datetime.datetime.now()).replace(' ', '_')))
    execute(tidy_backups, target)

@task
def tidy_backups(role="staging"):
    target = set_target(role)
    cd(target['directory'])
    backup_files = os.listdir('.').sort(reverse=True)
    while backup_files:
        backup_count = len([name for name in os.listdir('.') if os.path.isfile(name)])
        if backup_count > config.backup_count:
            os.remove(backup_files.pop())
            
