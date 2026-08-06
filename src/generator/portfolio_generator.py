from flask import render_template 

class PortFolioGenerator : 
    @staticmethod 
    def render_moder_portfolio(structured_data)->str : 
        try : 
            return render_template("modern.html",date = structured_data)
        except Exception as e  : 
            raise RuntimeError(f"Template rendering error : {e}")

        