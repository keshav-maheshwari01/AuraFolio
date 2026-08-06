import os 
from dotenv import load_dotenv


load_dotenv()    #load env variables

class Config : 
    GEMINI_API_KEY :str = os.getenv("GEMINI_API_KEY","")
    MODEL_NAME : str = os.getenv("GEMINI_MODEL","gemini-1.5-flash")

    @classmethod 

    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing. Please add it to your .env file"
            )
  