#!/user/bin/env/python
from __future__ import with_statement
import datetime, shutil, os, sys

from fabric.api import *
from fabric.context_managers import cd, lcd
from fabric.operations import local as lrun
from fabric.contrib.files import exists, sed

import config

env.target = {}

def set_target(target_name):
    """Set the target host using the given string

    Keyword arguments:
    target_name -- Target name to match from the configuration file"""
    env.target = getattr(config, target_name)
    env.hosts = [env.target['host']]

@task
def local():
    """ Set the target host to the local server"""
    set_target('local')
    
@task
def staging():
    """ Set the target host to the staging server"""
    set_target('staging')

@task
def production():
    """Set the target host to the production server"""
    set_target('production')

@task
def setup():
    """Checkout repository to target directory of target host"""
    if not exists(env.target['directory']):
        run('mkdir %s' % env.target['directory'])
    with cd(env.target['directory']):
        run('git clone --recursive %s .' % config.git_url)
        run('mkdir %s' % config.backup_directory)

@task
def deploy(branch='master', tag=None, commit=None):
    """Update target deployment. Arguments are mutually exclusive. Precedence is commit > tag > branch.

    Keyword arguments:
    branch -- The branch to deploy
    tag -- The tag to deploy
    commit -- The commit hash to deploy"""
    with cd(env.target['directory']):
        run('git reset --hard HEAD')
        if not commit:
            if tag:
                run('git checkout tag/%s' % tag)
            else:
                run('git checkout %s' % branch)
        else:
            run('git checkout %s' % commit)
        for key, value in env.target['wordpressConfig'].items():
            sed('wp-config.php', '%%%%%s%%%%' % key, value)
            
@task
def db_clone(source="staging"):
    """Clone the database from the given source to the target

    Keyword arguments:
    source -- The source to clone from (local, staging or production)"""
    execute(db_backup)
    source = getattr(config, source)
    run("mysqldump --add-drop-table -h %s -u %s -p%s %s | ssh -C %s 'mysql -u %s -p%s %s'" %
        (source['wordpressConfig']['DB_HOST'],
         source['wordpressConfig']['DB_USER'],
         source['wordpressConfig']['DB_PASSWORD'] ,
         source['wordpressConfig']['DB_NAME'],
         env.target['host'],
         env.target['wordpressConfig']['DB_USER'],
         env.target['wordpressConfig']['DB_PASSWORD'],
         env.target['wordpressConfig']['DB_NAME']))

@task
def db_backup():
    """Backup the database on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        run('mysqldump --add-drop-table -h %s -u %s -p%s %s | gzip -9 > %s.sql.gz' %
            (env.target['wordpressConfig']['DB_HOST'],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME'],
             str('backup-%s' % datetime.datetime.now()).replace(' ', '-')))
    execute(tidy_backups)

def get_backup_files():
    """Create a sorted list of database backup files on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = run('ls -1').splitlines()
        backup_files.sort()
        return backup_files

@task
def tidy_backups():
    """Remove backup files over the limit set in the configuration file"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = get_backup_files()
        if len(backup_files) > config.backup_count:
            for filename in backup_files[:-config.backup_count]:
                run('rm %s' % filename)
    
@task
def restore_backup():
    """Restore the latest backup on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = get_backup_files()
        run('gunzip -c %s | mysql -u %s -p%s %s' %
            (backup_files[-1],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME']))
