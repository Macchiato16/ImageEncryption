from flask import Flask, render_template, redirect, url_for, request, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from auth import verify_user, register_user
from encryption import generate_key, encrypt_image, decrypt_image, decrypt_image_to_bytes
from forms import LoginForm, RegisterForm, UploadForm
from models import db, User, EncryptedImage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_first_request
def create_tables():
    db.create_all()
    if not os.path.exists("secret.key"):
        generate_key()  # 生成密钥文件


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        register_user(form.username.data, form.password.data)
        flash('注册成功。请登录。', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = verify_user(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('upload'))
        else:
            flash('登录失败。请检查用户名和密码。', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encrypted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.enc')

        file.save(filepath)
        encrypt_image(filepath, encrypted_filepath)

        encrypted_image = EncryptedImage(filename=filename, encrypted_path=encrypted_filepath, user_id=current_user.id)
        db.session.add(encrypted_image)
        db.session.commit()

        os.remove(filepath)  # 加密后删除原文件

        flash('图片上传并加密成功！', 'success')
        return redirect(url_for('upload'))
    return render_template('upload.html', form=form)


@app.route('/gallery')
@login_required
def gallery():
    images = EncryptedImage.query.filter_by(user_id=current_user.id).all()
    return render_template('gallery.html', images=images)


@app.route('/download/<int:image_id>')
@login_required
def download(image_id):
    image = EncryptedImage.query.get(image_id)
    if image and image.user_id == current_user.id:
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        decrypt_image(image.encrypted_path, decrypted_path)
        return send_file(decrypted_path, as_attachment=True)
    else:
        flash('无权下载此文件。', 'danger')
        return redirect(url_for('gallery'))


@app.route('/image/<int:image_id>')
@login_required
def view_image(image_id):
    image = EncryptedImage.query.get(image_id)
    if image and image.user_id == current_user.id:
        image_data = decrypt_image_to_bytes(image.encrypted_path)
        return send_file(BytesIO(image_data), mimetype='image/jpeg', as_attachment=False)
    else:
        flash('无权查看此文件。', 'danger')
        return redirect(url_for('gallery'))


if __name__ == '__main__':
    app.run(debug=True)
