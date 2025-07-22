from flask import Flask , render_template, redirect, url_for,request
from flask import session
from flask_sqlalchemy import SQLAlchemy
import os


from werkzeug.security import generate_password_hash, check_password_hash
 
def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']   =  'app123' 
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CHART_FOLDER'] = os.path.join('static','charts')
    os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)
    app.config['PASSWORD_HASH']='app123'
    db.init_app(app)
    return app
db=SQLAlchemy()

class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    password=db.Column(db.String(20),nullable=False)
    fullname=db.Column(db.String(20),nullable=False)
    address=db.Column(db.String(20),nullable=False)
    pincode=db.Column(db.String(20),nullable=False)

    bookings=db.relationship('Booking',back_populates='user', cascade='all, delete-orphan')

class Parking(db.Model):
    __tablename__='parking'
    id=db.Column(db.Integer,primary_key=True)
    primary_location_name=db.Column(db.String(20),nullable=False)
    address=db.Column(db.String(20),nullable=False)
    pin_code=db.Column(db.String(20),nullable=False)
    price=db.Column(db.Float,nullable=False)
    number_of_spots = db.Column(db.Integer,nullable=False)

    spots=db.relationship('parkingSpot',back_populates='parking', cascade='all, delete-orphan')

class parkingSpot(db.Model):
    __tablename__='parkingSpot'
    id=db.Column(db.Integer,primary_key=True)
    parking_id=db.Column(db.Integer,db.ForeignKey('parking.id'),nullable=False)
    spot_number=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='A')

    parking=db.relationship('Parking',back_populates='spots')
    bookings=db.relationship('Booking',back_populates='spot', cascade='all, delete-orphan')

class Booking(db.Model):
    __tablename__='booking'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    spot_id=db.Column(db.Integer,db.ForeignKey('parkingSpot.id'),nullable=False)
    vehicle_number=db.Column(db.String(20),nullable=False)
    start_time=db.Column(db.DateTime,nullable=False)
    end_time=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='O')
    parking_cost=db.Column(db.Float,nullable=False)

    user=db.relationship('User',back_populates='bookings')
    spot=db.relationship('parkingSpot',back_populates='bookings')
     
def create_admin():
    admin=User.query.filter_by(username='admin').first()
    if not admin:
        admin=User(username='admin',fullname='admin',address='admin',pincode='123456',password=generate_password_hash('app123'))
        db.session.add(admin)
        db.session.commit()
app=create_app()
app.app_context().push()
with app.app_context():
    db.create_all()
    create_admin()

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        print(username,password)
        user=User.query.filter_by(username=username).first()
        if user:
            if not check_password_hash(user.password,password):
                return redirect(url_for('login'))
            if user.username=="admin":
                session['username'] = username
                return redirect(url_for('admin'))
            else:
                session['username'] = username
                session['user_id'] = user.id
                return redirect(url_for('user'))

            
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('admin.html')

@app.route('/user',methods =['GET','POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user.html')


@app.route('/register',methods =['GET','POST'])
def register():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        fullname=request.form['fullname']
        address=request.form['address']
        pincode=request.form['pincode']
        user=User(username=username,password=generate_password_hash(password),fullname=fullname,address=address,pincode=pincode)
        db.session.add(user)    
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')
    
@app.route('/parking',methods=['GET','POST'])
def parking():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        primary_location_name = request.form['primary_location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = request.form['price']
        number_of_spots = request.form['number_of_spots']
        
        new_parking = Parking(primary_location_name=primary_location_name, address=address, pin_code=pin_code, price=price, number_of_spots=number_of_spots)
        db.session.add(new_parking)
        db.session.commit()
        
        return redirect(url_for('parking'))
    
    parkings = Parking.query.all()
    return render_template('parking.html', parkings=parkings)

if __name__=='__main__':
    app.run(debug=True)
