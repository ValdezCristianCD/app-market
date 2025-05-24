from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('pages/landing.html')

if __name__ == '__main__':
    app.run(debug=True)
