from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '2654598456186491'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nodue.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    college_name = db.Column(db.String(50), nullable=True)
    branch_name = db.Column(db.String(50), nullable=True)

# Nodue Request Model
class NodueRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref='nodue_requests')
    is_approved = db.Column(db.Boolean, default=False)
    hod_comment = db.Column(db.String(200))
    library_comment = db.Column(db.String(200))
    staff_comment = db.Column(db.String(200))
    college_name = db.Column(db.String(50), nullable=True)
    branch_name = db.Column(db.String(50), nullable=True)

class FacultyStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(50), nullable=False)
    branch_name = db.Column(db.String(50), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    staff_name = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user_nodue_form', methods=['GET', 'POST'])
@login_required
def user_nodue_form():
    if request.method == 'POST':
        nodue_request = NodueRequest(student=current_user, college_name=current_user.college_name, branch_name=current_user.branch_name)
        db.session.add(nodue_request)
        db.session.commit()
        flash('Nodue request submitted successfully!', 'success')

    return render_template('user_nodue_form.html')

@app.route('/admin_form', methods=['GET', 'POST'])
@login_required
def admin_form():
    if current_user.role == 'Admin':
        if request.method == 'POST':
            # Create faculty and staff entry
            faculty_name = request.form.get('faculty_name')
            staff_name = request.form.get('staff_name')
            faculty_staff_entry = FacultyStaff(
                college_name=current_user.college_name,
                branch_name=current_user.branch_name,
                faculty_name=faculty_name,
                staff_name=staff_name
            )
            db.session.add(faculty_staff_entry)
            db.session.commit()
            flash('Faculty and Staff information added successfully!', 'success')

        return render_template('admin_form.html')

    else:
        flash('Access denied. You are not authorized to view this page.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form =LoginForm()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html',form=form )

@app.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role.lower()
    return render_template(f'{role}_dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Routes for Nodue Certification
@app.route('/nodue_request', methods=['GET', 'POST'])
@login_required
def nodue_request():
    if request.method == 'POST':
        nodue_request = NodueRequest(student=current_user, college_name=current_user.college_name, branch_name=current_user.branch_name)
        db.session.add(nodue_request)
        db.session.commit()
        flash('Nodue request submitted successfully!', 'success')

    return render_template('nodue_request.html')

# Routes for HOD, Library, and Staff
@app.route('/hod_dashboard')
@login_required
def hod_dashboard():
    if current_user.role == 'HOD':
        nodue_requests = NodueRequest.query.filter_by(
            is_approved=False, college_name=current_user.college_name, branch_name=current_user.branch_name
        ).all()
        return render_template('hod_dashboard.html', nodue_requests=nodue_requests)
    else:
        flash('Access denied. You are not authorized to view this page.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/library_dashboard')
@login_required
def library_dashboard():
    if current_user.role == 'Library':
        nodue_requests = NodueRequest.query.filter_by(
            is_approved=True, library_comment=None, college_name=current_user.college_name, branch_name=current_user.branch_name
        ).all()
        return render_template('library_dashboard.html', nodue_requests=nodue_requests)
    else:
        flash('Access denied. You are not authorized to view this page.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.role == 'Staff':
        nodue_requests = NodueRequest.query.filter_by(
            is_approved=True, library_comment=True, staff_comment=None, college_name=current_user.college_name, branch_name=current_user.branch_name
        ).all()
        return render_template('staff_dashboard.html', nodue_requests=nodue_requests)
    else:
        flash('Access denied. You are not authorized to view this page.', 'danger')
        return redirect(url_for('dashboard'))

# Additional routes for faculty and staff information
@app.route('/faculty_staff')
@login_required
def faculty_staff():
    # Fetch faculty and staff information based on the college and branch
    faculty_staff_info = FacultyStaff.query.filter_by(
        college_name=current_user.college_name,
        branch_name=current_user.branch_name
    ).first()

    if faculty_staff_info:
        faculty_name = faculty_staff_info.faculty_name
        staff_name = faculty_staff_info.staff_name
    else:
        faculty_name = "Faculty Name Not Available"
        staff_name = "Staff Name Not Available"

    return render_template('faculty_staff.html', faculty_name=faculty_name, staff_name=staff_name, user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


