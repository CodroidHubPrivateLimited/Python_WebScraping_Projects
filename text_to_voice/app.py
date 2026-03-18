from flask import Flask, render_template_string

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/history.html')
def history():
    try:
        with open('templates/history.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "History page not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
