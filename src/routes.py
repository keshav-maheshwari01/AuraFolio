from flask import Blueprint , jsonify , render_template, request , send_file    #blueprint -- helps in organizing routes 
from src.resume.reader import ResumeReader 
from src.ai.gemini_client import GeminiClient 
from src.generator.portfolio_generator import PortFolioGenerator
import os 
import uuid    #unique id               # for downloading only when user clicks download otherwise for preview it in RAM

import io      #help in memory          # for downloading only when user clicks download otherwise for preview it in RAM


main_bp = Blueprint("main",__name__)    #blueprint is helping in dividing different routes and still connected 



PORTFOLIO_CACHE = {}




def process_resume_and_cache(resume_text:str,template_name:str = "modern")->str:
    #ai parsing, template rendering, and ram caching
    ai_client = GeminiClient()
    structured_data = ai_client.parse_resume_to_json(resume_text)

    token = str(uuid.uuid4())

    html_content =PortFolioGenerator.render_portfolio(
        structured_data,
        template_name=template_name,
        download_token = token
    )

    PORTFOLIO_CACHE[token] - html_content

    return html_content




@main_bp.route("/")
def home():
    return render_template("index.html")






@main_bp.route("/preview")
def preview_portfolio():

    try : 
        resume_text = ResumeReader.read_resume("data/resume.text")
        return process_resume_and_cache(resume_text,template_name="modern")
    
    except Exception as e : 
        return  f"<h1 style='color: red; text-align: center; margin-top: 50px;'>❌ Error: {str(e)}</h1>", 500


    


@main_bp.route("/generate-portfolio",methods=["POST"])
def preview_custom_portfolio():
    try : 
        resume_text = ""

        uploaded_file = request.files.get("resume_file")
        if uploaded_file and uploaded_file.filename!="":
            resume_text = ResumeReader.read_resume_stream(uploaded_file)
        else : 
            resume_text = request.form.get("resume_text","").strip()

        if not resume_text:
            return "❌ Error: Please either upload a resume file or paste your resume text.", 400


        template_name=request.form.get("template_name","modern")

        return process_resume_and_cache(resume_text,template_name="modern")
    except Exception as e :
                
        return f"<h1 style='color: red; text-align: center; margin-top: 50px;'>❌ Error: {str(e)}</h1>", 500


    

@main_bp.route("/download/<token>")
def download_portfolio(token):  
    html_content = PORTFOLIO_CACHE.get(token) 


    if not html_content:
        return "⚠️ Error: Preview session expired or not found. Please generate a new preview.", 404


    buffer = io.BytesIO(html_content.encode("utf-8"))   #creates file like object in RAM 


    return send_file(
        buffer,
        as_attachment=True,
        download_name="portfolio.html",
        mimetype="text/html"
    )


#this is for testing like we can check it with postman that this website is working correctly or not 
@main_bp.route("/generate")
def generate_json():
    try:
        resume_text = ResumeReader.read_resume("data/resume.txt")
        ai_client = GeminiClient()
        structured_data = ai_client.parse_resume_to_json(resume_text)

        return jsonify({
            "status": "success",
            "message": "AI successfully parsed resume into schema-valid JSON!",
            "data": structured_data.model_dump()
        }) 
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
    
