import os
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from extensions import db
from models import File, Folder
from flask import flash

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_file(file, key):
    cipher = AES.new(key, AES.MODE_EAX)
    file_data = file.read()
    ciphertext, tag = cipher.encrypt_and_digest(file_data)
    return cipher.nonce, ciphertext, tag

def decrypt_file(ciphertext, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise ValueError("Decryption failed: Invalid key or corrupted data")

def save_file(file, user_id, folder_id=None):
    if not allowed_file(file.filename):
        flash(f"File type {file.filename.rsplit('.', 1)[1]} not allowed.", 'error')
        return None

    key = get_random_bytes(32)
    file.seek(0)
    file_hash = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)

    existing_file = File.query.filter_by(file_hash=file_hash, user_id=user_id).first()
    if existing_file:
        flash('File already exists (duplicate detected).', 'error')
        return None

    shard = f"shard{user_id % 2}"
    upload_dir = os.path.join('uploads', shard)
    os.makedirs(upload_dir, exist_ok=True)

    try:
        nonce, ciphertext, tag = encrypt_file(file, key)
        filepath = os.path.join(upload_dir, f"{file_hash}.enc")
        metadata_path = os.path.join(upload_dir, f"{file_hash}.meta")

        with open(filepath, 'wb') as f:
            f.write(nonce + tag + ciphertext)

        with open(metadata_path, 'w') as meta_f:
            meta_f.write(base64.b64encode(key).decode())

        new_file = File(
            filename=file.filename,
            filepath=filepath,
            file_hash=file_hash,
            user_id=user_id,
            folder_id=folder_id
        )
        db.session.add(new_file)
        db.session.commit()
        return new_file.id
    except Exception as e:
        flash(f"Error saving file: {str(e)}", 'error')
        return None

def save_folder(name, user_id, parent_id=None):
    try:
        new_folder = Folder(name=name, user_id=user_id, parent_id=parent_id)
        db.session.add(new_folder)
        db.session.commit()
        return new_folder.id
    except Exception as e:
        flash(f"Error creating folder: {str(e)}", 'error')
        return None

def get_user_files(user_id, folder_id=None):
    query = File.query.filter_by(user_id=user_id)
    if folder_id is not None:
        query = query.filter_by(folder_id=folder_id)
    return query.all()

def get_user_folders(user_id, parent_id=None):
    query = Folder.query.filter_by(user_id=user_id)
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    return query.all()

def get_file_content(file):
    metadata_path = file.filepath.replace(".enc", ".meta")
    if not os.path.exists(metadata_path):
        raise ValueError(f"Metadata file missing for {file.filename}")

    try:
        with open(file.filepath, 'rb') as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        with open(metadata_path, 'r') as meta_f:
            key = base64.b64decode(meta_f.read().strip())

        return decrypt_file(ciphertext, key, nonce, tag)
    except Exception as e:
        raise ValueError(f"Error decrypting file {file.filename}: {str(e)}")

def delete_file(file):
    try:
        metadata_path = file.filepath.replace(".enc", ".meta")
        if os.path.exists(file.filepath):
            os.remove(file.filepath)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        db.session.delete(file)
        db.session.commit()
    except Exception as e:
        flash(f"Error deleting file {file.filename}: {str(e)}", 'error')

def delete_folder(folder):
    try:
        for file in folder.files:
            delete_file(file)
        for subfolder in folder.subfolders:
            delete_folder(subfolder)
        db.session.delete(folder)
        db.session.commit()
    except Exception as e:
        flash(f"Error deleting folder {folder.name}: {str(e)}", 'error')