from cmdbox.app import common
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
        opt["choise"] += [
            dict(opt="query", type="str", default=None, required=True, multi=False, hide=False, choise=None,
                discription_ja="検索クエリーを指定します。",
                discription_en="Specifies a search query."),
            dict(opt="kcount", type="int", default=5, required=True, multi=False, hide=False, choise=None,
                discription_ja="検索結果件数を指定します。",
                discription_en="Specify the number of search results."),
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
            docs = vector_store.similarity_search(args.query, k=args.kcount)
            ret = dict(success=dict(docs=[dict(id=doc.id, type=doc.type, content=doc.page_content) for doc in docs]))
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

