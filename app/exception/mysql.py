from pymysql.constants.ER import DUP_ENTRY, LOCK_WAIT_TIMEOUT, NO_SUCH_TABLE, TABLEACCESS_DENIED_ERROR

# Examples of retryable errors:
# Code: 2013 Lost connection to MySQL server during query:
# Code: 2006 MySQL server has gone away 'Une connexion existante a dû être fermée par l’hôte distant'
# Code: 2003 MySQL network connection has been refused
# Code: 1205 Lock wait timeout exceeded; try restarting transaction
MYSQL_RECOVERABLE_ERRORS = [2013, 2006, 2003, 1205]

MYSQL_ERRORS = {
    DUP_ENTRY: "Duplicate entry",
    TABLEACCESS_DENIED_ERROR: "Command denied to user",
    NO_SUCH_TABLE: "Table doesn't exist",
    LOCK_WAIT_TIMEOUT: "Lock wait timeout exceeded",
    2013: "Lost connection to MySQL server during query",
    2006: "MySQL server has gone away",
    2003: "Can't connect to MySQL server",
}

ERROR_CANNOT_EXECUTE_MYSQL_COMMAND = "cannot execute mysql command"
