from flask import render_template 
import os 

class PortFolioGenerator : 
    @staticmethod 
    def render_portfolio(structured_data)->str :    #for preview 
        try : 
            return render_template("modern.html",data = structured_data)
        except Exception as e  : 
            raise RuntimeError(f"Template rendering error : {e}")

    @staticmethod 
    def save_portfolio_to_disk(Structured_data , output_path:str = "output/portfolio.html")->str:  #for downloading 
        try : 
            os.mkdir(os.path.dirname(output_path),exist_ok = True)
            html_content = render_template("modern.html",data = Structured_data)

            with open(output_path,"w",encoding="utf-8") as f : 
                f.write(html_content)
            return output_path  
        except Exception as e  : 
            raise RuntimeError(f"❌ Failed to save portfolio to disk: {str(e)}")

        