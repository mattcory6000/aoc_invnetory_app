from flask import Blueprint
import pandas as pd
from flask import render_template, request, redirect, url_for, flash
import os

# In-memory storage
inventory_df = None
properties_df = None

main = Blueprint('main', __name__)

@main.route('/')
def index():
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
            return redirect(url_for('main.index'))
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
        inventory_trimmed = inventory_df[['Wine ID', 'Wine', 'Wine Code', 'BIN Location', 'Case Count', 'Bottle Count']]
        properties_trimmed = properties_df[['Wine ID', 'UPC']]
        merged_df = pd.merge(inventory_trimmed, properties_trimmed, on='Wine ID', how='left')
        merged_df.columns = ['Wine ID', 'Wine Name', 'Wine Code', 'Bin Location', 'Case Count', 'Bottle Count', 'UPC']
        records = merged_df.to_dict(orient='records')
        return render_template("preview.html", data=records)
    except Exception as e:
        flash(f"Error processing data: {str(e)}")
        return redirect(url_for('main.upload_files'))

@main.route('/count', methods=['GET', 'POST'])
def count():
    global inventory_df, properties_df

    if inventory_df is None or properties_df is None:
        flash("No data loaded. Please upload files first.")
        return redirect(url_for('main.upload_files'))

    upc_search = request.form.get('upc_search', '').strip()
    matched_record = None

    if request.method == 'POST' and upc_search:
        upc_normalized = upc_search.lstrip("'").strip()

        properties_trimmed = properties_df[['Wine ID', 'UPC']]
        wine_ids = properties_trimmed[properties_trimmed['UPC'].astype(str).str.lstrip("'").str.strip() == upc_normalized]['Wine ID']

        if not wine_ids.empty:
            wine_id = wine_ids.iloc[0]

            if 'Case Count' not in inventory_df.columns:
                inventory_df['Case Count'] = ''
            if 'Bottle Count' not in inventory_df.columns:
                inventory_df['Bottle Count'] = ''

            idx = inventory_df[inventory_df['Wine ID'] == wine_id].index
            if not idx.empty:
                i = idx[0]
                bin_input = request.form.get('bin_location', '')
                if bin_input:
                    inventory_df.at[i, 'BIN Location'] = bin_input
                case_input = request.form.get('case_count', '')
                if case_input:
                    inventory_df.at[i, 'Case Count'] = case_input
                bottle_input = request.form.get('bottle_count', '')
                if bottle_input:
                    inventory_df.at[i, 'Bottle Count'] = bottle_input
                flash("Count saved.")
        searched_wine_id = wine_id if not wine_ids.empty else None

    # Refresh match display after POST or GET with a valid UPC
    if upc_search:
        upc_normalized = upc_search.lstrip("'").strip()
        properties_trimmed = properties_df[['Wine ID', 'UPC']]
        wine_ids = properties_trimmed[properties_trimmed['UPC'].astype(str).str.lstrip("'").str.strip() == upc_normalized]['Wine ID']
        
        wine_id = searched_wine_id if 'searched_wine_id' in locals() else wine_ids.iloc[0]
        if wine_id is not None:
            idx = inventory_df[inventory_df['Wine ID'] == wine_id].index
            if not idx.empty:
                i = idx[0]
                wine_row = inventory_df.loc[i, ['Wine ID', 'Wine', 'Wine Code', 'BIN Location', 'Case Count', 'Bottle Count']]
                upc_row = properties_trimmed[properties_trimmed['Wine ID'] == wine_id].iloc[0]
                matched_record = {
                    'Wine ID': wine_row['Wine ID'],
                    'Wine Name': wine_row['Wine'],
                    'Wine Code': wine_row['Wine Code'],
                    'Bin Location': wine_row['BIN Location'],
                    'Case Count': wine_row['Case Count'],
                    'Bottle Count': wine_row['Bottle Count'],
                    'UPC': upc_row['UPC'],
                    'Show Count Only': True  # Used to trigger display-only mode in the template
                }
        else:
            flash("No match found for UPC.")

    return render_template('count.html', result=matched_record)