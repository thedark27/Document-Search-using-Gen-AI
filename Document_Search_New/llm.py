import langchain
langchain.verbose = False
import glob
import pandas as pd
from langchain.chains.question_answering import load_qa_chain
import fitz
import os
from langchain.chat_models import ChatOpenAI
from fuzzywuzzy import fuzz
from langchain import PromptTemplate
import glob
import os




os.environ["OPENAI_API_KEY"] ="Your openai Key" 

       

#Function to Highlight the pdf according to similar Content:
def highlight_pdf( pdf_path,page_num,page_con,threshold=70):
    doc = fitz.open("static/PDFS/"+pdf_path)
    found = False
    j=0
    for k in page_num: 
        page=doc[k]
        words = page.get_text_words()
        highlighted_chunks = []
        current_chunk = []
        search_text=page_con[j]
        j=j+1
        for i, word in enumerate(words):
            word_text = word[4]
            similarity = fuzz.token_set_ratio(search_text, word_text)
            if similarity >= threshold:
                current_chunk.append(word)
            else:
                if current_chunk:
                    highlighted_chunks.append(current_chunk)
                    current_chunk = []

        if current_chunk:
            highlighted_chunks.append(current_chunk)

        for chunk in highlighted_chunks:
            if len(chunk) > 10:
                found = True
                rects = [fitz.Rect(word[:4]) for word in chunk]
                page.add_highlight_annot(rects)

    # Save the updated PDF to a temporary file
    print(f"value of found: {found}")
    if found:
        doc.save("static/High/"+pdf_path)
        doc.close()
    else:
        doc.close()
        return None



#Function to call llm for summary output:
def new_chain(vectorstore,search):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    question_prompt_template = """
                    Answer the question as precise as possible using the provided context. \n\n
                    Context: \n {context} \n
                    Question: \n {question} \n
                    Answer:
                    """
    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["context", "question"]
    )

    # summaries is required. a bit confusing.
    combine_prompt_template = """Given the extracted content and the question, create a final answer.
    If the answer is not contained in the context, say "answer not available in context. \n\n
    Summaries: \n {summaries}?\n
    Question: \n {question} \n
    Answer:
    """
    combine_prompt = PromptTemplate(
        template=combine_prompt_template, input_variables=["summaries", "question"]
    )
    
    map_reduce_chain = load_qa_chain(
    llm,
    chain_type="map_reduce",
    return_intermediate_steps=True,
    question_prompt=question_prompt,
    combine_prompt=combine_prompt,)
    
    
    new_db = vectorstore.as_retriever()

    docs = new_db.get_relevant_documents(search)

    map_reduce_embeddings_outputs = map_reduce_chain(
        {"input_documents": docs, "question": search}
    )

    answer=map_reduce_embeddings_outputs["output_text"]
    
    if "answer not available in context" in answer:
        answer=""
        

    
    dic = {}
    for i in docs:
        if i.metadata['source'] in dic:
            dic[i.metadata['source']].append([i.metadata['page'],i.page_content])
        else:
            dic[i.metadata['source']] = [[i.metadata['page'],i.page_content]]
    
    pdf_name=[]
    page_numb={}
    for i in dic:
        name = i.split('\\')[-1]
        page_num=[]
        page_con=[]    
        for j in dic[i]:
            page_num.append(j[0])
            page_con.append(j[1])
            
        highlight_pdf(name,page_num,page_con) 
        for k in range(len(page_num)):
            page_num[k] = int(page_num[k])+1
        pdf_name.append("High/"+name)
        page_numb["High/"+name]=page_num
        

    return answer,pdf_name,pdf_name,page_numb
        
        
            

