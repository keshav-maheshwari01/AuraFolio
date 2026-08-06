from flask import Blueprint , jsonify , render_template_string     #blueprint -- helps in organizing routes 
from src.resume.reader import ResumeReader 
from src.ai.gemini_client import GeminiClient 
from src.generator.portfolio_generator import PortFolioGenerator

main_bp = Blueprint("main",__name__)    #blueprint is helping in dividing different routes and still connected 

@main_bp.route("/")
def home():
    return"""
 <html>
        <head><title>AuraFolio Studio</title></head>
        <body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h1>✨ Welcome to AuraFolio AI Resume & Portfolio Studio</h1>
            <p>Your modular AI engineering studio is running successfully!</p>
            <br>
            <div style="display: flex; justify-content: center; gap: 15px;">
                <a href="/generate" style="background: #000; color: #fff; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">View Raw JSON</a>
                <a href="/preview" style="background: #2563eb; color: #fff; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">Preview HTML Portfolio</a>
            </div>
        </body>
    </html>
"""

@main_bp.route("/generate")
def generate_portfolio():

    try :
        resume_text = ResumeReader.read_resume("data/resume.txt")
        ai_client = GeminiClient()
        structured_data = ai_client.parse_resume_to_json(resume_text)

        return jsonify({
            "status": "success",
            "message": "AI successfully parsed the resume!",
            "data": structured_data.model_dump()
        }) 
    except Exception as e :
        return jsonify({"status": "error",
            "message": str(e)
        }),500



@main_bp.route("/preview")
def preview_portfolio():
    try : 
        resume_text = ResumeReader.read_resume("data/resume.txt")
        ai_client = GeminiClient()
        structured_data =  ai_client.parse_resume_to_json(resume_text)

        return PortFolioGenerator.render_moder_portfolio(structured_data)

    except Exception as e : 
        return  f"<h1 style='color: red; text-align: center; margin-top: 50px;'>❌ Error: {str(e)}</h1>", 500"