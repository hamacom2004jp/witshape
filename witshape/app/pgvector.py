from pathlib import Path
import logging
import psycopg


class Pgvector:
    def __init__(self, logger:logging.Logger, dbhost:str, dbport:int, dbname:str, dbuser:str, dbpass:str, dbtimeout:int):
        """
        コンストラクタ

        Args:
            logger (logging.Logger): ロガー
            dbhost (str): データベースホスト名
            dbport (int): データベースポート
            dbname (str): データベース名
            dbuser (str): データベースユーザー名
            dbpass (str): データベースパスワード
            dbtimeout (int): データベース接続のタイムアウト
        """
        if logger is None:
            raise ValueError("logger is required.")
        if dbhost is None:
            raise ValueError("dbhost is required.")
        if dbport is None:
            raise ValueError("dbport is required.")
        if dbname is None:
            raise ValueError("dbname is required.")
        if dbuser is None:
            raise ValueError("dbuser is required.")
        if dbpass is None:
            raise ValueError("dbpass is required.")
        if dbtimeout is None:
            raise ValueError("dbtimeout is required.")
        self.logger = logger
        self.dbhost = dbhost
        self.dbport = dbport
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbtimeout = dbtimeout

    def create_db(self, newdbname:str):
        """
        データベースを作成します

        Args:
            newdbname (str): 作成するデータベース名
        """
        if newdbname is None:
            raise ValueError("newdbname is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {newdbname}")
                cur.execute(f"CREATE SCHEMA {self.dbuser}")
                cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {newdbname} TO {self.dbuser}")
                cur.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {self.dbuser} TO {self.dbuser}")
                cur.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {self.dbuser} TO {self.dbuser}")
                cur.execute(f"GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA {self.dbuser} TO {self.dbuser}")
                cur.execute(f"GRANT ALL PRIVILEGES ON SCHEMA {self.dbuser} TO {self.dbuser}")
                cur.execute(f"CREATE EXTENSION vector")
                cur.execute(f"SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                for record in cur:
                    self.logger.info(f"extversion={record}")

    def drop_db(self, dbname:str):
        """
        データベースを削除します

        Args:
            dbname (str): 削除するデータベース名
        """
        if dbname is None:
            raise ValueError("dbname is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"DROP DATABASE {dbname}")

    def select_docids(self, servicename:str, file:Path=None):
        """
        ドキュメントIDを取得します

        Args:
            servicename (str): サービス名
            file (Path): ファイル名
        """
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                where = None
                if servicename is not None and file is not None:
                    where = f"WHERE c.name = '{servicename}' AND e.cmetadata->>'source' = '{file}'"
                elif servicename is not None:
                    where = f"WHERE c.name = '{servicename}'"
                else:
                    raise ValueError(f"select_docids param invalid. savetype={savetype}, servicename={servicename}, file={file}")
                cur.execute(f"SELECT e.id FROM {self.dbuser}.langchain_pg_embedding e inner join {self.dbuser}.langchain_pg_collection c " + \
                            f"ON e.collection_id = c.uuid {where}")
                return [record[0] for record in cur]
