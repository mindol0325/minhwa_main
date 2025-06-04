import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(120), nullable=True)

def save_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return filename
    return None

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    query = request.args.get('q', '')
    if query:
        items = PortfolioItem.query.filter(PortfolioItem.title.contains(query)).all()
    else:
        items = PortfolioItem.query.all()
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        image_file = request.files.get('image')
        image_name = save_image(image_file)
        item = PortfolioItem(title=title, description=description, image=image_name)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_edit.html', item=None)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    item = PortfolioItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title = request.form['title']
        item.description = request.form.get('description')
        image_file = request.files.get('image')
        image_name = save_image(image_file)
        if image_name:
            item.image = image_name
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_edit.html', item=item)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    item = PortfolioItem.query.get_or_404(item_id)
    if item.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
        except OSError:
            pass
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
