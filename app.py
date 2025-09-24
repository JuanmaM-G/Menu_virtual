from flask import Flask, render_template


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


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)