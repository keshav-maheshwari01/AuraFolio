
import google.generativeai as genai
from pydantic import BaseModel , Field

from src.config import Config

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

    def parse_resume_to_json(self,resume_text:str)-> ResumeSchema:
        prompt = f"""
        Analyze the following raw resume text and extract the professional details 
        according to the required schema. Do not invent or hallucinate any information.
        If a section is missing, provide an empty list or appropriate default.

        RESUME TEXT:
        ----------------
        {resume_text}
        ----------------
        """
        try : 
            response = self.model.generate_content(prompt)

            structured_data = ResumeSchema.model_validate_json(response.text)
            return structured_data 
        except Exception as e : 
            raise RuntimeError(f" Gemini API Error during resume parsing: {str(e)}")    