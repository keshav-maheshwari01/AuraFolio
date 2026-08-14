
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





   
class ATSScoreSchema(BaseModel):
    ats_score : int = Field(description="Compatibility score from 0 to 100 based on keyword match, skills, and experience alignment.")
    matched_keywords : list[str] = Field(description="Keywords, technologies, and skills found in both the resume and job description.")
    missing_keywords:list[str] = Field(description="Important keywords or tools from the job description that are missing from the resume." )
    recommendations : list[str] = Field(description="Actionable, specific tips to optimize the resume for this job description.")


class CoverLetterSchema(BaseModel):
    subject_line : str = Field(description = "A compelling, professional email subject line for the job application.")
    salutation : str = Field(description ="Professional greeting, e.g., 'Dear Hiring Manager,' or 'Dear [Hiring Team],'." )
    body_paragraphs: list[str] = Field(description="3 to 4 well-structured paragraphs connecting the candidate's resume experience directly to the job description requirements.")
    sign_off: str = Field(description="Professional closing statement and sign-off, e.g., 'Sincerely, [Candidate Name]'.")


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


                
    def analyze_ats_score(self,resume_text : str , job_description : str , max_retries :int = 3 ) -> ATSScoreSchema:
        prompt = f"""
        You are an advanced Applicant Tracking System (ATS) and professional recruiter bot.
        Compare the following Resume against the Target Job Description. 
        Calculate an honest ATS compatibility score from 0 to 100.
        Identify matched keywords, missing keywords, and provide clear recommendations.
        Return ONLY valid JSON matching the requested schema.

        RESUME TEXT:
        ----------------
        {resume_text}
        ----------------

        TARGET JOB DESCRIPTION:
        ----------------
        {job_description}
        ----------------
        """



        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔄 Running ATS analysis (Attempt {attempt}/{max_retries})...")
                response = self.model.generate_content(prompt,generation_config={"response_mime_type":"application/json","response_schema":ATSScoreSchema})
                validated_data = ATSScoreSchema.model_validate_json(response.text)
                
                logger.info("✅ ATS Analysis complete and validated.")
                return validated_data

            except ValidationError as ve:
                logger.warning(f"⚠️ ATS validation warning on attempt {attempt}: {ve}")
                if attempt == max_retries:
                    raise RuntimeError(f"ATS Analysis failed validation after {max_retries} attempts: {ve}")
                
                prompt = f"""
                Your previous ATS JSON output failed validation. Please fix the error.
                RESUME: {resume_text}
                JOB DESCRIPTION: {job_description}
                PREVIOUS JSON: {response.text}
                ERROR: {ve}
                Return ONLY valid JSON matching ATSScoreSchema.
                """
            except Exception as e:
                logger.error(f"❌ ATS API Error: {e}")
                if attempt == max_retries:
                    raise RuntimeError(f"ATS API failure: {str(e)}")


def generate_cover_letter(self , resume_text:str , job_description : str , max_retries : int = 3 )-> CoverLetterSchema :


    prompt = f"""
        You are an expert executive career coach and professional writer.
        Write a compelling, tailored cover letter for a job application by synthesizing 
        the candidate's Resume with the Target Job Description. 
        Highlight specific matching skills and achievements. Avoid generic fluff.
        Return ONLY valid JSON matching the requested CoverLetterSchema.

        RESUME TEXT:
        ----------------
        {resume_text}
        ----------------

        TARGET JOB DESCRIPTION:
        ----------------
        {job_description}
        ----------------
        """
    for attempt in range(1,max_retries+1):
        try : 
            logger.info(f"🔄 Generating cover letter (Attempt {attempt}/{max_retries})...")

            response = self.model.generate_content(prompt,generation_config = {
                "response_mime_type" :"application/json" , "response_schema":CoverLetterSchema
            })
            validated_data = CoverLetterSchema.model_validate_json(response.text)
            logger.info("✅ Cover letter successfully generated and validated.")
            return validated_data



        except ValidationError as ve:
                logger.warning(f"⚠️ Cover letter validation warning on attempt {attempt}: {ve}")
                if attempt == max_retries:
                    raise RuntimeError(f"Cover letter failed validation after {max_retries} attempts: {ve}")
                
                prompt = f"""
                Your previous cover letter JSON failed validation. Please fix the error.
                RESUME: {resume_text}
                JOB DESCRIPTION: {job_description}
                PREVIOUS JSON: {response.text}
                ERROR: {ve}
                Return ONLY valid JSON matching CoverLetterSchema.
                """
        except Exception as e:
            logger.error(f"❌ Cover letter API Error: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"Cover letter API failure: {str(e)}")





    


 