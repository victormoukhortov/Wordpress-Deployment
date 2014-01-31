# Local configuration
local = {
    "wordpressConfig" : {
        # Wordpress databaes name
        "DB_NAME" : "",
        # Wordpress database user
        "DB_USER" : "",
        # Wordpress database user password
        "DB_PASSWORD" : "",
        # Wordpress database host
        "DB_HOST" : "localhost",
        # URL to Wordpress installation - eg. http://localhost/myproject/wp
        "WP_SITEURL" : "",
        # URL to home page - eg. http://localhost/myproject
        "WP_HOME" : ""
    },
    # Absolute path to install directory - eg. /var/www/html/myproject
    "directory" : "",
    # Absolute path to wordpress shared directory - eg. /var/www/html/wordpress-shared
    "sharedDirectory" : "",
    # SSH user and host - eg. me@localhost
    "host" : "",
    # Path to SRDB 2.2.0 installation (should be outside of web root) - eg. ~/.srdb/searchreplacedbcli.php
    "srdbCli" : "",
    # Whether to run deployments on this environemnt (Set to False if you are serving your working directory)
    "deploy" : False
}
