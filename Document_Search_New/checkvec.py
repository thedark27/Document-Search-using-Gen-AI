#Writ a function to get all processed Pdfs:
def get_already_vec(path_of_txt):
    with open(path_of_txt,'r') as file:
        text = file.read()
        
    if len(text)==0:
        return []   
    text = text[:-1]    
    text = text.split(',')
    return text  

