(Another) Wordpress Deployment Strategy
================================
This is a simple command-line deployment tool for Wordpress using Python Fabric.

Assumptions
--------------------------------
* Using [My Fork](https://github.com/victormoukhortov/WordPress-Skeleton) of Mark Jaquith's Excellent Wordpress-Skeleton ([diff here](https://github.com/markjaquith/WordPress-Skeleton/compare/master...victormoukhortov:master))
* Using git for version control

Getting Started
--------------------------------
These instructions assume that you will be deploying to a local server. If you don't want to do this, you can install directly onto staging just as well. You will still need to fill in `local_config.py` if you want to synchronize your database to/from local.

1. Clone [Wordpress Skeleton](https://github.com/victormoukhortov/WordPress-Skeleton) into your working directory. Be sure to use the `--recursive` flag to grab Wordpress as well.
2. Reset origin to your own git server: `git remote set-url origin your-git-url-here.git` (should be a bare git repository).
3. Copy `fabfile.py`, `config.py` and `local_config.py` from this repository to your working directory
4. Enter your data into `config.py` and `local_config.py`
5. Commit and push your changes
6. Run `fab local setup`, then `fab local deploy`
7. Navigate to `localhost/your-wordpress-directory/wp/wp-admin/install.php` and install Wordpress.
8. You can now run `fab staging setup` and `fab staging db_copy:local` to setup your staging environment.


Usage
--------------------------------
    fab [local|staging|production] [<task>]:[<arguments>]

### Tasks

    setup

Prepares the target host for a Wordpress deployment. Clones the repository and creates the database on the target host.

    deploy:[<branch>|branch=<branch>|tag=<tag>|<commit=<hash>],[submodules=no|yes]

Deploys the given branch/tag/commit to the target host. Performs search and replace on `wp-config.php`. If the submodules argument is given, updates submodules as well (default is `no` for performance).

    db_copy:[local|staging|production]

Executes `db_backup` then copies the database from the given host to the target host. Executes `mysql_update` and `deploy` in-place afterwards.

    db_backup:[<filename>]

Performs database backup on the target host. Executes `tidy_backups` afterwards. If filename is given, create file which will be ignored by `tidy_backups`.

    tidy_backups

Removes files starting with `config.backup_filename` over the limit set in `config.backup_count` on the target host. You won't usually need to run this explicitly.

    db_restore
    
Restore most recent auto-generated backup. This command will overwrite the current database.

    db_update

Updates environment-specific Wordpress settings in the database on the target host. Run this to propagate changes to your configuration files into the database.

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
    
    fab local db_copy:staging

Copies the database **from** your staging environment **to** your local environment.

    fab staging db_backup:my-backup

Create a backup of the database on staging with the filename `my-backup`. This file will be ignored by `tidy_backups`.

Troubleshooting
--------------------------------

Most commands quiet fabric's default verbose output. If you are having any issues, run `fab --show=debug [<your command>]` to see exactly what is happening. 

Issues and pull requests are always welcome.
