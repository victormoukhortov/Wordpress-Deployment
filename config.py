#!/user/bin/env/python

# Git origin URL
git_url = ""

# Staging server configuration
staging = {
    "wordpressConfig" : {
        # Wordpress databaes name
        "DB_NAME" : "",
        # Wordpress database user
        "DB_USER" : "",
        # Wordpress database user password
        "DB_PASSWORD" : "",
        # Wordpress database host
        "DB_HOST" : "localhost",
        # URL to Wordpress installation - eg. http://myproject.com/wp
        "WP_SITEURL" : "",
        # URL to home page - eg. http://myproject.com
        "WP_HOME" : ""
    },
    # Absolute path to install directory - eg. /var/www/html/myproject
    "directory" : "",
    # Absolute path to wordpress shared directory - eg. /var/www/html/wordpress-shared
    "sharedDirectory" : "",
    # SSH user and host - eg. me@myproject.com
    "host" : "",
    # Path to SRDB 2.2.0 installation (should be outside of web root) - eg. ~/.srdb/searchreplacedbcli.php
    "srdbCli" : ""
}

# Production server configuration
production = {
    "wordpressConfig" : {
        # Wordpress databaes name
        "DB_NAME" : "",
        # Wordpress database user
        "DB_USER" : "",
        # Wordpress database user password
        "DB_PASSWORD" : "",
        # Wordpress database host
        "DB_HOST" : "localhost",
        # URL to Wordpress installation - eg. http://myproject.com/wp
        "WP_SITEURL" : "",
        # URL to home page - eg. http://myproject.com
        "WP_HOME" : ""
    },
    # Absolute path to install directory - eg. /var/www/html/myproject
    "directory" : "",
    # Absolute path to wordpress shared directory - eg. /var/www/html/wordpress-shared
    "sharedDirectory" : "",
    # SSH user and host - eg. me@myproject.com
    "host" : "",
    # Path to SRDB 2.2.0 installation (should be outside of web root) - eg. ~/.srdb/searchreplacedbcli.php
    "srdbCli" : ""
}

# Number of auto-backups to maintain
backup_count = 3
# Directory to store the backups in (relative to project directory)
backup_directory = "db-backup"
# Filename to prepent to automatically-generated backups.
backup_filename = "auto-backup"
