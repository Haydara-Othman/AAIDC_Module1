import os
from typing import List
from dotenv import load_dotenv                                  #type:ignore
from langchain_core.prompts import PromptTemplate                    #type:ignore
from langchain_core.output_parsers import StrOutputParser       #type:ignore
from vectordb import VectorDB                                   #type:ignore
from langchain_openai import ChatOpenAI                         #type:ignore
from langchain_groq import ChatGroq                             #type:ignore
from langchain_google_genai import ChatGoogleGenerativeAI       #type:ignore
from utils import read_pdf_file , read_txt_file , extract_final_answer
from prompts import My_Prompt_Template, secondary_prompt




# Load environment variables
load_dotenv()


def load_documents() -> List:
    
    results = []
    docs =[ x  for x in os.listdir("data") ]
    names=[doc[:-4] for doc in docs]
    for name,doc in zip(names,docs) :
        path = os.path.join("data" , doc)
        if doc.endswith(".txt"):
            results.append({'content':read_txt_file(path) , 'title':name})
        elif doc.endswith(".pdf"):
            results.append({'content':read_pdf_file(path) , 'title':name})
    return results


class RAGAssistant:
   

    def __init__(self):
       
        
        self.llm = self._initialize_llm()
        if not self.llm:
            raise ValueError(
                "No valid API key found. Please set one of: "
                "OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
            )

        # Initialize vector database
        self.vector_db = VectorDB()

        self.prompt_template = PromptTemplate(
            input_variables=['content', 'query'],
            template= My_Prompt_Template

        )  


        self.second_prompt_template = PromptTemplate(
            input_variables=['f_response'],
            template= secondary_prompt

        )

        
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        self.secondary_chain = self.second_prompt_template | self.llm | StrOutputParser()

        print("RAG Assistant initialized successfully")

    def _initialize_llm(self):
        """
        Initialize the LLM by checking for available API keys.
        Tries OpenAI, Groq, and Google Gemini in that order.
        """
        # Check for OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            print(f"Using OpenAI model: {model_name}")
            return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"), model=model_name, temperature=0.0
            )

        elif os.getenv("GROQ_API_KEY"):
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            print(f"Using Groq model: {model_name}")
            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"), model=model_name, temperature=0.0
            )

        elif os.getenv("GOOGLE_API_KEY"):
            model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
            print(f"Using Google Gemini model: {model_name}")
            return ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model=model_name,
                temperature=0.0,
            )

        else:
            raise ValueError(
                "No valid API key found. Please set one of: OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
            )

    def add_documents(self, documents: List) :
        self.vector_db.add_documents(documents,3500)

    def invoke(self, input: str, n_results: int = 5):
        
        
        rc = self.vector_db.search(query = input ,n_results = n_results)

        content = "\n\n".join([
            f"From {chunk['title']} : \n {chunk['content']}"
            for chunk in rc
        ])

        sources = [chunk['title'] for chunk in rc if chunk["similarity"]>0]
        is_sources = True if sources else False
        sources = list (set ( sources))
        sources = ' \n '.join(sources)
    
        llm_response = self.chain.invoke({'content': content  ,  'query' : input})
        
        # If the LLM didn't generate JSON format properly, resend the response to the llm and ask it to extract the final response.
        final_answer, thinking_process , parsed= extract_final_answer(llm_response)
        if not parsed:
            final_answer = StrOutputParser(self.secondary_chain.invoke(final_answer))
        
        return {
            'llm_final_response': final_answer,  # Only the final answer for display
            'thinking_process': thinking_process,  # The thinking process (can be empsty)
            'full_response': llm_response,  # The complete raw response
            'relevant_context': content,
            'sources': sources,
            'is_sources': is_sources
        }


def main():
    
    try:
        
        print("Initializing RAG Assistant...")
        assistant = RAGAssistant()

        # Load sample documents
        print("\nLoading documents...")
        sample_docs = load_documents()
        print(f"Loaded {len(sample_docs)} sample documents")

        assistant.add_documents(sample_docs)

        done = False
    
        while not done:
            print("")
            print("_"*50)
            print("")
            question = input("Enter a question or 'quit' to exit: ")
            print("\n")
            if question.lower() == "quit":
                done = True

            else:
                
                result = assistant.invoke(question)
                print(result['llm_final_response'])
                if result["is_sources"]:
                    sources =result["sources"]
                    print(f"\n Sources : {sources}")
                print("\n")
                print(f"Thinking process for testing: {result['thinking_process']}")

    except Exception as e:
        print(f"Error running RAG assistant: {e}")
        print("Make sure you have set up your .env file with at least one API key:")
        print("- OPENAI_API_KEY (OpenAI GPT models)")
        print("- GROQ_API_KEY (Groq Llama models)")
        print("- GOOGLE_API_KEY (Google Gemini models)")


if __name__ == "__main__":
    main()
