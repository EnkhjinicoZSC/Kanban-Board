from flask import Flask, session, g, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import functools

#first step in starting a flask app
app = Flask(__name__)

#configuring the database
app.secret_key = '1vbcxesfg2degd2bg34gsdf12hfs2jh'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#initializing sqlalchemy
db=SQLAlchemy(app)

#creating of the model
class Note(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)
    TaskName = db.Column(db.String(100))
    TaskTime = db.Column(db.Float(20))
    description = db.Column(db.String(100))
    level = db.Column(db.String(100))
    
    
class User(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)


with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(User(username = "john", password = generate_password_hash("john123")))
    db.session.commit()
    db.session.add(Note(TaskName = "Read documentation", level = "todo", user_id = 1))
    db.session.add(Note(TaskName = "Buy a book", level = "todo", user_id = 1))
    db.session.add(Note(TaskName = "LeetCode", level = "in-progress", user_id = 1))
    db.session.add(Note(TaskName = "Finish mockup", level = "in-progress", user_id = 1))
    db.session.add(Note(TaskName = "Get a picture", level = "done", user_id = 1))
    db.session.add(Note(TaskName = "Workout", level = "done", user_id = 1))
    db.session.commit()
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view
    
    
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
    
    
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username = username).first()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmPassword = request.form["confirm-password"]
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not confirmPassword:
            error = 'Confirm Password is required.'
        elif confirmPassword != password:
            error = 'Confirm Password and Password are mismatching.'

        if error is None:
            try:
                user = User(username = username, password = generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))

        flash(error)

    return render_template('register.html')
#home route
@app.route('/')
@login_required
def index():
    # making the data to render from a descending order according to the datetime
    tasks_todo = Note.query.filter_by(level = "todo", user_id = g.user.id)
    # complete = Note.query.filter_by(complete=True).order_by(desc(Note.date)).all()
    tasks_in_progress = Note.query.filter_by(level = "in-progress", user_id = g.user.id)
    tasks_done = Note.query.filter_by(level = "done", user_id = g.user.id)
    return render_template('index.html', tasks_todo = tasks_todo, tasks_in_progress = tasks_in_progress, tasks_done = tasks_done)

#route for adding todos
@app.route('/add', methods=['POST'])
@login_required
def add():
    note = Note(TaskName = request.form['TaskName'], level = "todo", user_id = g.user.id)
    db.session.add(note)
    db.session.commit()
    return redirect (url_for('index'))

#route to mark completed task
@app.route('/updates', methods = ['POST'])
@login_required
def updates():
    id = request.form['id']
    note = Note.query.filter_by(id=int(id)).first()
    level = request.form['level']
    note.level = level
    db.session.commit()

    return redirect (url_for('index'))


#initiating the flask framework
if __name__ == "__main__":
    app.run(debug=True, port = 5001)

