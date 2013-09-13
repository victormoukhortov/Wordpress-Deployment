#!/user/bin/env/python
from __future__ import with_statement
import datetime, shutil, os, sys

from fabric.api import *
from fabric.context_managers import cd, lcd
from fabric.operations import local as lrun
from fabric.contrib.files import exists, sed
from fabric.utils import abort

import config

env.target = {}

def set_target(target_name):
    """Set the target host using the given string

    Keyword arguments:
    target_name -- Target name to match from the configuration file"""
    env.target = getattr(config, target_name)
    env.hosts = [env.target['host']]
    env.target['wordpressConfig']['WP_STAGE'] = target_name

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
    """Checkout repository to target directory of target host. Create mysql database on target"""
    if not exists(env.target['directory']):
        run('mkdir %s' % env.target['directory'])
    with cd(env.target['directory']):
        run('git clone --recursive %s .' % config.git_url)
        run('mkdir %s' % config.backup_directory)
    run('mysql -h %s -u %s -p%s -e "CREATE DATABASE IF NOT EXISTS %s"' %
        (env.target['wordpressConfig']['DB_HOST'],
         env.target['wordpressConfig']['DB_USER'],
         env.target['wordpressConfig']['DB_PASSWORD'],
         env.target['wordpressConfig']['DB_NAME']))

@task
def deploy(branch=None, tag=None, commit=None, quiet=True):
    """Update target deployment. Arguments are mutually exclusive. Precedence is commit > tag > branch. If no arguments are given, redeploys current deployment

    Keyword arguments:
    branch -- The branch to deploy (optional)
    tag -- The tag to deploy (optional)
    commit -- The commit hash to deploy (optional)"""
    if not exists(env.target['directory']):
        abort("Target directory does not exist. Run 'fab %s setup' first" % env.target['wordpressConfig']['WP_STAGE'])
    if tag or branch or commit:
        with cd(env.target['directory']):
            log_level = '--quiet' if quiet == True else '--verbose'
            git_commands = ['git reset --hard',
                'git fetch --all %s' % log_level,
                'git fetch --tags %s' % log_level]
            for command in git_commands:
                run(command)
            if not commit:
                if tag:
                    run('git checkout %s' % tag)
                elif branch:                
                    run('git pull %s' % log_level)
                    run('git checkout %s' % branch)
                    run('git submodule %s foreach %s' %
                        (log_level,
                         "; ".join(git_commands)))
                    run('git submodule update --recursive')
            else:
                run('git checkout %s' % commit)
    with cd(env.target['directory']):
        for key, value in env.target['wordpressConfig'].items():
            sed('wp-config.php', '%%%%%s%%%%' % key, value, backup='')

@task
def db_copy(source):
    """Clone the database from the given source to the target

    Keyword arguments:
    source -- The source to clone from (local, staging or production)"""
    execute(db_backup)
    source = getattr(config, source)
    mysql_update = "UPDATE wp_options \
        SET option_value = '%s' \
        WHERE option_name = 'home';\
        UPDATE wp_options \
        SET option_value = '%s' \
        WHERE option_name = 'siteurl';\
        UPDATE wp_options \
        SET option_value = '%s/wp/wp-content/themes/' \
        WHERE option_name = 'template_root' \
        OR option_name = 'stylesheet_root';" % (
            env.target['wordpressConfig']['WP_HOME'],
            env.target['wordpressConfig']['WP_SITEURL'],
            env.target['directory'])
    mysqldump = 'mysqldump --add-drop-table -h %s -u %s -p%s %s' % (
        source['wordpressConfig']['DB_HOST'],
        source['wordpressConfig']['DB_USER'],
        source['wordpressConfig']['DB_PASSWORD'] ,
        source['wordpressConfig']['DB_NAME'])
    mysql_login = 'mysql -h %s -u %s -p%s %s' % (
        env.target['wordpressConfig']['DB_HOST'],
        env.target['wordpressConfig']['DB_USER'],
        env.target['wordpressConfig']['DB_PASSWORD'],
        env.target['wordpressConfig']['DB_NAME'])
    if source == config.local:
        lrun("%s | ssh %s '%s'" %
            (mysqldump,
             env.target['host'],
             mysql_login))
    else:
        run("ssh %s '%s' | %s" %
            (source['host'],
             mysqldump,
             mysql_login))
    run('mysql -h %s -u %s -p%s -e "%s" %s' %
        (env.target['wordpressConfig']['DB_HOST'],
         env.target['wordpressConfig']['DB_USER'],
         env.target['wordpressConfig']['DB_PASSWORD'],
         mysql_update,
         env.target['wordpressConfig']['DB_NAME']))
    execute(deploy)
            
@task
def db_backup(filename = str('%s-%s' % (config.backup_filename, datetime.datetime.now())).replace(' ', '-')):
    """Backup the database on the target host

    Keyword arguments:
    filename -- The filename, without extensiosn, to use for database backup (optional).
        If different from 'config.backup_filename', created backups will be ignored by tidy_backups"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        run('mysqldump --add-drop-table -h %s -u %s -p%s %s | gzip -9 > %s.sql.gz' %
            (env.target['wordpressConfig']['DB_HOST'],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME'],
             filename))
    execute(tidy_backups)

def get_backup_files():
    """Create a sorted list of auto-generated database backup files on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = run("find . -maxdepth 1 -name '%s*.sql.gz' -printf '%%f\n'" % config.backup_filename).splitlines()
        backup_files.sort()
        return backup_files

@task
def tidy_backups():
    """Remove auto-generated backup files over the limit set in the config file."""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = get_backup_files()
        if len(backup_files) > config.backup_count:
            for filename in backup_files[:-config.backup_count]:
                run('rm %s' % filename)
    
@task
def db_restore():
    """Restore the latest auto-generated backup on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)):
        backup_files = get_backup_files()
        run('gunzip -c %s | mysql -h %s -u %s -p%s %s' %
            (backup_files[-1],
             env.target['wordpressConfig']['DB_HOST'],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME']))
