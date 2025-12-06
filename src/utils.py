import PyPDF2       #type:ignore
import json                    

def read_pdf_file(path):
    with open(path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    return text

def read_txt_file(path):
    with open(path , 'r') as f:
        return f.read()


def extract_final_answer(response: str) -> tuple[str, str]:
    
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]   
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  
    
    cleaned = cleaned.strip()
    
    
    try:
        data = json.loads(cleaned)
        final_answer = data.get("response", "").strip()
        thinking = data.get("thinking", "").strip()
        return final_answer, thinking,True
    except json.JSONDecodeError:
       
        return response.strip(), "",False



