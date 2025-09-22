from flask import Flask, render_template
from flask_session import Session

app = Flask(__name__)

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/navbar')
def navbar():
    return render_template ('navbar.html')

@app.route('/footer')
def footer():
    return render_template ('footer.html')

@app.route('/primer')
def primer():
    return render_template ('primer.html')
# -------------------------------------------------------------------------------
                # ==== COLOMETRIA ====
# -------------------------------------------------------------------------------
@app.route('/primerC')
def primerC():
    return render_template ('primerC.html') 

@app.route('/primerCC')
def primerCC():
    return render_template ('primerCC.html') 

@app.route('/primerCCC')
def primerCCC():
    return render_template ('primerCCC.html') 

# -------------------------------------------------------------------------------

@app.route('/segundo')
def segundo():
    return render_template ('segundo.html')

# -------------------------------------------------------------------------------
                # ==== COLOMETRIA ====
# -------------------------------------------------------------------------------

@app.route('/segundoC')
def segundoC():
    return render_template ('segundoC.html')

@app.route('/segundoCC')
def segundoCC():
    return render_template ('segundoCC.html')

@app.route('/segundoCCC')
def segundoCCC():
    return render_template ('segundoCCC.html')

# -------------------------------------------------------------------------------
@app.route('/tercero')
def tercero():
    return render_template ('tercero.html')

# -------------------------------------------------------------------------------
                # ==== COLOMETRIA ====
# -------------------------------------------------------------------------------
@app.route('/terceroC')
def terceroC(): 
    return render_template ('terceroC.html')

@app.route('/terceroCC')
def terceroCC():
    return render_template ('terceroCC.html')

@app.route('/terceroCCC')
def terceroCCC():
    return render_template ('terceroCCC.html')


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)