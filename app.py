from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from models import User, LoginActivity, File, Folder
from auth import register_user, authenticate_user
from storage import save_file, get_user_files, get_file_content, save_folder, get_user_folders, delete_file, delete_folder
import zipfile
import io
import os
import secrets
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dicss.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def validate_csrf_token(token):
    return token == session.get('csrf_token')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
@login_required
def home():
    folder_id = request.args.get('folder_id', type=int, default=None)
    files = get_user_files(current_user.id, folder_id)
    folders = get_user_folders(current_user.id, folder_id)
    current_folder = Folder.query.get(folder_id) if folder_id else None
    
    # Compute breadcrumb trail
    ancestors = []
    folder = current_folder
    while folder:
        ancestors.insert(0, (folder.name, folder.id))
        folder = folder.parent
    
    return render_template('home.html', files=files, folders=folders, current_folder=current_folder, folder_id=folder_id, ancestors=ancestors)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token.', 'error')
        return redirect(url_for('home'))
    
    files = request.files.getlist('file')
    folder_id = request.form.get('folder_id', type=int, default=None)
    if not files or all(not f.filename for f in files):
        flash('No files selected for upload.', 'error')
        return redirect(url_for('home', folder_id=folder_id))
    
    for file in files:
        if file and file.filename:
            file_id = save_file(file, current_user.id, folder_id)
            if file_id:
                activity = LoginActivity(
                    user_id=current_user.id,
                    action='upload',
                    details=f"Uploaded file: {file.filename}"
                )
                db.session.add(activity)
    db.session.commit()
    flash('Files uploaded successfully!', 'success')
    return redirect(url_for('home', folder_id=folder_id))

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token.', 'error')
        return redirect(url_for('home'))
    
    name = request.form.get('name')
    parent_id = request.form.get('parent_id', type=int, default=None)
    if not name:
        flash('Folder name is required.', 'error')
        return redirect(url_for('home', folder_id=parent_id))
    
    folder_id = save_folder(name, current_user.id, parent_id)
    if folder_id:
        activity = LoginActivity(
            user_id=current_user.id,
            action='create_folder',
            details=f"Created folder: {name}"
        )
        db.session.add(activity)
        db.session.commit()
        flash('Folder created successfully!', 'success')
    return redirect(url_for('home', folder_id=parent_id))

@app.route('/delete_folder/<int:folder_id>')
@login_required
def delete_folder_route(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash('You do not have permission to delete this folder.', 'error')
        return redirect(url_for('home'))
    
    parent_id = folder.parent_id
    delete_folder(folder)
    activity = LoginActivity(
        user_id=current_user.id,
        action='delete_folder',
        details=f"Deleted folder: {folder.name}"
    )
    db.session.add(activity)
    db.session.commit()
    flash('Folder deleted successfully!', 'success')
    return redirect(url_for('home', folder_id=parent_id))

@app.route('/bulk_download')
@login_required
def bulk_download():
    file_ids = request.args.get('file_ids', '').split(',')
    file_ids = [id for id in file_ids if id.isdigit()]
    if not file_ids:
        flash('No valid files selected.', 'error')
        return redirect(url_for('home'))
    
    files = File.query.filter(File.id.in_(file_ids), File.user_id == current_user.id).all()
    if not files:
        flash('No valid files selected.', 'error')
        return redirect(url_for('home'))
    
    try:
        file_names = ", ".join([file.filename for file in files])
        activity = LoginActivity(
            user_id=current_user.id,
            action='download',
            details=f"Bulk downloaded files: {file_names}"
        )
        db.session.add(activity)
        db.session.commit()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for file in files:
                content = get_file_content(file)
                zip_file.writestr(file.filename, content)
        
        zip_buffer.seek(0)
        return Response(zip_buffer.getvalue(), mimetype='application/zip', headers={'Content-Disposition': 'attachment; filename=files.zip'})
    except Exception as e:
        flash(f"Error downloading files: {str(e)}", 'error')
        return redirect(url_for('home'))

@app.route('/bulk_delete')
@login_required
def bulk_delete():
    file_ids = request.args.get('file_ids', '').split(',')
    file_ids = [id for id in file_ids if id.isdigit()]
    if not file_ids:
        flash('No valid files selected.', 'error')
        return redirect(url_for('home'))
    
    files = File.query.filter(File.id.in_(file_ids), File.user_id == current_user.id).all()
    if not files:
        flash('No valid files selected.', 'error')
        return redirect(url_for('home'))
    
    try:
        file_names = ", ".join([file.filename for file in files])
        activity = LoginActivity(
            user_id=current_user.id,
            action='delete',
            details=f"Bulk deleted files: {file_names}"
        )
        db.session.add(activity)
        
        for file in files:
            delete_file(file)
        
        flash('Selected files deleted successfully!', 'success')
    except Exception as e:
        flash(f"Error deleting files: {str(e)}", 'error')
    return redirect(url_for('home'))

@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to access this file.', 'error')
        return redirect(url_for('home'))
    
    try:
        activity = LoginActivity(
            user_id=current_user.id,
            action='download',
            details=f"Downloaded file: {file.filename}"
        )
        db.session.add(activity)
        db.session.commit()
        
        content = get_file_content(file)
        return Response(content, mimetype='application/octet-stream', headers={'Content-Disposition': f'attachment; filename={file.filename}'})
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", 'error')
        return redirect(url_for('home'))

@app.route('/delete/<int:file_id>')
@login_required
def delete(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to delete this file.', 'error')
        return redirect(url_for('home'))
    
    try:
        activity = LoginActivity(
            user_id=current_user.id,
            action='delete',
            details=f"Deleted file: {file.filename}"
        )
        db.session.add(activity)
        
        delete_file(file)
        
        flash('File deleted successfully!', 'success')
    except Exception as e:
        flash(f"Error deleting file: {str(e)}", 'error')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('login'))
        
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            login_user(user)
            activity = LoginActivity(
                user_id=user.id,
                action='login',
                details=f"User {username} logged in"
            )
            db.session.add(activity)
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token.', 'error')
            return redirect(url_for('register'))
        
        username = request.form['username']
        password = request.form['password']
        logging.debug(f"Registering user: {username}")
        try:
            register_user(username, password)
            user = User.query.filter_by(username=username).first()
            if not user:
                raise ValueError("User creation failed")
            activity = LoginActivity(
                user_id=user.id,
                action='register',
                details=f"User {username} registered"
            )
            db.session.add(activity)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f"Registration failed: {str(e)}", 'error')
    return render_template('register.html')

@app.route('/activity')
@login_required
def activity():
    activities = LoginActivity.query.filter_by(user_id=current_user.id).order_by(LoginActivity.timestamp.desc()).all()
    return render_template('activity.html', activities=activities)

@app.route('/logout')
@login_required
def logout():
    activity = LoginActivity(
        user_id=current_user.id,
        action='logout',
        details=f"User {current_user.username} logged out"
    )
    db.session.add(activity)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)