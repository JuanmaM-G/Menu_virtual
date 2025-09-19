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

@app.route('/segundo')
def segundo():
    return render_template ('segundo.html')

@app.route('/tercero')
def tercero():
    return render_template ('tercero.html')
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)