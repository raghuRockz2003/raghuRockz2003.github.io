from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import RiceBag
from .db import db
import os
import pandas as pd

routes_blueprint = Blueprint('routes', __name__)

UPLOAD_FOLDER = 'uploaded_files'
ALLOWED_EXTENSIONS = {'xlsx'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Landing page
@routes_blueprint.route('/landing')
def landing():
    username = "Pusarla Santosh"  # Example; replace with actual user data if available
    return render_template('landing.html', username=username)

# Main inventory page
@routes_blueprint.route('/')
def index():
    rice_bags = RiceBag.query.all()
    return render_template('index.html', rice_bags=rice_bags)

# Add a new rice bag
@routes_blueprint.route('/add', methods=['GET', 'POST'])
def add_rice_bag():
    if request.method == 'POST':
        name = request.form['name']
        weight = request.form['weight']
        price = request.form['price']
        if not name or not weight or not price:
            flash('All fields are required!', 'error')
            return redirect(url_for('routes.add_rice_bag'))

        new_rice_bag = RiceBag(name=name, weight=weight, price=price)
        db.session.add(new_rice_bag)
        db.session.commit()
        flash('Rice bag added successfully!', 'success')
        return redirect(url_for('routes.index'))

    return render_template('add_rice_bag.html')

@routes_blueprint.route('/edit/<int:bag_id>', methods=['GET', 'POST'])
def edit_rice_bag(bag_id):
    rice_bag = RiceBag.query.get_or_404(bag_id)
    if request.method == 'POST':
        rice_bag.name = request.form['name']
        rice_bag.weight = request.form['weight']
        rice_bag.price = request.form['price']
        db.session.commit()
        flash('Rice bag updated successfully!', 'success')
        return redirect(url_for('routes.index'))

    return render_template('edit_rice_bag.html', rice_bag=rice_bag)


# Delete a rice bag
@routes_blueprint.route('/delete/<int:bag_id>', methods=['POST'])
def delete_rice_bag(bag_id):
    rice_bag = RiceBag.query.get_or_404(bag_id)
    db.session.delete(rice_bag)
    db.session.commit()
    flash('Rice bag deleted successfully!', 'success')
    return redirect(url_for('routes.index'))

# Export data to Excel
@routes_blueprint.route('/export')
def export_to_excel():
    rice_bags = RiceBag.query.all()
    data = [{'Name': bag.name, 'Weight': bag.weight, 'Price': bag.price} for bag in rice_bags]
    df = pd.DataFrame(data)
    filepath = os.path.join(UPLOAD_FOLDER, 'exported_data.xlsx')
    df.to_excel(filepath, index=False)

    flash(f'Data exported successfully to {filepath}!', 'success')
    return redirect(url_for('routes.index'))

# Upload Excel file
@routes_blueprint.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part!', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file!', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Process the Excel file
            try:
                df = pd.read_excel(filepath)
                for _, row in df.iterrows():
                    rice_bag = RiceBag(name=row['Name'], weight=row['Weight'], price=row['Price'])
                    db.session.add(rice_bag)
                db.session.commit()
                flash('Data imported successfully!', 'success')
            except Exception as e:
                flash(f'Error processing file: {e}', 'error')
            return redirect(url_for('routes.index'))

        flash('Invalid file format! Only .xlsx files are allowed.', 'error')
    return render_template('upload_excel.html')
