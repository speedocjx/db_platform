try:
    import MySQLdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()