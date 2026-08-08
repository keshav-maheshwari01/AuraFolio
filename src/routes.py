from flask import Blueprint , jsonify , render_template, request , send_file    #blueprint -- helps in organizing routes 
from src.resume.reader import ResumeReader 
from src.ai.gemini_client import GeminiClient 
from src.generator.portfolio_generator import PortFolioGenerator
import os 
import uuid    #unique id               # for downloading only when user clicks download otherwise for preview it in RAM

import io      #help in memory          # for downloading only when user clicks download otherwise for preview it in RAM


main_bp = Blueprint("main",__name__)    #blueprint is helping in dividing different routes and still connected 



PORTFOLIO_CACHE = {}


@main_bp.route("/")
def home():
    return render_template("index.html")


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

        html_content = PortFolioGenerator.render_modern_portfolio(structured_data)

        token = str(uuid.uuid4())
        PORTFOLIO_CACHE[token] = html_content 

        return render_template("modern.html", data=structured_data, download_token=token)
  
    except Exception as e : 
        return  f"<h1 style='color: red; text-align: center; margin-top: 50px;'>❌ Error: {str(e)}</h1>", 500


    


@main_bp.route("/preview-custom",methods=["POST"])
def preview_custom_portfolio():
    try : 
        resume_text = request.form.get("resume_text","").strip()
        if not resume_text:
            return "❌ Error: Resume text cannot be empty.", 400

        ai_client = GeminiClient()
        structured_data = ai_client.parse_resume_to_json(resume_text)

        return PortFolioGenerator.render_moder_portfolio(structured_data)
    except Exception as e:
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

    
    
    
