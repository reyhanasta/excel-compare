import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import logging

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'  # Directory to temporarily store uploaded files
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}  # Allowed file extensions

# --- Flask App Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * \
    1024  # Optional: Limit file size (e.g., 16MB)
# Important: Change this for production!
app.secret_key = 'your_secret_key_here'

# Setup logging
logging.basicConfig(level=logging.INFO)

# --- Helper Functions ---


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_excel_safe(filepath):
    """Tries reading an Excel file with different engines."""
    try:
        # Try openpyxl first (for .xlsx)
        df = pd.read_excel(filepath, engine='openpyxl')
        app.logger.info(
            f"Successfully read {os.path.basename(filepath)} using openpyxl")
        return df
    except Exception as e_xlsx:
        app.logger.warning(
            f"Reading {os.path.basename(filepath)} with openpyxl failed: {e_xlsx}. Trying xlrd...")
        try:
            # Try xlrd as fallback (for .xls)
            df = pd.read_excel(filepath, engine='xlrd')
            app.logger.info(
                f"Successfully read {os.path.basename(filepath)} using xlrd")
            return df
        except Exception as e_xls:
            app.logger.error(
                f"Reading {os.path.basename(filepath)} with xlrd also failed: {e_xls}")
            raise ValueError(
                f"Could not read Excel file: {os.path.basename(filepath)}. Ensure it's a valid .xlsx or .xls file.") from e_xls


def perform_comparison(file1_path, file2_path, column_name):
    """
    Performs the column comparison between two Excel files.

    Args:
        file1_path (str): Path to the first Excel file.
        file2_path (str): Path to the second Excel file.
        column_name (str): The name of the column to compare.

    Returns:
        tuple: (unique_to_file1, unique_to_file2, error_message)
               Returns lists of unique values and None for error_message on success.
               Returns (None, None, error_message_string) on failure.
    """
    try:
        # Read Excel files safely
        df1 = read_excel_safe(file1_path)
        df2 = read_excel_safe(file2_path)

        # Validate column name existence
        if column_name not in df1.columns:
            return None, None, f"Column '{column_name}' not found in {os.path.basename(file1_path)}."
        if column_name not in df2.columns:
            return None, None, f"Column '{column_name}' not found in {os.path.basename(file2_path)}."

        # Extract, clean, and prepare data for comparison
        # Convert to string, strip whitespace, drop NaNs, get unique values
        col1_values = df1[column_name].dropna().astype(
            str).str.strip().unique()
        col2_values = df2[column_name].dropna().astype(
            str).str.strip().unique()

        set1 = set(col1_values)
        set2 = set(col2_values)

        # Find differences
        unique_to_file1 = sorted(list(set1 - set2))
        unique_to_file2 = sorted(list(set2 - set1))

        app.logger.info(f"Comparison successful for column '{column_name}'.")
        return unique_to_file1, unique_to_file2, None  # Success

    except ValueError as ve:  # Catch specific read errors from helper
        app.logger.error(f"ValueError during comparison: {ve}")
        return None, None, str(ve)
    except Exception as e:
        app.logger.error(
            f"An unexpected error occurred during comparison: {e}", exc_info=True)
        return None, None, f"An unexpected error occurred: {e}"


# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles both displaying the form (GET) and processing the upload (POST)."""
    if request.method == 'POST':
        # --- File Upload Handling ---
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('Both file parts are required!', 'error')
            return redirect(request.url)

        file1 = request.files['file1']
        file2 = request.files['file2']
        column_name = request.form.get('columnName', '').strip()

        if file1.filename == '' or file2.filename == '':
            flash('Both files must be selected!', 'error')
            return redirect(request.url)

        if not column_name:
            flash('Column name must be provided!', 'error')
            return redirect(request.url)

        # Check file types and save securely
        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)

            # Ensure upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

            results_data = None
            error_message = None
            try:
                file1.save(filepath1)
                app.logger.info(f"Saved file 1 to {filepath1}")
                file2.save(filepath2)
                app.logger.info(f"Saved file 2 to {filepath2}")

                # --- Perform Comparison ---
                unique1, unique2, error = perform_comparison(
                    filepath1, filepath2, column_name)

                if error:
                    error_message = error
                    # Show error to user via flash message
                    flash(error_message, 'error')
                    app.logger.warning(f"Comparison failed: {error}")
                else:
                    results_data = {
                        'unique1': unique1,
                        'unique2': unique2,
                        'colName': column_name,
                        'file1Name': filename1,
                        'file2Name': filename2
                    }
                    app.logger.info(
                        "Comparison successful, preparing results.")

            except Exception as e:
                app.logger.error(
                    f"An error occurred during file processing or comparison: {e}", exc_info=True)
                error_message = f"An unexpected error occurred: {e}"
                flash(error_message, 'error')  # Show generic error

            finally:
                # --- Cleanup: Delete temporary files ---
                try:
                    if os.path.exists(filepath1):
                        os.remove(filepath1)
                        app.logger.info(f"Removed temporary file: {filepath1}")
                    if os.path.exists(filepath2):
                        os.remove(filepath2)
                        app.logger.info(f"Removed temporary file: {filepath2}")
                except Exception as e_clean:
                    app.logger.error(
                        f"Error cleaning up temporary files: {e_clean}")

            # Render the template again, passing results or errors
            return render_template('index.html', results=results_data, error=error_message)

        else:
            flash('Invalid file type. Only .xlsx and .xls files are allowed.', 'error')
            return redirect(request.url)

    # --- GET Request Handling ---
    # Just display the initial form
    return render_template('index.html', results=None, error=None)


# --- Run the App ---
if __name__ == '__main__':
    # Make sure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Run in debug mode for development (auto-reloads, provides debugger)
    # IMPORTANT: Disable debug mode for production!
    app.run(debug=True)
