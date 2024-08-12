from flask import Flask, render_template, redirect, session
from models import db, User, connect_db, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secrettunnel'

# Initialize the database
db.init_app(app)

# Create the tables (run this once, or use migrations)
with app.app_context():
    db.create_all()


@app.route('/')
def root():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.register(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        
        # Redirect to the user's personal page
        return redirect(f'/users/{user.username}')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session['username'] = user.username
            
            # Redirect to the user's personal page
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors.append('Invalid username/password')

    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_user(username):
    """Show user details (except password) and their feedback. Only accessible by the logged-in user."""
    
    if "username" not in session or session['username'] != username:
        return redirect('/login')

    user = User.query.get_or_404(username)
    feedback_list = Feedback.query.filter_by(username=username).all()

    return render_template('user_detail.html', user=user, feedback_list=feedback_list)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Delete user and their feedback, then log them out. Only accessible by the logged-in user."""
    
    if "username" not in session or session['username'] != username:
        return redirect('/login')

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()

    session.pop('username', None)

    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """Show form to add feedback and handle form submission. Only accessible by the logged-in user."""
    
    if "username" not in session or session['username'] != username:
        return redirect('/login')

    form = FeedbackForm()

    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{username}')

    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show form to edit feedback and handle form submission. Only accessible by the feedback author."""
    
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session['username'] != feedback.username:
        return redirect('/login')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback. Only accessible by the feedback author."""
    
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session['username'] != feedback.username:
        return redirect('/login')

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{feedback.username}')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)