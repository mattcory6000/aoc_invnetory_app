from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

# In-memory storage
inventory_df = None
properties_df = None

@main.route('/')
def index():
    from flask import render_template
    return render_template("upload.html")

@main.route('/upload', methods=['GET', 'POST'])
def upload_files():
    global inventory_df, properties_df

    if request.method == 'POST':
        inventory_file = request.files.get('inventory_file')
        properties_file = request.files.get('properties_file')

        if not inventory_file or not properties_file:
            flash("Both files are required.")
            return redirect(request.url)

        try:
            inventory_df = pd.read_excel(inventory_file)
            properties_df = pd.read_excel(properties_file)
            flash("Files uploaded successfully!")
            return redirect(url_for('main.index'))  # We'll later redirect to a dashboard/search view
        except Exception as e:
            flash(f"Error reading files: {str(e)}")
            return redirect(request.url)

    return render_template('upload.html')

@main.route('/preview')
def preview_data():
    global inventory_df, properties_df

    if inventory_df is None or properties_df is None:
        flash("No files uploaded yet.")
        return redirect(url_for('main.upload_files'))

    try:
        # Select only needed columns
        inventory_trimmed = inventory_df[['Wine ID', 'Wine', 'Wine Code', 'BIN Location']]
        properties_trimmed = properties_df[['Wine ID', 'UPC']]

        # Merge on Wine ID
        merged_df = pd.merge(inventory_trimmed, properties_trimmed, on='Wine ID', how='left')

        # Rename for clarity
        merged_df.columns = ['Wine ID', 'Wine Name', 'Wine Code', 'Bin Location', 'UPC']

        # Convert to records for rendering
        records = merged_df.to_dict(orient='records')
        return render_template("preview.html", data=records)

    except Exception as e:
        flash(f"Error processing data: {str(e)}")
        return redirect(url_for('main.upload_files'))