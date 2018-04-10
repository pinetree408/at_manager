from flask import Flask
from flask import render_template
import parser

app = Flask(__name__)

@app.route('/')
def index():
    #json_dump = parser.get_focusable_tree(parser.get_tree())
    json_dump = parser.get_tree()
    return render_template('index.html', json_dump=json_dump)

if __name__ == '__main__':
    app.run()
