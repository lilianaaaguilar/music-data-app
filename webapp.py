from flask import Flask

import json

app = Flask(__name__)

@app.route('/')
def render_about():
    return render_template('about.html')
    
@app.route('/databygenre')
def render_databygenre():
