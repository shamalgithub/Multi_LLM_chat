from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
    SentenceSplitter,
)
from utils import modify_file_name


#load the embedding model 
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

#load data base instance 
db = chromadb.PersistentClient(path="./chroma_db")

def load_doc_to_vectordb(path_to_doc , db_instance=db)->str:
    
    documents = SimpleDirectoryReader(
    input_files=[path_to_doc]
    ).load_data()

    file_name = documents[0].metadata['file_name']
    file_name = modify_file_name(original_name=file_name)
    # Using semantic splitter did not produce good results. continous chunking works better for continuous docs 
    # splitter = SemanticSplitterNodeParser(
    #     buffer_size=1, breakpoint_percentile_threshold=75, embed_model=embed_model
    # )

    base_splitter = SentenceSplitter(chunk_size=1000)
    base_nodes = base_splitter.get_nodes_from_documents(documents)
    collection_name = f"{file_name}_collection"
    chroma_collection = db_instance.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(base_nodes , storage_context=storage_context , embed_model = embed_model )

    
    return collection_name

def query_vectordb(collection_name , query, top_k=2 , db=db):
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model = embed_model
    )
    reteriver = index.as_retriever(similarity_top_k =top_k)
    retrived_nodes = reteriver.retrieve(query)

    retrived_context = [retrived_nodes[i].text for i in range(len(retrived_nodes))]

    return retrived_context


def get_collections():
    collections = db.list_collections()
    collection_list = [i.name for i in collections]
    return collection_list



def query_all_collections(query , top_k=1 , db=db):
    collection_list = get_collections()
    retrived_contexts =[]
    for i in collection_list:
        context = query_vectordb(collection_name=i , query=query , top_k=top_k , db=db)
        retrived_contexts.append({"doc":i , "context":context})
    return retrived_contexts

def delete_collection(collection_name , db=db):
    db.delete_collection(name=collection_name)

######### TEST CODE ##############
# collection_name = load_doc_to_vectordb(path_to_doc="/home/shamal/Downloads//HR Manual - Internal Purpose  1.pdf" , db_instance=db)
# query = "what are the processes around the commencement of employment ?"
# collection_name = "HR_Manual_-_Internal_Purpose__1pdf_collection"
# print(collection_name)
# delete_collection(collection_name="Research_Guidance_Document___Initial_Dra_collection")
# context = query_vectordb(collection_name=collection_name , query=query , top_k=3)
# context = query_all_collections(query=query)
# print(context)
# print(context)

######### END TEST CODE #########

