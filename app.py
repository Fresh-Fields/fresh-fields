from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///test1.db"
db=SQLAlchemy(app)

class Test1(db.Model):
     
     name = db.Column(db.String(200), nullable = False)
     district = db.Column(db.Integer, nullable = False)
     email = db.Column(db.String(200), nullable = False)
     farmerid = db.Column(db.Integer, primary_key = True, nullable = False)
     number = db.Column(db.Integer, nullable = False)
     password = db.Column(db.String(200), nullable = False)
     
    
     date_created = db.Column(db.DateTime, default = datetime.utcnow)

     def __repr__(self) -> str:
         return f"{self.name} - {self.farmerid} - {self.number} - {self.email} - {self.district}"


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method=='POST':
        name = request.form['name']
        district = request.form['district']
        email = request.form['email']
        farmerid = request.form['farmerid']
        number = request.form['number']
        password = request.form['password']
        test1 = Test1(name=name, district=district, email=email, farmerid=farmerid, number=number, password=password)
        db.session.add(test1)
        db.session.commit()
        
    allTest1 = Test1.query.all() 
    return render_template('index.html', allTest1=allTest1)



@app.route('/show')
def show_registrations():
    allTest1 = Test1.query.all()
    return render_template('show.html', allTest1=allTest1)



@app.route('/show/<int:farmer_id>')
def show_registration(farmer_id):
    registration = Test1.query.filter_by(farmerid=farmer_id).first()
    if registration:
        print(registration)
        return render_template('show_registration.html', registration=registration)
      
    else:
        return "Registration not found"








if __name__ =="__main__":
    
    with app.app_context():
        db.create_all()  # This line creates the database tables if they don't exist
    app.run(debug=True)

  


    