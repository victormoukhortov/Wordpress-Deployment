#!/user/bin/env/python

# Git origin URL
git_url = ""

# Staging server configuration
staging = {
    'wordpressConfig' : {
        # Wordpress databaes name
        "DB_NAME" : "",
        # Wordpress database user
        "DB_USER" : "",
        # Wordpress database user password
        "DB_PASSWORD" : "",
        # Wordpress database host
        "DB_HOST" : "localhost",
        # URL to Wordpress installation - eg. http://myproject.com/blog/wp
        "WP_HOME" : "",
        # URL to blog home page - eg. http://myproject.com/blog
        "WP_SITEURL" : "",
    },
    # Absolute path to install directory - eg. /var/www/html/myproject
    "directory" : "",
    # SSH user and host - eg. me@myproject.com
    "host" : ""
}

# Production server configuration
production = {
    'wordpressConfig' : {
        # Wordpress databaes name
        "DB_NAME" : "",
        # Wordpress database user
        "DB_USER" : "",
        # Wordpress database user password
        "DB_PASSWORD" : "",
        # Wordpress database host
        "DB_HOST" : "localhost",
        # URL to Wordpress installation - eg. http://myproject.com/blog/wp
        "WP_HOME" : "",
        # URL to blog home page - eg. http://myproject.com/blog
        "WP_SITEURL" : "",
    },
    # Absolute path to install directory - eg. /var/www/html/myproject
    "directory" : "",
    # SSH user and host - eg. me@myproject.com
    "host" : ""
}

# Number of auto-backups to maintain
backup_count = 3
# Directory to store the backups in (relative to project directory)
backup_directory = 'db-backup'
# Filename to prepent to automatically-generated backups.
backup_filename = 'auto-backup'
