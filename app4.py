from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'


students = [
    {'roll_number': f'231032{i:03}', 'password': f'pass{i:03}', 'username': f'user{i:03}'} for i in range(1, 32)
]


faculty = [
    {'faculty_id': 'E001', 'password': 'electrical123', 'work_type': 'electric'},
    {'faculty_id': 'F002', 'password': 'furniture123', 'work_type': 'furniture'},
    {'faculty_id': 'C003', 'password': 'cleaning123', 'work_type': 'cleaning'},
    {'faculty_id': 'O004', 'password': 'other123', 'work_type': 'other'}
]


grievances = []


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
def interface():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    student_grievances = [g for g in grievances if g['roll_number'] == session.get('roll_number')]
    return render_template('interface.html', username=session.get('username'), roll_number=session.get('roll_number'),
                           grievances=student_grievances, bg_image='/static/backgrounds/interface.jpg')


@app.route('/submit_grievance', methods=['POST'])
def submit_grievance():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    grievance = {
        'id': len(grievances) + 1,
        'username': session.get('username'),
        'roll_number': session.get('roll_number'),
        'hostel_building': request.form.get('hostelBuilding'),
        'block': request.form.get('Blocks'),
        'room': request.form.get('roomNumber'),
        'description': request.form.get('description'),
        'work_type': request.form.get('grievanceType'),
        'status': 'pending',
        'image': None
    }
 
    grievances.append(grievance)
    return render_template('success.html', bg_image='/static/backgrounds/success.jpg')
@app.route('/view_grievances')

def view_grievances():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    student_grievances = [g for g in grievances if g['roll_number'] == session.get('roll_number')]
    return render_template('view_grievances.html', grievances=student_grievances, bg_image='/static/backgrounds/view_grievances.jpg')

@app.route('/confirm_completion', methods=['POST'])
def confirm_completion():
    grievance_id = int(request.form.get('grievance_id'))
    for grievance in grievances:
        if grievance['id'] == grievance_id and grievance['status'] == 'completed':
            grievance['status'] = 'confirmed'
            break
    return redirect(url_for('view_grievances'))


@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if session.get('user_type') != 'faculty':
        return redirect(url_for('index'))
    work_type = session.get('work_type')
    relevant_grievances = [g for g in grievances if g['work_type'] == work_type]

    if request.method == 'POST':
        grievance_id = int(request.form.get('grievance_id'))
        action = request.form.get('action')
        for grievance in grievances:
            if grievance['id'] == grievance_id:
                grievance['status'] = 'accepted' if action == 'accept' else 'declined'
                break
        return redirect(url_for('inbox'))

    return render_template('inbox.html', grievances=relevant_grievances, bg_image='/static/backgrounds/inbox.jpg')
@app.route('/mark_taken', methods=['POST'])


@app.route('/mark_taken', methods=['POST'])
def mark_taken():
    grievance_id = int(request.form.get('grievance_id'))
    for grievance in grievances:
        if grievance['id'] == grievance_id and grievance['status'] == 'pending':
            grievance['status'] = 'taken'
            break
    return redirect(url_for('inbox'))


@app.route('/mark_completed', methods=['POST'])
def mark_completed():
    grievance_id = int(request.form.get('grievance_id'))
    for grievance in grievances:
        if grievance['id'] == grievance_id and grievance['status'] == 'taken':
            grievance['status'] = 'completed'
            break
    return redirect(url_for('inbox'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
