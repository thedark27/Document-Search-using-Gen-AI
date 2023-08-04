from flask import Flask,render_template,url_for,request
import os
from llm import new_chain
from vector_using_doc_loader import load_vec,create,extract_pdf_files


app = Flask(__name__)


#To take the response from llm:
@app.route('/',methods=['POST','GET'])
def index():
    if request.method == "POST":
        search = request.form["se"]
        
        if len(search)>0:      
            vectorestore = load_vec()          
            answer,pname,pdf_name,wpg= new_chain(vectorestore,search)
            answer = answer.split('\n')
            return render_template('index.html',con=[search,answer,pname,pdf_name,wpg])
    
    return render_template('index.html')




@app.route('/sel')
def selec():
    return render_template('selpdf.html')




@app.route('/end')
def end():
    return render_template('selpdf.html')



#To Overwrite the PDF:
@app.route('/yes')
def yes():
    pdfs=extract_pdf_files('static/pdf_junction')
    for pdf in pdfs:
        name=pdf.split('\\')[-1]
        with open(pdf, 'rb') as source_file:
            with open('static/PDFS/'+name, 'wb+') as destination_file:
                    destination_file.write(source_file.read())
                    
    processed_folder = 'static/pdf_junction'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pdf'):
            os.remove(os.path.join(processed_folder, filename))  
                          
    pdfs=extract_pdf_files('static/PDFS')
    create(pdfs)
    s="PDF processing completed!"        
    return render_template('selpdf.html',con=[s])        



#To process the pdf for making vectorstore    
@app.route('/process', methods=['POST'])
def process_pdfs():
    already_pdf=extract_pdf_files('static/PDFS')
    already_pdf1=[]
    for pdf in already_pdf:
        already_pdf1.append(pdf.split('\\')[-1])
        
 
    uploaded_files = request.files.getlist('pdfs')

    
    #os.makedirs(processed_folder, exist_ok=True)
    
    c=0
    for file in uploaded_files:
        if file.filename != '':
            if file.filename in already_pdf1:
                c = c+1
    
    if c>0:
        processed_folder = 'static/pdf_junction'
        for file in uploaded_files:
            if file.filename != '':
                file.save(os.path.join(processed_folder, file.filename))
        return render_template('overwrite.html')
    
    else:
        processed_folder = 'static/PDFS'
        for file in uploaded_files:
            if file.filename != '':
                file.save(os.path.join(processed_folder, file.filename))
        pdfs=extract_pdf_files('static/PDFS')
        create(pdfs)
    s="PDF processing completed!"
    return render_template('selpdf.html',con=[s])






#To Delete all the files
@app.route('/delete', methods=['GET'])
def delete_pdfs():
    processed_folder = 'static/PDFS'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pdf'):
            os.remove(os.path.join(processed_folder, filename))
            
    processed_folder = 'static/High'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pdf'):
            os.remove(os.path.join(processed_folder, filename))
            
    processed_folder = 'static/vec_junction'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pdf'):
            os.remove(os.path.join(processed_folder, filename))
            
    processed_folder = 'vec'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.faiss'):
            os.remove(os.path.join(processed_folder, filename))
    
    processed_folder = 'vec'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pkl'):
            os.remove(os.path.join(processed_folder, filename))
                  
            
    processed_folder = 'static/pdf_junction'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.pdf'):
            os.remove(os.path.join(processed_folder, filename))                
            

            
    processed_folder = 'static/table'
    for filename in os.listdir(processed_folder):
        if filename.endswith('.csv'):
            os.remove(os.path.join(processed_folder, filename))        
    
    with open('trac.txt', 'w') as file:
        pass        
    s = "All Data Related to Pdf deleted Scusefully!"        
    return render_template('selpdf.html',con=[s])



if __name__ == '__main__':
    app.run(debug=True)
   
