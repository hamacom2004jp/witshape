from cmdbox.app import common, feature
from google.oauth2 import service_account
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    JSONLoader,
    TextLoader,
    UnstructuredMarkdownLoader)
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import (
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
    TextSplitter
)
from typing import Dict, Any, Tuple, Union, List
import argparse
import chardet
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
            discription_ja="データを読込み特徴値をデータベースに登録します。",
            discription_en="Reads data and registers embedded values in the database.",
            choise=[
                dict(opt="dbhost", type="str", default="localhost", required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースホスト名を指定します。",
                     discription_en="Specify the database host name to connect to."),
                dict(opt="dbport", type="int", default=15432, required=True, multi=False, hide=True, choise=None,
                     discription_ja="接続するデータベースポートを指定します。",
                     discription_en="Specify the database port to connect to."),
                dict(opt="dbname", type="str", default="witshape", required=True, multi=False, hide=True, choise=None,
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
                dict(opt="llmprov", type="str", default="azureopenai", required=False, multi=False, hide=False, choise=["azureopenai", "openai", "vertexai"],
                     discription_ja="llmのプロバイダを指定します。",
                     discription_en="Specify llm provider."),
                dict(opt="llmprojectid", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     discription_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type="file", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     discription_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                     discription_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     discription_en="Specify the project ID for llm's provider connection."),
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
                dict(opt="loadpath", type="dir", default=".", required=False, multi=False, hide=False, choise=None,
                     discription_ja="読込みパスを指定します。",
                     discription_en="Specifies the load path."),
                dict(opt="chunk_size", type="int", default=1000, required=False, multi=False, hide=False, choise=None,
                     discription_ja="チャンクサイズを指定します。",
                     discription_en="Specifies the chunk size."),
                dict(opt="chunk_overlap", type="int", default=50, required=False, multi=False, hide=False, choise=None,
                     discription_ja="チャンクのオーバーラップサイズを指定します。",
                     discription_en="Specifies the overlap size of the chunk."),
                dict(opt="chunk_separator", type="str", default=None, required=False, multi=True, hide=False, choise=None,
                     discription_ja="チャンク化するための区切り文字を指定します。",
                     discription_en="Specifies the delimiter character for chunking."),
                dict(opt="loadgrep", type="str", default="*", required=False, multi=False, hide=False, choise=None,
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
                embeddings = OpenAIEmbeddings(model=args.llmmodel, apikey=args.llmapikey)
            elif args.llmprov == 'azureopenai':
                if args.llmmodel is None: raise ValueError("llmmodel is required.")
                if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
                if args.llmapikey is None: raise ValueError("llmapikey is required.")
                embeddings = AzureOpenAIEmbeddings(model=args.llmmodel, endpoint=args.llmendpoint, apikey=args.llmapikey)
            elif args.llmprov == 'vertexai':
                if args.llmmodel is None: raise ValueError("llmmodel is required.")
                if args.llmsvaccountfile is None: raise ValueError("llmsvaccountfile is required.")
                if args.llmprojectid is None: raise ValueError("llmprojectid is required.")
                if args.llmlocation is None: raise ValueError("llmlocation is required.")
                credentials = service_account.Credentials.from_service_account_file(args.llmsvaccountfile)
                scoped_credentials = credentials.with_scopes([
                    'https://www.googleapis.com/auth/cloud-platform'
                ])
                embeddings = VertexAIEmbeddings(model_name=args.llmmodel, project=args.llmprojectid, location=args.llmlocation, credentials=scoped_credentials)
            else:
                raise ValueError("llmprov is invalid.")

            # チャンク化オブジェクト準備
            if args.chunk_size is None: raise ValueError("chunk_size is required.")
            if args.chunk_overlap is None: raise ValueError("chunk_overlap is required.")
            chunk_separator = None if args.chunk_separator is None or len(args.chunk_separator)<=0 else args.chunk_separator
            md_splitter = MarkdownTextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
            txt_splitter = RecursiveCharacterTextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap, separators=chunk_separator)

            # ドキュメント読込み
            docs = []
            if args.loadprov == 'local':
                if args.loadpath is None: raise ValueError("loadpath is required.")
                if args.loadgrep is None: raise ValueError("loadgrep is required.")
                loadpath = Path(args.loadpath)
                if not loadpath.exists(): raise ValueError("loadpath is not found.")
                for file in loadpath.glob(args.loadgrep):
                    if not file.is_file():
                        continue
                    try:
                        if file.suffix == '.pdf': docs += self.load_pdf(file, args, txt_splitter)
                        elif file.suffix == '.docx': docs += self.load_docx(file, args, txt_splitter)
                        elif file.suffix == '.csv': docs += self.load_csv(file, args, txt_splitter)
                        elif file.suffix == '.txt': docs += self.load_txt(file, args, txt_splitter)
                        elif file.suffix == '.md': docs += self.load_md(file, args, md_splitter)
                        elif file.suffix == '.json': docs += self.load_json(file, args, txt_splitter)
                        else: raise ValueError(f"Unsupport file extension.")
                        if logger.level == logging.DEBUG:
                            logger.debug(f"embedding success. file={file}")
                    except Exception as e:
                        logger.warning(f"embedding warning: {str(e)} file={file}")
                if len(docs) == 0:
                    raise ValueError(f"No documents found. loadpath={loadpath.absolute()}, loadgrep={args.loadgrep}")
            else:
                raise ValueError("loadprov is invalid.")

            vector_store = PGVector(
                embeddings=embeddings,
                collection_name=args.servicename,
                connection=connection,
                use_jsonb=True,
            )
            ids = vector_store.add_documents(docs)
            ret = dict(success=dict(ids=ids))
            logger.info(f"embedding success. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                        f"servicename={args.servicename}, size={len(ids)}")
        except Exception as e:
            logger.error(f"embedding error: {str(e)}. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                         f"servicename={args.servicename}", exc_info=True)
            ret = dict(error=f"embedding error: {str(e)} dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                             f"servicename={args.servicename}")
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return 1, ret, None
        return 0, ret, None

    def load_csv(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        CSVファイルを読み込みます

        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト

        Returns:
            List[Document]: ドキュメントリスト
        """
        enc = self.load_encodeing(file)
        loader = CSVLoader(file, encoding=enc)
        return loader.load_and_split(text_splitter=splitter)

    def load_docx(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        DOCXファイルを読み込みます
        
        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト

        Returns:
            List[Document]: ドキュメントリスト
        """
        loader = Docx2txtLoader(file)
        return loader.load_and_split(text_splitter=splitter)

    def load_json(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        JSONファイルを読み込みます

        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト

        Returns:
            List[Document]: ドキュメントリスト
        """
        loader = JSONLoader(file, jq_schema=".", text_content=False)
        return loader.load_and_split(text_splitter=splitter)

    def load_md(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        MDファイルを読み込みます

        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト

        Returns:
            List[Document]: ドキュメントリスト
        """
        loader = UnstructuredMarkdownLoader(file, text_splitter=splitter)
        return loader.load_and_split(text_splitter=splitter)

    def load_pdf(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        PDFファイルを読み込みます

        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト

        Returns:
            List[Document]: ドキュメントリスト
        """ 
        loader = PyPDFLoader(file)
        return loader.load_and_split(text_splitter=splitter)

    def load_txt(self, file:Path, args:argparse.Namespace, splitter:TextSplitter) -> List[Document]:
        """
        TXTファイルを読み込みます

        Args:
            file (Path): ファイル
            args (argparse.Namespace): 引数
            splitter (TextSplitter): テキスト分割オブジェクト
        
        Returns:
            List[Document]: ドキュメントリスト
        """
        enc = self.load_encodeing(file)
        loader = TextLoader(file, encoding=enc)
        return loader.load_and_split(text_splitter=splitter)

    def load_encodeing(self, file:Path) -> str:
        """
        ファイルのエンコーディングを取得します

        Args:
            file (Path): ファイル

        Returns:
            str: エンコーディング
        """
        with open(file, "rb") as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result["encoding"]
            encoding = encoding.lower()
            if encoding == "shift_jis":
                return "shift-jis"
            else:
                return encoding
