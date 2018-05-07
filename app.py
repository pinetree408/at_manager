from flask import Flask
from flask import render_template, request
import parser

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def index():
    f_name = 'naver.AT'
    at_type = 'all'
    if request.method == 'POST':
        f_name = str(request.form['site'])
        at_type = str(request.form['type'])

    tree = parser.get_tree(f_name)
    if at_type == 'focusable_with_child':
        tree = parser.get_focusable_tree_with_child(tree)
    elif at_type == 'focusable_without_child':
        tree = parser.get_focusable_tree_without_child(tree)
    
    return render_template('index.html', f_name=f_name, at_type=at_type, json_dump=tree)

if __name__ == '__main__':
    app.run()
