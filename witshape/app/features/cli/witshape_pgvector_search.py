from cmdbox.app import common
from langchain_core.documents import Document
from typing import Dict, Any, Tuple, Union, List
from witshape.app.features.cli import pgvector_base
import argparse
import logging


class PgvectorSearch(pgvector_base.PgvectorBase):
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
        return 'search'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt["discription_ja"] = "クエリーの特徴値を使用してデータベースを検索します。"
        opt["discription_en"] = "Search the database using the embedded values of the query."
        opt["choice"] += [
            dict(opt="query", type="str", default=None, required=True, multi=False, hide=False, choice=None,
                discription_ja="検索クエリーを指定します。",
                discription_en="Specifies a search query."),
            dict(opt="kcount", type="int", default=5, required=True, multi=False, hide=False, choice=None,
                discription_ja="検索結果件数を指定します。フィルタ条件を指定するとここで指定した件数の中からフィルタします。",
                discription_en="Specify the number of search results. If filter conditions are specified, the results will be filtered from the number of results specified here."),
            dict(opt="filter_source", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="フィルタ条件のソース名を指定します。ファイルパスなどに対して中間マッチします。",
                discription_en="Specifies the source name of the filter condition. Intermediate match for file paths, etc."),
            dict(opt="filter_spage", type="int", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="フィルタ条件の開始ページを指定します。",
                discription_en="Specifies the starting page of the filter condition."),
            dict(opt="filter_epage", type="int", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="フィルタ条件の終了ページを指定します。",
                discription_en="Specifies the end page of the filter condition."),
            dict(opt="filter_table", type="bool", default=False, required=False, multi=False, hide=False, choice=[True, False],
                discription_ja="フィルタ条件のテーブルを指定します。Trueを指定するとテーブル要素を対象にします。",
                discription_en="Specifies the table of filter conditions; if True, table elements are targeted."),
            dict(opt="filter_score", type="float", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="フィルタ条件の0~1のスコア閾値を指定します。0に近いほど類似しています。",
                discription_en="Specifies the 0~1 score threshold for the filter condition; the closer to 0, the more similar it is."),
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
            if args.query is None: raise ValueError("query is required.")
            if args.kcount is None: raise ValueError("kcount is required.")

            # 埋め込みモデル準備
            embeddings = self.create_embeddings(args)
            # ベクトルストア作成
            vector_store = self.create_vectorstore(args, embeddings)
            # 検索
            docs:List[Tuple[Document, float]] = vector_store.similarity_search_with_score(args.query, k=args.kcount)
            res = []
            for doc, score in docs:
                if args.filter_score is not None and args.filter_score < score: continue
                if args.filter_source is not None and args.filter_source not in doc.metadata['source']: continue
                if args.filter_spage is not None and args.filter_spage > doc.metadata['page']: continue
                if args.filter_epage is not None and args.filter_epage < doc.metadata['page']: continue
                table = doc.metadata['table'] if 'table' in doc.metadata else False
                if args.filter_table and not table: continue
                res.append(dict(id=doc.id, type=doc.type, score=score, content=doc.page_content,
                                source=doc.metadata['source'], page=doc.metadata['page'], table=table))
            ret = dict(success=dict(docs=res))
            logger.info(f"embedding success. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                        f"servicename={args.servicename}, size={len(docs)}")
        except Exception as e:
            logger.error(f"embedding error: {str(e)}. dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                         f"servicename={args.servicename}")
            ret = dict(error=f"embedding error: {str(e)} dbhost={args.dbhost}, dbport={args.dbport}, dbname={args.dbname}, dbuser={args.dbuser}, " + \
                             f"servicename={args.servicename}")
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return 1, ret, None
        return 0, ret, None

