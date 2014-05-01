(Another) Wordpress Deployment Strategy
================================
This is a simple command-line deployment tool for [Wordpress](https://wordpress.org/) using [Python Fabric](http://www.fabfile.org/) (more or less a simple wrapper around SSH and bash). This tool uses ideomatic Fabric and is extremely light-weight. Python is not required to be installed on target environments.

At the moment this tool only depends on [Git](http://git-scm.com/) and [Interconnectit's Search Replace DB CLI](https://github.com/interconnectit/Search-Replace-DB/tree/2.2.0) for database copying operations (optional, only required for the `db_copy` task). Otherwise, unlike Capistrano, you don't have to install anything on your servers.

In conjunction with Git and [WP CLI](http://wp-cli.org/), this tool can be used to easily automate most Wordpress related taskes, including databse migration and pushing plugin updates.

Assumptions
--------------------------------
* Using [My Fork](https://github.com/victormoukhortov/WordPress-Skeleton) of Mark Jaquith's excellent Wordpress-Skeleton ([diff here](https://github.com/markjaquith/WordPress-Skeleton/compare/master...victormoukhortov:master))
* Using git for version control

Getting Started
--------------------------------
These instructions assume that you will be deploying to a local server. If you don't want to do this, you can install directly onto staging just as well.

1. Clone my fork of [Wordpress Skeleton](https://github.com/victormoukhortov/WordPress-Skeleton) into your working directory. Be sure to use the `--recursive` flag to grab Wordpress as well.
2. Reset origin to your own git server: `git remote set-url origin your-git-url-here.git` (should be a bare git repository).
3. Copy `.gitignore`, `fabfile.py`, `config.py` and `local_config_sample.py` from this repository to your working directory
4. Install [Search Replace DB CLI 2.2](https://github.com/interconnectit/Search-Replace-DB/tree/2.2.0) somewhere _outside of your web root_ on _all_ target environments (such as `~/.srdb`).
5. Enter your data into `config.py` and `local_config_sample.py`
6. Rename `local_config_sample.py` to `local_config.py`
7. Commit and push your changes.
8. Run `fab local setup`, then `fab local deploy` (If you are working with a symlink, just run `fab local db_create`).
9. Navigate to your local Wordpress URL and install the database.
10. You can now run `fab staging setup` and `fab staging db_copy:local,options_table=yes` to setup your staging environment.

### Symlinks

If your local deployment directory is a symlink to your working directly, please set `local_config.deploy` to `False`. This will stop the `deploy` task from running. This task  usually runs `git reset --hard HEAD` and **will destroy your changes** otherwise.

Usage
--------------------------------
    fab [local|staging|production] [<task>]:[<arguments>]

### Tasks

    setup

Prepares the target host for a Wordpress deployment. Clones the repository and creates the database on the target host.

	db_create

Creates the database on the target host if it does not exist. Used by `setup`.

    deploy:[<branch>|branch=<branch>|tag=<tag>|<commit=<hash>][,submodules=no|yes]

Deploys the given branch/tag/commit to the target host. Performs search and replace on `wp-config.php`. If the submodules argument is given, updates submodules as well (default is `no` for performance). **Please note that this command uses `git reset --hard HEAD` and will destroy changes in the working directory**.

    db_copy:[local|staging|production][,options_table=no|yes]

Executes `db_backup` then copies the database from the given host to the target host. Executes `db_update` and `deploy` in-place afterwards. If `options_table=yes` is given, will copy the `wp_options` table as well. **Please note that copying the options table may lead to theme corruption**.

	db_update:[local|staging|production]

Uses [Search Replace DB CLI 2.2](https://github.com/interconnectit/Search-Replace-DB/tree/2.2.0) to change Wordpress-specific settings (like `site_url` and `wp_home`) in the database from the given host to the target host. Executed by `db_copy` after copying the database. You won't usually need to run this explicitly.
	
    db_backup:[<filename>]

Performs database backup on the target host. Executes `tidy_backups` afterwards. If filename is given, create file which will be ignored by `tidy_backups`.

    tidy_backups

Removes files starting with `config.backup_filename` over the limit set in `config.backup_count` on the target host. You won't usually need to run this explicitly.

    db_restore
    
Restore most recent auto-generated backup. This command will overwrite the current database.

Examples
--------------------------------
    
    fab staging setup

Setup Wordpress for deployment on staging.
    
    fab production deploy:master,submodules=yes

Deploys the `master` branch to your production environment. Also updates submodules.

    fab staging deploy:tag=1.0.1

Deploys tag `1.0.1` to your staging environment.

    fab local deploy:commit=82904baffde6ab7e62829514d662db463f7da6c4
    
Deploys commit `82904baffde6ab7e62829514d662db463f7da6c4` to your local environment
    
    fab local db_copy:staging,options_table=yes

Copies the database, including the `wp_options` table, **to** your local environment **from** your staging environment.

    fab staging db_backup:my-backup

Create a backup of the database on staging with the filename `my-backup`. This file will be ignored by `tidy_backups`.

    cd wp
    wp plugin update --all
    cd ../
    git add -A
    git commit -m 'Updating plugins'
    git push origin master
    fab staging deploy:master
    
Deploying plugin updates with the [Wordpress Command-Line-Interface](http://wp-cli.org/). Note that WP-CLI onyl works in the wordpress submodule.

    cd wp
    git fetch --tags
    git checkout 3.9
    cd ../
    git add wp
    git commit -m 'Updating Wordpress to 3.9'
    git push origin master
    fab production deploy:master,submodules=yes
    
Deploying updates to Wordpress.
    

Troubleshooting
--------------------------------

Most commands quiet fabric's default verbose output by default. If you are having any issues, run `fab --show=debug [<your command>]` to see exactly what is happening. 

Issues and pull requests are always welcome.
