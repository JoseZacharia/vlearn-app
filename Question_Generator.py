


from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os


embedding = ''
docsearch=''
chain=''
shfile = None


def generate_questions(cursor, module_id, raw_text):
    
    os.environ["OPENAI_API_KEY"] = "*************************"

    # We need to split the text that we read into smaller chunks so that during information retreival we don't hit the token size limits.
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
    )
    texts = text_splitter.split_text(raw_text)
    initialise(texts)

    qa=[]
    cursor.execute('select "TID", "Topic Name" from  "Topic" where "Module ID" = %s', (module_id,))
    for i in cursor.fetchall():
        topic=i[1]
        query = f'give questions regarding "{topic}" separated by semicolon'
        result=run_query(query)
        print(result)
        generated_questions=result.split(';')
        print(generated_questions)

        for q in generated_questions:
            answer=run_query(q)
            print("Question: ", q)
            print("Answer: ", answer)
            # if answer != " I don't know.":
            if "I don't know" not in answer:
                qa.append((i[0], q, answer))

    return qa


def initialise(texts):
    global embeddings, docsearch, chain
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    chain = load_qa_chain(OpenAI(), chain_type="stuff")


def run_query(query):
    docs = docsearch.similarity_search(query)
    result = chain.run(input_documents=docs, question=query)
    return result
