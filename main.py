import json
from  src.resume.reader import ResumeReader
from src.ai.gemini_client import GeminiClient

def main() : 
    print("Starting Aurofolio")

    try : 
        resume_text = ResumeReader.read_resume("data/resume.txt")
        print("Reading resume -- successfull")

        ai_client = GeminiClient()
        print("connected successfully")

        structured_resume = ai_client.parse_resume_to_json(resume_text)
        print("AI Extraction Completed\n")


        print("*"*100)
        print(structured_resume.model_dump_json(indent=2))
        print("*"*100)

    except Exception as e :
        print(f"An error occured during execution:{e} ")

if __name__=="__main__":
    main()


