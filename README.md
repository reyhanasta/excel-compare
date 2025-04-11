# Excel Column Comparator (Python/Flask)

A simple web application built with Python and Flask that allows users to upload two Excel files (.xlsx or .xls) and compare the values within a specified column, highlighting the differences.

## Description

This tool provides a web interface where users can:

1.  Select two Excel files from their local machine.
2.  Specify the exact name of the column header they wish to compare in both files.
3.  Submit the files and column name for comparison.
4.  View the results, which list the unique values found only in the specified column of the first file and those found only in the second file.

The comparison logic handles basic data cleaning (ignores empty cells, treats values as strings, trims whitespace) before identifying differences.

## Features

- Web-based interface using Flask.
- Supports `.xlsx` and `.xls` file formats.
- Compares a user-specified column between two files.
- Displays unique values present only in File 1 or File 2.
- Basic error handling for file uploads and column validation.
- Temporary file storage with automatic cleanup.

## Requirements

- Python 3.x
- pip (Python package installer)
- The following Python libraries:
  - Flask
  - pandas
  - openpyxl (for `.xlsx` files)
  - xlrd (for `.xls` files)

## Setup and Installation

1.  **Clone the Repository (or download the files):**

    ```bash
    # If using git
    git clone <your-repository-url>
    cd <your-repository-folder>

    # Or, if you downloaded the files, navigate to the directory containing app.py
    ```

2.  **Navigate to Project Directory:**
    Make sure your terminal/command prompt is in the project's root directory (the one containing `app.py`).

3.  **Create Folders:**
    Ensure the `templates` folder exists and contains the `index.html` file. The `uploads` folder for temporary file storage will be created automatically by the script if it doesn't exist.

    ```
    your-project-folder/
    ├── app.py
    └── templates/
        └── index.html
    ```

4.  **Install Dependencies:**
    It's recommended to use a virtual environment:

    ```bash
    # Create a virtual environment (optional but recommended)
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    # Install required packages
    pip install Flask pandas openpyxl xlrd
    ```

## Running the Application

1.  **Start the Flask Server:**
    Make sure you are in the project's root directory and your virtual environment (if used) is activated. Run the following command:

    ```bash
    python app.py
    ```

2.  **Access the Application:**
    Open your web browser and navigate to:
    `http://127.0.0.1:5000`
    (Or the URL provided in the terminal output, usually the one above).

## Usage

1.  Open the application URL in your browser.
2.  Use the "Select First Excel File" button to choose your first file (File X).
3.  Use the "Select Second Excel File" button to choose your second file (File Y).
4.  Enter the exact, case-sensitive name of the column header you want to compare into the "Column Name to Compare" field.
5.  Click the "Compare Columns" button.
6.  The page will reload. Any errors (like missing files, wrong column names) will be shown as flash messages at the top. If successful, the results section will appear below the form, showing the unique values for each file.

## Configuration Notes

- **`UPLOAD_FOLDER`**: In `app.py`, this variable defines where uploaded files are temporarily stored. Defaults to `uploads/`.
- **`ALLOWED_EXTENSIONS`**: Defines which file extensions are permitted for upload. Defaults to `xlsx` and `xls`.
- **`app.secret_key`**: **IMPORTANT SECURITY NOTE:** The default `secret_key` in `app.py` is insecure and only suitable for development. For any production or shared deployment, you **MUST** replace `'your_secret_key_here'` with a long, random, and unpredictable string. It is highly recommended to load this key from an environment variable rather than hardcoding it. This key is essential for securing user sessions (used by `flash()` messages).

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.
