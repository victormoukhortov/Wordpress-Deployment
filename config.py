#!/user/bin/env/python

git_url = ""

local = {
    'wordpressConfig' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "WP_HOME" : "",
        "WP_SITEURL" : ""
    },
    "directory" : "",
    "host" : ""
}

staging = {
    'wordpressConfig' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "WP_HOME" : "",
        "WP_SITEURL" : ""
    },
    "directory" : "",
    "host" : ""
}

production = {
    'wordpressConfig' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "WP_HOME" : "",
        "WP_SITEURL" : ""
    },
    "directory" : "",
    "host" : ""
}
    
backup_count = 3
backup_directory = '.db-backup'
backup_filename = 'auto-backup'
