"""app.py"""
from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Serve webpage icon.
    """
    return redirect(url_for('static',
                            filename='favicon48x48.ico',
                            mimetype='image/vnd.microsoft.icon'
                            )
                    )


@app.route('/', methods=['GET'])
def base_url():
    """Redirect bare url to home page."""
    return redirect(url_for('home'), code=303)


@app.route('/home/', methods=['GET'])
def home():
    """Home page."""
    return render_template('home.html')


@app.route('/projects/', methods=['GET'])
def projects():
    """Projects page."""
    return render_template('projects.html', methods=['GET'])


@app.route('/blog/', methods=['GET'])
def blog():
    """Blog page."""
    return render_template('blog.html')


@app.route('/contact/', methods=['GET'])
def contact():
    """Contact page."""
    return render_template('contact.html')


@app.route('/about/', methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
