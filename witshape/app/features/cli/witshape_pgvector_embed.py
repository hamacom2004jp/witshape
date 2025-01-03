from cmdbox.app import common
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
    TextSplitter
)
from typing import Dict, Any, Tuple, Union, List
from witshape.app import pgvector
from witshape.app.features.cli import pgvector_base
import argparse
import logging
import pdfplumber


class PgvectorEmbedd(pgvector_base.PgvectorBase):
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
        opt = super().get_option()
        opt["discription_ja"] = "データを読込み特徴値をデータベースに登録します。"
        opt["discription_en"] = "Reads data and registers embedded values in the database."
        opt["choice"] += [
            dict(opt="loadprov", type="str", default="azureopenai", required=False, multi=False, hide=False, choice=["local"],
                discription_ja="読込みプロバイダを指定します。",
                discription_en="Specifies the load provider."),
            dict(opt="loadpath", type="dir", default=".", required=False, multi=False, hide=False, choice=None,
                discription_ja="読込みパスを指定します。",
                discription_en="Specifies the load path."),
            dict(opt="loadgrep", type="str", default="*", required=False, multi=False, hide=False, choice=None,
                discription_ja="読込みgrepパターンを指定します。",
                discription_en="Specifies a load grep pattern."),
            dict(opt="savetype", type="str", default="per_doc", required=False, multi=False, hide=False, choice=["per_doc", "per_service", "add_only"],
                discription_ja="保存パターンを指定します。 `per_doc` :ドキュメント単位、 `per_service` :サービス単位、 `add_only` :追加のみ",
                discription_en="Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only"),
            dict(opt="pdf_chunk_table", type="str", default="table", required=False, multi=False, hide=False, choice=["none", "table", "row_with_header"],
                discription_ja="PDFファイル内の表のチャンク方法を指定します。 `none` :表単位でチャンクしない、 `table` :表単位、 `row_with_header` :行単位(ヘッダ付き)",
                discription_en="Specifies how to chunk tables in the PDF file. `none` :do not chunk by table, `table` :by table, `row_with_header` :by row (with header)"),
            dict(opt="chunk_size", type="int", default=1000, required=False, multi=False, hide=False, choice=None,
                discription_ja="チャンクサイズを指定します。",
                discription_en="Specifies the chunk size."),
            dict(opt="chunk_overlap", type="int", default=50, required=False, multi=False, hide=False, choice=None,
                discription_ja="チャンクのオーバーラップサイズを指定します。",
                discription_en="Specifies the overlap size of the chunk."),
            dict(opt="chunk_separator", type="str", default=None, required=False, multi=True, hide=False, choice=None,
                discription_ja="チャンク化するための区切り文字を指定します。",
                discription_en="Specifies the delimiter character for chunking."),
        ]
        return opt

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
            # 埋め込みモデル準備
            embeddings = self.create_embeddings(args)

            # チャンク化オブジェクト準備
            if args.chunk_size is None: raise ValueError("chunk_size is required.")
            if args.chunk_overlap is None: raise ValueError("chunk_overlap is required.")
            chunk_separator = None if args.chunk_separator is None or len(args.chunk_separator)<=0 else args.chunk_separator
            md_splitter = MarkdownTextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
            txt_splitter = RecursiveCharacterTextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap, separators=chunk_separator)
            pg = pgvector.Pgvector(logger, args.dbhost, args.dbport, args.dbname, args.dbuser, args.dbpass, args.dbtimeout)

            # ベクトルストア作成
            vector_store = self.create_vectorstore(args, embeddings)
            ids = []
            # ドキュメント読込み
            if args.loadprov == 'local':
                if args.loadpath is None: raise ValueError("loadpath is required.")
                if args.loadgrep is None: raise ValueError("loadgrep is required.")
                loadpath = Path(args.loadpath)
                if not loadpath.exists(): raise ValueError("loadpath is not found.")
                if args.savetype == 'per_service':
                    sv_delids = pg.select_docids(args.servicename, None)
                docs = None
                for file in loadpath.glob(args.loadgrep):
                    if not file.is_file():
                        continue
                    try:
                        if args.savetype == 'per_doc':
                            doc_delids = pg.select_docids(args.servicename, file)
                        if file.suffix == '.pdf': docs = self.load_pdf(file, args, txt_splitter, md_splitter)
                        elif file.suffix == '.docx': docs = self.load_docx(file, args, txt_splitter)
                        elif file.suffix == '.csv': docs = self.load_csv(file, args, txt_splitter)
                        elif file.suffix == '.txt': docs = self.load_txt(file, args, txt_splitter)
                        elif file.suffix == '.md': docs = self.load_md(file, args, md_splitter)
                        elif file.suffix == '.json': docs = self.load_json(file, args, txt_splitter)
                        else: raise ValueError(f"Unsupport file extension.")
                        # ドキュメント登録（100件ずつ）
                        for i in range(0, len(docs), 100):
                            ids += vector_store.add_documents(docs[i:i+100])
                        # 古いドキュメント削除
                        if args.savetype == 'per_doc':
                            vector_store.delete(ids=doc_delids, collection_only=True)
                        if logger.level == logging.DEBUG:
                            logger.debug(f"embedding success. file={file}")
                    except Exception as e:
                        logger.warning(f"embedding warning: {str(e)} file={file}", exc_info=True)
                if docs is None:
                    raise ValueError(f"No documents found. loadpath={loadpath.absolute()}, loadgrep={args.loadgrep}")
                # サービス単位で古いドキュメント削除
                if args.savetype == 'per_service':
                    vector_store.delete(ids=sv_delids, collection_only=True)
            else:
                raise ValueError("loadprov is invalid.")

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
        docs = []
        doc_tables = []
        with pdfplumber.open(file) as pdf:
            #tset = TableSettings.resolve(table_settings)
            for page in pdf.pages:
                text = page.extract_text()
                texts = splitter.split_text(text)
                docs += [Document(t, metadata=dict(source=str(file), page=page.page_number)) for t in texts]

                if "pdf_chunk_table" in args and args.pdf_chunk_table != "none":
                    tables = page.extract_tables()
                    with_header = True if "pdf_chunk_table" in args and args.pdf_chunk_table == "row_with_header" else False
                    if tables is not None and len(tables) > 0:
                        header_md = ""
                        table_md = ""
                        for table in tables:
                            for i, row in enumerate(table):
                                if row is None or type(row) is not list:
                                    continue
                                row = [('' if r is None else r.replace('\n', ' ')) for r in row] # セル内の改行をスペースに変換
                                row_md = f'|{"|".join(row)}|\n'
                                if with_header:
                                    if i == 0:
                                        header_md = row_md
                                        continue
                                    if i >= 1:
                                        table_chunk = md_splitter.split_text(header_md+row_md)
                                        doc_tables += [Document(t, metadata=dict(source=str(file), page=page.page_number, table=True)) for t in table_chunk]
                                    continue
                                table_md += row_md
                        table_chunk = md_splitter.split_text(table_md)
                        doc_tables += [Document(header_md+t, metadata=dict(source=str(file), page=page.page_number, table=True)) for t in table_chunk]
        return docs + doc_tables
