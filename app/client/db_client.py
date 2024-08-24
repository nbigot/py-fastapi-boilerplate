import logging
from app.db.mysql.connection import MySQLConnectionArgs
from app.client.mysql_client import MySQLClient
from app.db.postgresql.connection import PostgreSQLConnectionArgs
from app.client.postgresql_client import PostgreSQLClient
from app.router.default.models import ApiV1ListTablesResponse


class DBClient:
    def __init__(self, config: dict):
        self.config: dict = config
        self.logger = logging.getLogger("db")
        self.client = (
            self.build_postgresql_client()
            if self.config["db"]["engine"].lower() == "postgresql"
            else self.build_mysql_client()
        )

    def disconnect(self) -> None:
        self.client.disconnect()

    # This is a demo method
    def get_list_of_tables(
        self,
        limit: int,
    ) -> ApiV1ListTablesResponse:
        return self.client.get_list_of_tables(limit=limit)

    def build_mysql_client(self) -> MySQLClient:
        self.client = MySQLClient(
            cnx_args=MySQLConnectionArgs(
                hostname=self.config["db"]["mysql"]["hostname"],
                tcp_port=self.config["db"]["mysql"]["port"],
                login=self.config["db"]["mysql"]["username"],
                password=self.config["db"]["mysql"]["password"],
                database=self.config["db"]["mysql"]["database"],
                program=self.config["db"]["mysql"]["program"],
            ),
            logger=logging.getLogger("db.client"),
            dry_run=self.config["db"]["dry_run"],
        )

    def build_postgresql_client(self) -> PostgreSQLClient:
        self.client = PostgreSQLClient(
            cnx_args=PostgreSQLConnectionArgs(
                hostname=self.config["db"]["postgresql"]["hostname"],
                tcp_port=self.config["db"]["postgresql"]["port"],
                login=self.config["db"]["postgresql"]["username"],
                password=self.config["db"]["postgresql"]["password"],
                database=self.config["db"]["postgresql"]["database"],
                program=self.config["db"]["postgresql"]["program"],
            ),
            logger=logging.getLogger("db.client"),
            dry_run=self.config["db"]["dry_run"],
        )
