from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():

    app_config = {
        'app_name' : 'App Market'
    }

    links = {
        'LANDING' : '/landing',
        'TEST' : '/test'
    }

    page_vars = {
        **app_config,
        'nav_links' : links,
        'app_section' : 'Landing' 
    }

    return render_template('pages/landing.html',**page_vars)

if __name__ == '__main__':
    app.run(debug=True)
