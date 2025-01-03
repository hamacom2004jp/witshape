from cmdbox.app import feature
from google.oauth2 import service_account
from pathlib import Path
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    JSONLoader,
    TextLoader,
    UnstructuredMarkdownLoader)
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import TextSplitter, MarkdownTextSplitter
from pdfplumber.table import TableSettings
from typing import Dict, Any, Tuple, Union, List
import argparse
import chardet


class PgvectorBase(feature.Feature):

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="-",
            discription_en="-",
            choice=[
                dict(opt="dbhost", type="str", default="localhost", required=True, multi=False, hide=True, choice=None,
                     discription_ja="接続するデータベースホスト名を指定します。",
                     discription_en="Specify the database host name to connect to."),
                dict(opt="dbport", type="int", default=15432, required=True, multi=False, hide=True, choice=None,
                     discription_ja="接続するデータベースポートを指定します。",
                     discription_en="Specify the database port to connect to."),
                dict(opt="dbname", type="str", default="witshape", required=True, multi=False, hide=True, choice=None,
                     discription_ja="接続するデータベース名を指定します。",
                     discription_en="Specify the name of the database to connect to."),
                dict(opt="dbuser", type="str", default="postgres", required=True, multi=False, hide=True, choice=None,
                     discription_ja="接続するデータベースユーザー名を指定します。",
                     discription_en="Specifies the database user name to connect to."),
                dict(opt="dbpass", type="str", default="postgres", required=True, multi=False, hide=True, choice=None,
                     discription_ja="接続するデータベースパスワードを指定します。",
                     discription_en="Specify the database password to connect to."),
                dict(opt="dbtimeout", type="int", default=30, required=False, multi=False, hide=True, choice=None,
                     discription_ja="データベース接続のタイムアウトを指定します。",
                     discription_en="Specifies the database connection timeout."),
                dict(opt="servicename", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="サービス名を指定します。",
                     discription_en="Specify the service name."),
                dict(opt="llmprov", type="str", default="azureopenai", required=False, multi=False, hide=False,
                     choice=["azureopenai", "openai", "vertexai", "ollama"],
                     discription_ja="llmのプロバイダを指定します。",
                     discription_en="Specify llm provider.",
                     choice_show=dict(azureopenai=["llmapikey", "llmendpoint"],
                                      openai=["llmapikey", "llmendpoint"],
                                      vertexai=["llmprojectid", "llmsvaccountfile", "llmlocation"],
                                      ollama=["llmendpoint", "llmmodel"],),
                     ),
                dict(opt="llmprojectid", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     discription_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     discription_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     discription_en="Specifies the location for llm provider connections."),
                dict(opt="llmapikey", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     discription_en="Specify API key for llm provider connection."),
                dict(opt="llmendpoint", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     discription_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type="str", default="text-multilingual-embedding-002", required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmの埋め込みモデルを指定します。",
                     discription_en="Specifies the embedding model for llm."),
            ])

    def create_embeddings(self, args:argparse.Namespace) -> Embeddings:
        """
        埋め込みオブジェクトを作成します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            Embeddings: 埋め込みオブジェクト
        """
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
        elif args.llmprov == 'ollama':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
            embeddings = OllamaEmbeddings(model=args.llmmodel, base_url=args.llmendpoint)
        else:
            raise ValueError("llmprov is invalid.")
        return embeddings

    def create_vectorstore(self, args:argparse.Namespace, embeddings:Any) -> PGVector:
        """
        ベクトルストアオブジェクトを作成します

        Args:
            args (argparse.Namespace): 引数
            embeddings (Any): 埋め込みオブジェクト

        Returns:
            PGVector: ベクトルストアオブジェクト
        """
        if args.dbhost is None: raise ValueError("dbhost is required.")
        if args.dbport is None: raise ValueError("dbport is required.")
        if args.dbname is None: raise ValueError("dbname is required.")
        if args.dbuser is None: raise ValueError("dbuser is required.")
        if args.dbpass is None: raise ValueError("dbpass is required.")
        if args.servicename is None: raise ValueError("servicename is required.")
        connection = f"postgresql+psycopg://{args.dbuser}:{args.dbpass}@{args.dbhost}:{args.dbport}/{args.dbname}"
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=args.servicename,
            connection=connection,
            use_jsonb=True,
        )
        return vector_store

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
        loader = UnstructuredMarkdownLoader(str(file), text_splitter=splitter)
        return loader.load_and_split(text_splitter=splitter)

    def load_pdf(self, file:Path, args:argparse.Namespace, splitter:TextSplitter, md_splitter:MarkdownTextSplitter) -> List[Document]:
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
