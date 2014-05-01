#!/user/bin/env/python
from __future__ import with_statement
import datetime, shutil, os, sys

from fabric.api import *
from fabric.context_managers import cd, lcd
from fabric.operations import local as lrun
from fabric.contrib.files import exists, sed
from fabric.state import output
from fabric.utils import abort, puts

import config
from local_config import local

config.local = local
env.target = {}

def set_target(target_name):
    """Set the target host using the given string

    Arguments:
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
def db_create():
    run('mysql -h %s -u %s -p%s -e "CREATE DATABASE IF NOT EXISTS %s"' %
        (env.target['wordpressConfig']['DB_HOST'],
         env.target['wordpressConfig']['DB_USER'],
         env.target['wordpressConfig']['DB_PASSWORD'],
         env.target['wordpressConfig']['DB_NAME']))

@task
def setup():
    """Checkout repository and create mysql database on target."""
    if not exists(env.target['directory']):
        run('mkdir %s' % env.target['directory'])
    if not exists(env.target['sharedDirectory']):
        run('mkdir %s' % env.target['sharedDirectory'])
    with cd(env.target['directory']), hide('running'):
        run('git clone --recursive %s .' % config.git_url)
        run('mkdir %s' % config.backup_directory)
    execute(db_create)

@task
def deploy(branch=None, tag=None, commit=None, submodules='no'):
    """Update target deployment.

    Arguments branch, tag and commit are mutually exclusive.
    If none of these are given, redeploys current deployment.
    Precedence is commit > tag > branch.

    Keyword arguments:
        branch -- The branch to deploy (default None)
        tag -- The tag to deploy (default None)
        commit -- The commit hash to deploy (default None)
        submodules -- If 'yes', redeploy all submodules, otherwise ignore them. (default 'no')
        quiet -- If True, show verbose output, otherwise be quiet. (default True)"""
    if 'deploy' in env.target and env.target['deploy'] != True:
        puts("Value %s.deploy not set. Aborting." % env.target['wordpressConfig']['WP_STAGE'])
        return
    if not exists(env.target['directory']):
        abort("Target directory does not exist. Run 'fab %s setup' first." % env.target['wordpressConfig']['WP_STAGE'])
    if tag or branch or commit:
        with cd(env.target['directory']), quiet():
            log_level = '--verbose' if output.debug else '--quiet'
            git_fetch = 'git fetch --all %s' % log_level
            git_fetch_tags = 'git fetch --tags %s' % log_level
            run(git_fetch)
            if not commit:
                if tag:
                    run(git_fetch_tags)
                    run('git checkout --force %s' % tag)
                elif branch:
                    run('git checkout --force %s' % branch)
                    run('git merge --ff-only origin/%s' % branch)
            else:
                run('git checkout --force %s' % commit)
            if submodules == 'yes':
                run('git submodule%s foreach %s; %s' %
                    ('' if output.debug else ' --quiet',
                     git_fetch_tags,
                     git_fetch))
                run('git submodule update --init --force --recursive')
    with cd(env.target['directory']), quiet():
        run('git reset --hard HEAD')
        for key, value in env.target['wordpressConfig'].items():
            sed('wp-config.php', '%%%%%s%%%%' % key, value, backup='')
        run('if [ ! -h %s/shared ]; then ln -s %s %s/shared; fi' % (env.target['directory'], env.target['sharedDirectory'], env.target['directory']))

@task
def db_update(source):
    """Update Wordpress-specific settings in the database.
    
    Uses Search Replace DB CLI to replace serialized values in the database.
        
    Arguments:
        source -- The source to replace settings from (local, staging or production)"""
    source = getattr(config, source)
    if not exists(env.target['srdbCli']):
        abort("Search Replace DB CLI does not exist at %s. Please install Search Replace DB on your target machine" % env.target['srdbCli'])
    cli_command = '%s -h%s -d%s -u%s -p%s' % (
        env.target['srdbCli'],
        env.target['wordpressConfig']['DB_HOST'],
        env.target['wordpressConfig']['DB_NAME'],
        env.target['wordpressConfig']['DB_USER'],
        env.target['wordpressConfig']['DB_PASSWORD'])
    with quiet():
        run('%s -s%s -r%s' %
            (cli_command,
             source['wordpressConfig']['WP_SITEURL'],
             env.target['wordpressConfig']['WP_SITEURL']))
        run('%s -s%s -r%s' %
            (cli_command,
             source['wordpressConfig']['WP_HOME'],
             env.target['wordpressConfig']['WP_HOME']))
        run('%s -s%s -r%s' %
            (cli_command,
             source['directory'],
             env.target['directory']))

@task
def db_copy(source, options_table='no'):
    """Copy the database from the given source to the target

    Arguments:
    source -- The source to copy from (local, staging or production)
    options_table -- Whether to copt the wp_options table (default 'no')"""
    execute(db_backup)
    db_clone(source, options_table)
    execute(db_update, source=source)
    execute(deploy)

def db_clone(source, options_table):
    source = getattr(config, source)
    mysqldump = 'mysqldump --add-drop-table -h %s -u %s -p%s %s%s' % (
        source['wordpressConfig']['DB_HOST'],
        source['wordpressConfig']['DB_USER'],
        source['wordpressConfig']['DB_PASSWORD'] ,
        source['wordpressConfig']['DB_NAME'],
        ' --ignore-table=%s.wp_options' % source['wordpressConfig']['DB_NAME'] if options_table is 'no' else '')
    mysql_login = 'mysql -h %s -u %s -p%s %s' % (
        env.target['wordpressConfig']['DB_HOST'],
        env.target['wordpressConfig']['DB_USER'],
        env.target['wordpressConfig']['DB_PASSWORD'],
        env.target['wordpressConfig']['DB_NAME'])
    with quiet():
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

@task
def db_backup(filename = str('%s-%s' % (config.backup_filename, datetime.datetime.now())).replace(' ', '-')):
    """Backup the database on the target host.

    Keyword arguments:
    filename -- The filename, without extensiosn, to use for database backup (optional).
        If different from 'config.backup_filename', created backups will be ignored by tidy_backups"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)), quiet():
        run('mysqldump --add-drop-table -h %s -u %s -p%s %s | gzip -9 > %s.sql.gz' %
            (env.target['wordpressConfig']['DB_HOST'],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME'],
             filename))
    execute(tidy_backups)

def get_backup_files():
    """Get a sorted list of backup files."""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)), quiet():
        with hide('running','stdout'):
            backup_files = run("find . -maxdepth 1 -name '%s*.sql.gz' -printf '%%f\n'" % config.backup_filename).splitlines()
            backup_files.sort()
            return backup_files

@task
def tidy_backups():
    """Remove auto-generated backup files over the limit."""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)), quiet():
        backup_files = get_backup_files()
        if len(backup_files) > config.backup_count:
            for filename in backup_files[:-config.backup_count]:
                run('rm %s' % filename)
    
@task
def db_restore():
    """Restore the latest auto-generated backup on the target host"""
    with cd('%s/%s' % (env.target['directory'], config.backup_directory)), quiet():
        backup_files = get_backup_files()
        run('gunzip -c %s | mysql -h %s -u %s -p%s %s' %
            (backup_files[-1],
             env.target['wordpressConfig']['DB_HOST'],
             env.target['wordpressConfig']['DB_USER'],
             env.target['wordpressConfig']['DB_PASSWORD'],
             env.target['wordpressConfig']['DB_NAME']))