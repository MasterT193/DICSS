Decentralized Intelligent Cloud Storage System (DICSS)
DICSS is a secure, user-friendly web application for storing and managing files locally with encryption. Built with Flask, it provides features like user authentication, folder organization, file encryption, and activity logging, all within a modern and intuitive user interface.
Features

User Authentication: Register and log in securely with username and password.
File Management: Upload, download, and delete files (supports .txt, .pdf, .jpg, .png, .docx).
Folder Organization: Create, navigate, and delete folders to organize files.
File Encryption: Files are encrypted using AES (via pycryptodome) and stored in uploads/shard0 or shard1.
Activity Logging: Tracks user actions (login, upload, delete, etc.) in a dedicated log.
Modern UI: Sleek design with card-based layouts, Font Awesome icons, and animated flash messages.
CSRF Protection: Secure forms with CSRF tokens.
Bulk Actions: Download or delete multiple files at once.

Technologies

Python 3.10+
Flask 2.3.2: Web framework.
Flask-SQLAlchemy 3.0.3: Database ORM.
Flask-Login 0.6.2: User session management.
Werkzeug 2.3.7: WSGI utilities (downgraded for compatibility).
bcrypt 4.0.1: Password hashing.
pycryptodome 3.18.0: File encryption.
SQLite: Lightweight database.
Font Awesome 5.15.4: Icons for UI.
Google Fonts: Poppins and Inter for typography.

Prerequisites

Python 3.10 or higher
pip (Python package manager)
Virtualenv (recommended)

Setup Instructions

Clone the Repository (if applicable, or create the project directory):
mkdir DICSS
cd DICSS


Create and Activate a Virtual Environment:
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate


Install Dependencies:Create a requirements.txt with the following content:
Flask==2.3.2
Flask-SQLAlchemy==3.0.3
Flask-Login==0.6.2
Werkzeug==2.3.7
bcrypt==4.0.1
pycryptodome==3.18.0

Then run:
pip install -r requirements.txt


Set Up Project Structure:Ensure the following directory structure:
DICSS/
├── static/
│   └── styles.css
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── activity.html
├── uploads/
│   ├── shard0/
│   └── shard1/
├── app.py
├── auth.py
├── extensions.py
├── models.py
├── storage.py
├── dicss.db (created on first run)
├── requirements.txt
└── README.md


Run the Application:
python app.py

The app will start at http://127.0.0.1:5000/. Open this URL in a browser.


Usage

Register:

Navigate to http://127.0.0.1:5000/register.
Enter a username and password to create an account.


Log In:

Go to http://127.0.0.1:5000/login.
Enter your credentials to access the home page.


Manage Files and Folders:

Create Folders: Use the "Create Folder" form to organize files.
Upload Files: Select files (multiple allowed) and upload them to the current folder.
Download/Delete: Use buttons next to each file or select multiple for bulk actions.
Navigate Folders: Click folder names to view contents, use the breadcrumb to go back.


View Activity Log:

Click "View Activity Log" to see a record of your actions (e.g., uploads, deletes).


Log Out:

Click "Logout" to end your session.



Directory Structure

app.py: Main Flask application with routes and logic.
auth.py: User authentication (register, login).
extensions.py: Database and Flask-Login initialization.
models.py: SQLAlchemy models (User, File, Folder, LoginActivity).
storage.py: File handling (encryption, sharding, storage).
static/styles.css: Modern CSS with Google Fonts and Font Awesome.
templates/*.html: Jinja2 templates for UI (home, login, register, activity).
uploads/shard0, uploads/shard1: Encrypted file storage.
dicss.db: SQLite database for users, files, folders, and activities.

Troubleshooting

ImportError: cannot import name 'url_decode' from 'werkzeug.urls':
Ensure Werkzeug==2.3.7 is installed:pip install werkzeug==2.3.7




Database Errors:
If the schema is outdated, delete dicss.db and restart the app:rm dicss.db
python app.py




UI Issues:
Clear browser cache or use incognito mode.
Ensure static/styles.css is updated and Font Awesome CDN is accessible.


TemplateSyntaxError:
Verify home.html uses the correct breadcrumb logic (no while loops).



Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss improvements.
License
MIT License
Copyright (c) 2025 Tanishq Verma
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
