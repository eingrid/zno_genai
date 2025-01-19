import os
from langchain_core.documents import Document
from uuid import uuid4
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import textwrap
import json
import dspy

def read_content_files(directory, max_chunk_size=300):
    documents = []
    
    print(f"Reading files from {directory}...")
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            topic = os.path.splitext(filename)[0]  # Remove .txt extension
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Split content into chunks
                chunks = textwrap.wrap(content, max_chunk_size, break_long_words=False, break_on_hyphens=False)
                
                # Create a document for each chunk
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk,
                        metadata={"topic": topic}
                    )
                    documents.append(doc)
                
                print(f"Processed: {filename} - Created {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return documents

def init_vector_db(documents_lists : list[list,str], collection_name="ukrainian_language"):
    
    embeddings = HuggingFaceEmbeddings(
        model_name="jinaai/jina-embeddings-v3",
        model_kwargs={"trust_remote_code": True}
    )
    
    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )
    
    for documents_source in documents_lists:
        documents, source = documents_source
        # Generate UUIDs for each document
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        # Add documents to the vector store
        vector_store.add_documents(documents=documents, ids=uuids, metadata = {"source":source})
        print("Vector database initialized successfully!")
        
    return vector_store


def init_with_parsed():
   # Configuration
    parsed_content_dir = "parsed_content"  # Directory with the parsed text files
    history_content = "izno_content"
    max_chunk_size = 700  # Maximum size for content chunks

    # Read and process the files
    documents_urk_lang = read_content_files(parsed_content_dir, max_chunk_size)
    documents_history = read_content_files(history_content, max_chunk_size)
    documents = [(documents_history,"history"),(documents_urk_lang,"ukr_lang")]

    # Initialize vector database
    vector_store = init_vector_db(documents)

    # Test the vector store with a sample query
    print("\nTesting vector store with a sample query...")
    results = vector_store.similarity_search("Підкреслені літери позначають однаковий звук у кожному слові рядка", k=3)
    print("\nSample results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. Topic: {doc.metadata['topic']}")
        print(f"Content: {doc.page_content}...")


def init_with_train_data():

    with open('gen-ai-ucu-2024-task-3/zno.train.jsonl', 'r') as json_file:
        json_list = list(json_file)

    all_questions = []
    for json_str in json_list:
        result = json.loads(json_str)
        all_questions.append(result)

    all_examples = []
    for sample in all_questions:
        example = dspy.Example(
            question=sample['question'],
            options=sample['answers'],
            subject = sample['subject'],
            correct_answer = sample['correct_answers'][0]
        ).with_inputs("question", "options")
        all_examples.append(example)
    train_set, test_set = all_examples[int(len(all_questions)*0.2):], all_examples[:int(len(all_questions)*0.2)]
    documents = []
    for example in train_set:

        content = f"Question: {example.question}\nOptions:{example.options}\nAnswer {example.correct_answer}"
        doc = Document(
            page_content=content,
        )
        documents.append(doc)
    vector_store = init_vector_db([(documents,'k')])

    print("\nTesting vector store with a sample query...")
    results = vector_store.similarity_search("Підкреслені літери позначають однаковий звук у кожному слові рядка", k=3)
    print("\nSample results:")
    for i, doc in enumerate(results, 1):
        # print(f"\n{i}. Topic: {doc.metadata['topic']}")
        print(f"Content: {doc.page_content}...")

def main():
    print("Initing vector db, you can change method to select initilization type.")
    init_with_train_data()


  

if __name__ == "__main__":
    main()