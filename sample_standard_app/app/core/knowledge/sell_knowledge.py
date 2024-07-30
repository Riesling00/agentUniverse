# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import DashscopeEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from langchain.text_splitter import TokenTextSplitter
from pathlib import Path

SPLITTER = TokenTextSplitter(chunk_size=600, chunk_overlap=100)


class SellKnowledge(Knowledge):
    """The demo knowledge."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = ChromaStore(
            collection_name="law_store",
            persist_path="../../DB/sell.db",
            embedding_model=DashscopeEmbedding(
                embedding_model_name='text-embedding-v2'
            ),
            dimensions=1536)
        self.reader = PdfReader()
        print('Here is the sell knowledge.')
        # Initialize the knowledge
        # self.insert_knowledge()

    def insert_knowledge(self, **kwargs) -> None:
        """
        Load civil law pdf and save into vector database.
        """
        for id in range(1,6):
            file_name = "../resources/sell/content_"+str(id)+".pdf"
            print('Insert knowledge from the pdf file '+file_name)
            civil_law_docs = self.reader.load_data(Path(file_name))
            lc_doc_list = SPLITTER.split_documents(Document.as_langchain_list(
            civil_law_docs
        ))
            self.store.insert_documents(Document.from_langchain_list(lc_doc_list))
