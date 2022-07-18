
from dis import disco
import email
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
    _path = 'Hotel/Database/Rooms'
    mydata = fire.call(_path)
    return render_template('index.html', 
                            mydata=mydata,
                            username=username
                           )


@app.route("/payment/<username>", methods=["GET"])
def payment(username):
    if not session.get(username):
        return redirect(url_for("login"))

    from mydatabase import fire
    _path = 'Hotel/Database/Rooms'
    mydata = fire.call(_path)

    return render_template("payment.html",
                            username=username,
                            mydata=mydata,
                        )


@app.route("/payments/<username>", methods=["GET", "POST"])
def payments(username):
    if not session.get(username):
        return redirect(url_for("login"))

    firstname   = request.form['firstname']
    emailid     = request.form['emailid']
    address     = request.form['address']
    city        = request.form['city']
    state       = request.form['state']
    zip         = request.form['zip']

    cardname    = request.form['cardname']
    cardnumber  = request.form['cardnumber']
    expmonth    = request.form['expmonth']
    expyear     = request.form['expyear']
    cvv         = request.form['cvv']

    cardtype    = request.form.get('cardtype') # Payment Type Check
    VIP         = request.form.get('VIP') # VIP Condition
    daymonth    = request.form.get('daymonth') # month Condition

    from mydatabase import fire
    import random
    order_ID = random.randint(1000,9999)

    ename = emailid.split('@')[0].replace('.','_')
    domain = emailid.split('@')[1].split('.')[0]

    _path = f'Hotel/Database/Customer/{ename+domain}'
    times = fire.call(_path)

    if times == None:
        fire.sets(_path, 1)
    else:
        fire.sets(_path, times+1)

    _path = 'Hotel/Database/Rooms'
    booked_room = fire.call(_path)

    new_dict = {}
    for k, d in booked_room.items():
        if d == 'empty':
            new_dict[k] = d

    for i in new_dict:
        room = request.form.get(i)
        print('===(room)===> ', room)

        if room != None:
            _path = f'Hotel/Database/Rooms/{room}'
            fire.sets(_path, 'booked')

# ----------------------------------

    price = 10000 # per room price
    _path = f'Hotel/Database/Customer/{ename+domain}'
    persontype = fire.call(_path)

    count = sum(map(lambda x : x == 'booked',
             list(booked_room.values())))

    percentage_room_booked = 100*count/len(booked_room)
    print('===(percentage_room_booked)===> ', percentage_room_booked)
    
    if percentage_room_booked < 50.0:
        if VIP == 'on':
            discount = 25
            price -= price*discount/100

        if persontype <= 5:
            discount = 10
            price -= price*discount/100

        elif persontype > 5:
            discount = 20
            price -= price*discount/100

    if percentage_room_booked > 80.0:
        if persontype <= 5:
            increased = 40

        elif persontype > 5:
            increased = 10
        price += price*increased/100

    daymonth = int(daymonth.split('-')[1])
    print('===(month)===> ', daymonth)

    if daymonth in [12, 1, 2]:
        increased = 40
        price += price*increased/100

    print('===(cardtype)===> ', cardtype)
    if cardtype == 'Credit':
        discount = 10
        price -= price*discount/100

    if cardtype == 'Debit':
        if persontype <= 5:
            discount = 1
            price -= price*discount/100

        if VIP == 'on':
            discount = 4
            price -= price*discount/100

    print('===(price)===> ', price)

# ----------------------------------

    passdict = {
        'firstname' : firstname,
        'emailid' : emailid,
        'address' : address,
        'city' : city,
        'state' : state,
        'zip' : zip,

        'cardname' : cardname,
        'cardnumber' : cardnumber,
        'expmonth' : expmonth,
        'expyear' : expyear,
        'cvv' : cvv,

        'cardtype' : cardtype,
        'persontype' : persontype,
        'VIP' : VIP,
        'order_ID' : order_ID,
    }

    _path = f'Hotel/Database/Form/{order_ID}'
    fire.sets(_path, passdict)

    return render_template(
        "payment.html",
        username=username,
        mydata=new_dict,
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e='Page not Found'), 404


def create_db():
    """ # Execute this first time to create new db in current directory. """
    db.create_all()


# @app.route("/signup/", methods=["GET", "POST"]) # page for admin only
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