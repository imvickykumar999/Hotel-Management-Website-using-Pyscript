
from flask import Flask, render_template, request, \
url_for, redirect, flash, session, abort

from flask_sqlalchemy import sqlalchemy, SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
db_name = "auth.db"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{db}'.format(db=db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'configure strong secret key here'

db = SQLAlchemy(app)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    pass_hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '' % self.username


@app.route('/<username>')
def index(username):
    if not session.get(username):
        return redirect(url_for("login"))

    from mydatabase import fire
    mydata = fire.call()
    return render_template('index.html', 
                            mydata=mydata,
                            username=username
                           )


@app.route("/payment/<username>")
def user_home(username):
    if not session.get(username):
        return redirect(url_for("login"))
    
    return render_template("payment.html",
                            username=username,
                        )

@app.route("/thankyou/<username>", methods=["GET", "POST"])
def user_account(username):
    try:
        if request.method == "POST":
            if not session.get(username):
                abort(401)

            data = request.form['data']
            return render_template("thankyou.html", 
                                    username=username,
                                    data=data,
                                    )
    except Exception as e:
        return render_template('404.html', e=e)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e='Page not Found'), 404


def create_db():
    """ # Execute this first time to create new db in current directory. """
    db.create_all()


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
            
        if not (username and password):
            flash("Username or Password cannot be empty")
            return redirect(url_for('signup'))
        else:
            username = username.strip()
            password = password.strip()

        hashed_pwd = generate_password_hash(password, 'sha256')
        new_user = User(username=username, pass_hash=hashed_pwd,)
        db.session.add(new_user)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("Username {u} is not available.".format(u=username))
            return redirect(url_for('signup'))

        flash("User account has been created.")
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for('login'))
        else:
            username = username.strip()
            password = password.strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.pass_hash, password):
            session[username] = True

            return redirect(url_for("index", username=username))
        else:
            flash("Invalid username or password.")
    return render_template("login_form.html")


@app.route("/logout/<username>")
def logout(username):
    session.pop(username, None)

    flash("successfully logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)