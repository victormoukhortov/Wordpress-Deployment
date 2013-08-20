#!/user/bin/env/python

git = {
    "url" : "",
    "user" : "",
    "password" : "",
}

table_prefix = "wp_"

dev = {
    'wordpress' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "table_prefix" : "wp_"
    },
    "directory" : "",
    "hosts" : [""]
}

staging = {
    'wordpressConfig' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "table_prefix" : "wp_"
    },
    "directory" : "",
    "hosts" : [""]
}

production = {
    'wordpressConfig' : {
        "DB_NAME" : "",
        "DB_USER" : "",
        "DB_PASSWORD" : "",
        "DB_HOST" : "localhost",
        "DB_CHARSET" : "utf8",
        "DB_COLLATE" : "",
        "table_prefix" : "wp_"
    },
    "directory" : "",
    "hosts" : [""]
}
    
backup_count = 3
backup_directory = '.db-backup'
