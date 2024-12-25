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

    def create_table(self):
        """
        テーブルを作成します
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
                cur.execute(f"CREATE TABLE {self.dbuser}.service (" \
                            + f"servicename text PRIMARY KEY," \
                            + f"metadate json," \
                            + f"createuser text," \
                            + f"updateuser text," \
                            + f"createdt timestamp default CURRENT_TIMESTAMP," \
                            + f"updatedt timestamp default CURRENT_TIMESTAMP)")
                cur.execute(f"CREATE TABLE {self.dbuser}.doc (" \
                            + f"id SERIAL PRIMARY KEY," \
                            + f"servicename text not null," \
                            + f"url text not null," \
                            + f"contenttype text not null," \
                            + f"filepath text not null," \
                            + f"filesize long default 0," \
                            + f"metadate json," \
                            + f"createuser text," \
                            + f"updateuser text," \
                            + f"createdt timestamp default CURRENT_TIMESTAMP," \
                            + f"updatedt timestamp default CURRENT_TIMESTAMP)")
                cur.execute(f"CREATE UNIQUE INDEX {self.dbuser}.doc_ix1 on doc (servicename, filepath)")
                cur.execute(f"CREATE INDEX {self.dbuser}.doc_ix2 on doc (servicename, metadate)")
                cur.execute(f"ALTER TABLE {self.dbuser}.doc ADD CONSTRAINT {self.dbuser}.doc_fk1 " + \
                            f"FOREIGN KEY (servicename) REFERENCES {self.dbuser}.service (servicename)")
                cur.execute(f"CREATE TABLE {self.dbuser}.chunk (" \
                            + f"id SERIAL PRIMARY KEY," \
                            + f"docid long not null," \
                            + f"servicename text not null," \
                            + f"page text," \
                            + f"content text," \
                            + f"embedding vector" \
                            + f")")
                cur.execute(f"CREATE INDEX {self.dbuser}.chunk_ix1 on chunk (servicename, embedding)")
                cur.execute(f"CREATE INDEX {self.dbuser}.chunk_ix2 on chunk (servicename, docid)")
                cur.execute(f"ALTER TABLE {self.dbuser}.chunk ADD CONSTRAINT {self.dbuser}.chunk_fk1 " + \
                            f"FOREIGN KEY (servicename) REFERENCES {self.dbuser}.service (servicename)")

    def drop_table(self):
        """
        テーブルを削除します
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
                cur.execute(f"DROP TABLE {self.dbuser}.chunk")
                cur.execute(f"DROP TABLE {self.dbuser}.doc")
                cur.execute(f"DROP TABLE {self.dbuser}.service")

    def insert_service(self, servicename:str, metadate:dict, createuser:str, updateuser:str):
        """
        サービス情報を登録します

        Args:
            servicename (str): サービス名
            metadate (dict): メタデータ
            createuser (str): 作成ユーザー
            updateuser (str): 更新ユーザー
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        if metadate is None:
            raise ValueError("metadate is required.")
        if createuser is None:
            raise ValueError("createuser is required.")
        if updateuser is None:
            raise ValueError("updateuser is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"INSERT INTO {self.dbuser}.service (servicename, metadate, createuser, updateuser) " + \
                            f"VALUES (%s, %s, %s, %s)",
                            (servicename, metadate, createuser, updateuser))

    def update_service(self, servicename:str, metadate:dict, updateuser:str):
        """
        サービス情報を更新します

        Args:
            servicename (str): サービス名
            metadate (dict): メタデータ
            updateuser (str): 更新ユーザー
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        if metadate is None:
            raise ValueError("metadate is required.")
        if updateuser is None:
            raise ValueError("updateuser is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {self.dbuser}.service " + \
                            f"SET metadate=%s, updateuser=%s, updatedt=CURRENT_TIMESTAMP WHERE servicename=%s",
                            (metadate, updateuser, servicename))

    def delete_service(self, servicename:str):
        """
        サービス情報を削除します。
        同時に、サービスに紐づくドキュメント情報とチャンク情報も削除します。

        Args:
            servicename (str): サービス名
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.dbuser}.chunk WHERE servicename=%s", (servicename,))
                cur.execute(f"DELETE FROM {self.dbuser}.doc WHERE servicename=%s", (servicename,))
                cur.execute(f"DELETE FROM {self.dbuser}.service WHERE servicename=%s", (servicename,))

    def select_service(self, servicename:str=None):
        """
        サービス情報を取得します

        Args:
            servicename (str): サービス名

        Returns:
            List[Dict[str, Any]]: サービス情報
        """
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            with conn.cursor() as cur:
                if servicename is None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.service")
                else:
                    cur.execute(f"SELECT * FROM {self.dbuser}.service WHERE servicename=%s", (servicename,))
                return [dict(servicename=record[0], metadate=record[1], createuser=record[2],
                             updateuser=record[3], createdt=record[4], updatedt=record[5]) for record in cur]

    def insert_doc(self, servicename:str, url:str, contenttype:str, filepath:str, filesize:int, metadate:dict, createuser:str, updateuser:str):
        """
        ドキュメント情報を登録します

        Args:
            servicename (str): サービス名
            url (str): URL
            contenttype (str): コンテントタイプ
            filepath (str): ファイルパス
            filesize (int): ファイルサイズ
            metadate (dict): メタデータ
            createuser (str): 作成ユーザー
            updateuser (str): 更新ユーザー
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        if url is None:
            raise ValueError("url is required.")
        if contenttype is None:
            raise ValueError("contenttype is required.")
        if filepath is None:
            raise ValueError("filepath is required.")
        if filesize is None:
            raise ValueError("filesize is required.")
        if metadate is None:
            raise ValueError("metadate is required.")
        if createuser is None:
            raise ValueError("createuser is required.")
        if updateuser is None:
            raise ValueError("updateuser is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"INSERT INTO {self.dbuser}.doc (servicename, url, contenttype, filepath, filesize, metadate, createuser, updateuser) " + \
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (servicename, url, contenttype, filepath, filesize, metadate, createuser, updateuser))

    def update_doc(self, id:int, url:str, contenttype:str, filepath:str, filesize:int, metadate:dict, updateuser:str):
        """
        ドキュメント情報を更新します

        Args:
            id (int): ID
            url (str): URL
            contenttype (str): コンテントタイプ
            filepath (str): ファイルパス
            filesize (int): ファイルサイズ
            metadate (dict): メタデータ
            updateuser (str): 更新ユーザー
        """
        if id is None:
            raise ValueError("id is required.")
        if url is None:
            raise ValueError("url is required.")
        if contenttype is None:
            raise ValueError("contenttype is required.")
        if filepath is None:
            raise ValueError("filepath is required.")
        if filesize is None:
            raise ValueError("filesize is required.")
        if metadate is None:
            raise ValueError("metadate is required.")
        if updateuser is None:
            raise ValueError("updateuser is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {self.dbuser}.doc " + \
                            f"SET url=%s, contenttype=%s, filepath=%s, filesize=%s, metadate=%s, updateuser=%s, updatedt=CURRENT_TIMESTAMP WHERE id=%s",
                            (url, contenttype, filepath, filesize, metadate, updateuser, id))

    def delete_doc(self, id:int):
        """
        ドキュメント情報を削除します。
        同時に、ドキュメントに紐づくチャンク情報も削除します。

        Args:
            id (int): ID
        """
        if id is None:
            raise ValueError("id is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.dbuser}.chunk WHERE docid=%s", (id,))
                cur.execute(f"DELETE FROM {self.dbuser}.doc WHERE id=%s", (id,))

    def select_doc(self, servicename:str, id:int=None, filepath:str=None, metadate:dict=None):
        """
        ドキュメント情報を取得します

        Args:
            servicename (str): サービス名
            id (int): ID
            filepath (str): ファイルパス
            metadate (dict): メタデータ

        Returns:
            List[Dict[str, Any]]: ドキュメント情報
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            with conn.cursor() as cur:
                if id is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.doc WHERE id=%s", (id))
                elif filepath is not None and metadate is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.doc WHERE servicename=%s AND filepath=%s AND metadate=%s", (servicename, f"%{filepath}%", metadate))
                elif filepath is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.doc WHERE servicename=%s AND filepath=%s", (servicename, f"%{filepath}%"))
                elif metadate is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.doc WHERE servicename=%s AND metadate=%s", (servicename, metadate))
                return [dict(id=record[0], servicename=record[1], url=record[2], contenttype=record[3],
                             filepath=record[4], filesize=record[5], metadate=record[6],
                             createuser=record[7], updateuser=record[8], createdt=record[9], updatedt=record[10]) for record in cur]

    def insert_chunk(self, docid:int, servicename:str, page:str, content:str, embedding:list):
        """
        チャンク情報を登録します

        Args:
            docid (int): ドキュメントID
            servicename (str): サービス名
            page (str): ページ
            content (str): コンテンツ
            embedding (list): ベクトル
        """
        if docid is None:
            raise ValueError("docid is required.")
        if servicename is None:
            raise ValueError("servicename is required.")
        if page is None:
            raise ValueError("page is required.")
        if content is None:
            raise ValueError("content is required.")
        if embedding is None:
            raise ValueError("embedding is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"INSERT INTO {self.dbuser}.chunk (docid, servicename, page, content, embedding) " + \
                            f"VALUES (%s, %s, %s, %s, %s)",
                            (docid, servicename, page, content, embedding))

    def update_chunk(self, id:int, page:str, content:str, embedding:list):
        """
        チャンク情報を更新します

        Args:
            id (int): ID
            page (str): ページ
            content (str): コンテンツ
            embedding (list): ベクトル
        """
        if id is None:
            raise ValueError("id is required.")
        if page is None:
            raise ValueError("page is required.")
        if content is None:
            raise ValueError("content is required.")
        if embedding is None:
            raise ValueError("embedding is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {self.dbuser}.chunk " + \
                            f"SET page=%s, content=%s, embedding=%s, updatedt=CURRENT_TIMESTAMP WHERE id=%s",
                            (page, content, embedding, id))

    def delete_chunk(self, id:int):
        """
        チャンク情報を削除します

        Args:
            id (int): ID
        """
        if id is None:
            raise ValueError("id is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.dbuser}.chunk WHERE id=%s", (id,))

    def select_chunk(self, servicename:str, id:int=None, docid:int=None, embedding:list=None):
        """
        チャンク情報を取得します

        Args:
            servicename (str): サービス名
            id (int): ID
            docid (int): ドキュメントID
            embedding (list): ベクトル

        Returns:
            List[Dict[str, Any]]: チャンク情報
        """
        if servicename is None:
            raise ValueError("servicename is required.")
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            with conn.cursor() as cur:
                if id is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.chunk WHERE id=%s", (id,))
                elif docid is not None and embedding is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.chunk WHERE servicename=%s AND docid=%s AND embedding=%s", (servicename, docid, embedding))
                elif docid is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.chunk WHERE servicename=%s AND docid=%s", (servicename, docid,))
                elif embedding is not None:
                    cur.execute(f"SELECT * FROM {self.dbuser}.chunk WHERE servicename=%s AND embedding=%s", (servicename, embedding))
                return [dict(id=record[0], docid=record[1], servicename=record[2], page=record[3],
                             content=record[4], embedding=record[5]) for record in cur]
