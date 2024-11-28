from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

# Student data with roll numbers and passwords
students = [
    {'roll_number': f'231032{i:03}', 'password': f'pass{i:03}', 'username': f'user{i:03}'} for i in range(1, 32)
]

# Faculty data with roles and passwords
faculty = [
    {'faculty_id': 'E001', 'password': 'electrical123', 'work_type': 'electric'},
    {'faculty_id': 'F002', 'password': 'furniture123', 'work_type': 'furniture'},
    {'faculty_id': 'C003', 'password': 'cleaning123', 'work_type': 'cleaning'},
    {'faculty_id': 'O004', 'password': 'other123', 'work_type': 'other'}
]

# Store grievances
grievances = []

# Dictionary to store confirmation status for grievances
grievance_confirmations = {}

# Decorator to check login status
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_type = session.get('user_type')
        if not user_type:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', bg_image='/static/backgrounds/home.jpg')

@app.route('/select_user_type', methods=['POST'])
def select_user_type():
    user_type = request.form.get('user_type')
    if user_type == 'student':
        return redirect(url_for('student_login'))
    elif user_type == 'faculty':
        return redirect(url_for('faculty_login'))
    return redirect(url_for('index'))

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        password = request.form.get('password')
        student = next((s for s in students if s['roll_number'] == roll_number and s['password'] == password), None)
        if student:
            session['user_type'] = 'student'
            session['roll_number'] = roll_number
            session['username'] = student['username']
            return redirect(url_for('interface'))
        else:
            flash('Invalid credentials! Please try again.')
    return render_template('student_login.html', bg_image='/static/backgrounds/student_login.jpg')

@app.route('/faculty_login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        password = request.form.get('password')
        faculty_member = next((f for f in faculty if f['faculty_id'] == faculty_id and f['password'] == password), None)
        if faculty_member:
            session['user_type'] = 'faculty'
            session['faculty_id'] = faculty_id
            session['work_type'] = faculty_member['work_type']
            return redirect(url_for('inbox'))
        else:
            flash('Invalid credentials! Please try again.')
    return render_template('faculty_login.html', bg_image='/static/backgrounds/faculty_login.jpg')

@app.route('/interface')
@login_required
def interface():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    return render_template('interface.html', 
                           username=session.get('username'), 
                           roll_number=session.get('roll_number'), 
                           grievance_confirmations=grievance_confirmations,
                           bg_image='/static/backgrounds/interface.jpg')

@app.route('/success')
@login_required
def success():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    return render_template('success.html', 
                           username=session.get('username'), 
                           roll_number=session.get('roll_number'), 
                           bg_image='/static/backgrounds/success.jpg')

@app.route('/your_grievances')
@login_required
def your_grievances():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    # Filter grievances for the current student
    user_grievances = [g for g in grievances if g['roll_number'] == session.get('roll_number')]
    
    return render_template('your_grievances.html', 
                           username=session.get('username'), 
                           roll_number=session.get('roll_number'), 
                           user_grievances=user_grievances,
                           grievance_confirmations=grievance_confirmations,
                           bg_image='/static/backgrounds/grievances.jpg')

@app.route('/submit_grievance', methods=['POST'])
@login_required
def submit_grievance():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    # Generate a unique grievance ID
    grievance_id = len(grievances) + 1
    
    grievance = {
        'id': grievance_id,
        'username': session.get('username'),
        'roll_number': session.get('roll_number'),
        'hostel_building': request.form.get('hostelBuilding'),
        'block': request.form.get('Blocks'),
        'room': request.form.get('roomNumber'),
        'description': request.form.get('description'),
        'work_type': request.form.get('grievanceType'),
        'status': 'pending'
    }
    
    # Add grievance to the list
    grievances.append(grievance)
    
    # Initialize confirmation status
    grievance_confirmations[grievance_id] = 'pending'
    
    # Redirect to success page
    return redirect(url_for('success'))

@app.route('/inbox')
@login_required
def inbox():
    if session.get('user_type') != 'faculty':
        return redirect(url_for('index'))
    work_type = session.get('work_type')
    relevant_grievances = [g for g in grievances if g['work_type'] == work_type]
    return render_template('inbox.html', 
                           grievances=relevant_grievances, 
                           grievance_confirmations=grievance_confirmations, 
                           bg_image='/static/backgrounds/inbox.jpg')

@app.route('/process_grievance', methods=['POST'])
@login_required
def process_grievance():
    if session.get('user_type') != 'faculty':
        return redirect(url_for('index'))
    
    grievance_id = int(request.form.get('grievance_id'))
    action = request.form.get('action')
    
    if action == 'completed':
        # Find the grievance
        for grievance in grievances:
            if grievance['id'] == grievance_id:
                grievance['status'] = 'completed'
                break
        grievance_confirmations[grievance_id] = 'waiting_confirmation'
    
    return redirect(url_for('inbox'))

@app.route('/confirm_grievance', methods=['POST'])
@login_required
def confirm_grievance():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    grievance_id = int(request.form.get('grievance_id'))
    confirmation = request.form.get('confirmation')
    
    if confirmation == 'yes':
        grievance_confirmations[grievance_id] = 'confirmed'
        # Find the grievance and update its status
        for grievance in grievances:
            if grievance['id'] == grievance_id:
                grievance['status'] = 'completed'
                break
    elif confirmation == 'no':
        grievance_confirmations[grievance_id] = 'rejected'
        # Find the grievance and update its status
        for grievance in grievances:
            if grievance['id'] == grievance_id:
                grievance['status'] = 'rejected'
                break
    
    return redirect(url_for('your_grievances'))

@app.route('/refresh_grievances', methods=['GET'])
@login_required
def refresh_grievances():
    if session.get('user_type') == 'student':
        return redirect(url_for('your_grievances'))
    elif session.get('user_type') == 'faculty':
        return redirect(url_for('inbox'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)