
import google.generativeai as genai
from pydantic import BaseModel , Field

from src.config import Config
import logging ## if pydantic validation gives error user needs to try this again thats why with logging we will enhance this like user dont need to retry its automatically gets load and give the desired output

from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ExperienceItem(BaseModel):
    company: str = Field(description="Name of the company or organization.")
    role: str = Field(description="Job title or position held.")
    duration: str = Field(description="Time period, e.g., 'Jan 2022 - Present'.")
    highlights: list[str] = Field(description="Key achievements or responsibilities.")

class ProjectItem(BaseModel):
    name: str = Field(description="Name of the project.")    #Field -- description for ai 
    description: str = Field(description="Brief description of what the project does.")
    technologies: list[str] = Field(description="Tech stack used.")

class ResumeSchema(BaseModel):
    full_name: str = Field(description="Candidate's full name.")
    professional_title: str = Field(description="Current job title or target role.")
    bio: str = Field(description="A compelling 2-3 sentence professional summary.")
    skills: list[str] = Field(description="List of technical and soft skills.")
    experience: list[ExperienceItem] = Field(description="Work history.")
    projects: list[ProjectItem] = Field(description="Notable portfolio projects.")



class GeminiClient  : 
    def __init__(self) :
        genai.configure(api_key=Config.GEMINI_API_KEY) 
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            generation_config= {
                "response_mime_type":"application/json",   #returns response in the form of json 
                "response_schema":ResumeSchema,            #return respose which follows this schema 
                "temperature" : 0.1,                         #controls randomness 
            } 
        )

    def parse_resume_to_json(self,resume_text:str,max_retries : int =3 )-> ResumeSchema:
        prompt = f"""
        Analyze the following raw resume text and extract the professional details 
        according to the required schema. Do not invent or hallucinate any information.
        If a section is missing, provide an empty list or appropriate default.

        RESUME TEXT:
        ----------------
        {resume_text}
        ----------------
        """

        for attempt in range(1,max_retries+1):
            try : 
                logger.info(f"Gemini parsing attempt {attempt} of {max_retries}... ")

                response = self.model.generate_content(prompt)

                validated_data = ResumeSchema.model_validate_json(response.text)
                logger.info("Successfully validated Gemini JSON response against schema")
                return validated_data
            
            except  ValidationError as ve : 
                logger.warning(f"Validation error on attempt {attempt}: {ve}")

                if attempt == max_retries:

                    logger.error(f"❌ Max retries ({max_retries}) reached. Schema validation failed.")

                    raise RuntimeError(
                        f"Gemini failed to produce schema-valid JSON after {max_retries} attempts. "
                        f"Last validation error: {str(ve)}"
                    )

                prompt = f"""
                Your previous JSON output failed schema validation. Please correct the errors.
                
                ORIGINAL RESUME TEXT:
                {resume_text}
                
                PREVIOUS INVALID JSON OUTPUT:
                {response.text}
                
                PYDANTIC VALIDATION ERROR TO FIX:
                {str(ve)}
                
                INSTRUCTIONS FOR REVISION:
                - Fix ONLY the validation errors specified above.
                - Preserve all other valid data.
                - Do not hallucinate or invent information.
                - Return ONLY valid JSON (no markdown ticks like ```json, no explanations).
                - Ensure every required field matches the schema format exactly.
                """
            
            except Exception as e:
                # Handle unexpected network or API errors
                logger.error(f"API Exception on attempt {attempt}: {str(e)}")
                if attempt == max_retries:
                    raise RuntimeError(f"Gemini API failure after {max_retries} attempts: {str(e)}")

                

    


        