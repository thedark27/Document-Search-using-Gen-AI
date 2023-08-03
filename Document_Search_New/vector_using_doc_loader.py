from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
import glob
import os
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from checkvec import get_already_vec



os.environ["OPENAI_API_KEY"] = "Your Openai Key"



#Function to extract all the pdf inside the Folder:
def extract_pdf_files(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, "**/*.pdf"), recursive=True)
    return pdf_files


#Function to load the embedding 
def load_vec():
    embeddings = OpenAIEmbeddings()
    vec = FAISS.load_local("vec", embeddings)
    return vec


#Function to convert the pdfs to embeddings and save local:
def create(pdfs):
    vec_list=get_already_vec('trac.txt')  #list of all already processed pdf
    
    if len(vec_list) == 0:
        name = pdfs[0].split('\\')[-1]
        print(name)
        with open(pdfs[0], 'rb') as source_file:
            with open('static/vec_junction/'+name, 'wb+') as destination_file:
                destination_file.write(source_file.read())
        loader = DirectoryLoader('static/vec_junction',
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=2000,
                                                   chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()  #Here using OpenAI embedding
        vectorstore = FAISS.from_documents(texts, embeddings) #Using FAISS for Vectorstore
        vectorstore.save_local('vec')
        with open('trac.txt', 'a') as file:
            file.write(name+",")
            
        processed_folder = 'static/vec_junction'
        for filename in os.listdir(processed_folder):
            if filename.endswith('.pdf'):
                os.remove(os.path.join(processed_folder, filename))
    
    vectorstore = load_vec()        
    for pdf in pdfs:
        vec_list = get_already_vec('trac.txt')
        name = pdf.split('\\')[-1]
        if name not in vec_list:
            print(name)
            with open(pdf, 'rb') as source_file:
                with open('static/vec_junction/'+name, 'wb+') as destination_file:
                    destination_file.write(source_file.read())
            
            loader = DirectoryLoader('static/vec_junction',
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=2000,
                                                   chunk_overlap=200)
            
            texts = text_splitter.split_documents(documents)
            embeddings = OpenAIEmbeddings()  #Here using OpenAI embedding
            vec = FAISS.from_documents(texts, embeddings) #Using FAISS for Vectorstore
            vectorstore.merge_from(vec)
            with open('trac.txt', 'a') as file:
                file.write(name+",")
            processed_folder = 'static/vec_junction'
            for filename in os.listdir(processed_folder):
                if filename.endswith('.pdf'):
                    os.remove(os.path.join(processed_folder, filename))
    
    vectorstore.save_local('vec')                
  
     
    

        




    
