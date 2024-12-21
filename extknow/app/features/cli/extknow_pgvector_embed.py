from cmdbox.app import common, feature
from extknow.app import pgvector
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PgvectorEmbedd(feature.Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "pgvector"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'embedd'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="サービスを削除します。",
            discription_en="Delete the service.",
            choise=[
                dict(opt="dbhost", type="str", default="localhost", required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースホスト名を指定します。",
                     discription_en="Specify the database host name to connect to."),
                dict(opt="dbport", type="int", default=5432, required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースポートを指定します。",
                     discription_en="Specify the database port to connect to."),
                dict(opt="dbname", type="str", default="extknow", required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベース名を指定します。",
                     discription_en="Specify the name of the database to connect to."),
                dict(opt="dbuser", type="str", default="postgres", required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースユーザー名を指定します。",
                     discription_en="Specifies the database user name to connect to."),
                dict(opt="dbpass", type="str", default="postgres", required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースパスワードを指定します。",
                     discription_en="Specify the database password to connect to."),
                dict(opt="dbtimeout", type="int", default=30, required=False, multi=False, hide=True, choise=None,
                     discription_ja="データベース接続のタイムアウトを指定します。",
                     discription_en="Specifies the database connection timeout."),
                dict(opt="servicename", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="サービス名を指定します。",
                     discription_en="Specify the service name."),
                dict(opt="llmprov", type="str", default="azureopenai", required=False, multi=False, hide=False, choise=["azureopenai", "openai"],
                     discription_ja="llmのプロバイダを指定します。",
                     discription_en="Specify llm provider."),
                dict(opt="llmapikey", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     discription_en="Specify API key for llm provider connection."),
                dict(opt="llmendpoint", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     discription_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type="str", default="text-embedding-ada-002", required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmの埋め込みモデルを指定します。",
                     discription_en="Specifies the embedding model for llm."),
                dict(opt="loadprov", type="str", default="azureopenai", required=False, multi=False, hide=False, choise=["local"],
                     discription_ja="読込みプロバイダを指定します。",
                     discription_en="Specifies the load provider."),
                dict(opt="loadpath", type="str", default=".", required=False, multi=False, hide=False, choise=None,
                     discription_ja="読込みパスを指定します。",
                     discription_en="Specifies the load path."),
                dict(opt="loadgrep", type="str", default=".", required=False, multi=False, hide=False, choise=None,
                     discription_ja="読込みgrepパターンを指定します。",
                     discription_en="Specifies a load grep pattern."),
            ])

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        try:
            if args.dbhost is None: raise ValueError("dbhost is required.")
            if args.dbport is None: raise ValueError("dbport is required.")
            if args.dbname is None: raise ValueError("dbname is required.")
            if args.dbuser is None: raise ValueError("dbuser is required.")
            if args.dbpass is None: raise ValueError("dbpass is required.")
            if args.servicename is None: raise ValueError("servicename is required.")
            connection = f"postgresql+psycopg://{args.dbuser}:{args.dbpass}@{args.dbhost}:{args.dbport}/{args.dbname}"
            if args.llmprov == 'openai':
                if args.llmmodel is None: raise ValueError("llmmodel is required.")
                if args.llmapikey is None: raise ValueError("llmapikey is required.")
                if args.servicename is None: raise ValueError("servicename is required.")
                from langchain_openai import OpenAIEmbeddings
                embeddings = OpenAIEmbeddings(model=args.llmmodel, apikey=args.llmapikey)
            elif args.llmprov == 'azureopenai':
                if args.llmmodel is None: raise ValueError("llmmodel is required.")
                if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
                if args.llmapikey is None: raise ValueError("llmapikey is required.")
                if args.servicename is None: raise ValueError("servicename is required.")
                from langchain_openai import AzureOpenAIEmbeddings
                embeddings = AzureOpenAIEmbeddings(model=args.llmmodel, endpoint=args.llmendpoint, apikey=args.llmapikey)
            else:
                raise ValueError("llmprov is invalid.")
            if args.loadprov == 'local':
                if args.loadpath is None: raise ValueError("loadpath is required.")
                if args.loadgrep is None: raise ValueError("loadgrep is required.")
                from langchain_community.document_loaders import DirectoryLoader
                from langchain_unstructured.document_loaders import UnstructuredLoader
                loader = DirectoryLoader(args.loadpath, glob=args.loadgrep, recursive=True, loader_cls=UnstructuredLoader)
            else:
                raise ValueError("loadprov is invalid.")

            from langchain_postgres import PGVector
            vector_store = PGVector(
                embeddings=embeddings,
                collection_name=args.servicename,
                connection=connection,
                use_jsonb=True,
            )
            docs = loader.load()
            ids = vector_store.add_documents(docs)
            ret = dict(success=dict(ids=ids))
            logger.info(f"embedding success. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                        f"servicename={args.servicename}, size={len(ids)}")
        except Exception as e:
            logger.error(f"embedding error: {str(e)}. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                         f"servicename={args.servicename}")
            ret = dict(error=f"embedding error: {str(e)} dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                             f"servicename={args.servicename}")
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return 1, ret, None
        return 0, ret, None

