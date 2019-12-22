from app import db

class User(db.Model):
    UserID=db.Column(db.Integer, primary_key=True)
    UserName=db.Column(db.String(250))
    Password=db.Column(db.String(250))
    Email=db.Column(db.String(250))
    Phonenumber=db.Column(db.String(250))
    QQnumber=db.Column(db.String(250))
    Authority=db.Column(db.Integer)

class Book(db.Model):
    BookID=db.Column(db.Integer, primary_key=True)
    BookName=db.Column(db.String(250))
    Writer=db.Column(db.String(250))
    Description=db.Column(db.String(250))

class Bookshelf(db.Model):
    ShelfID=db.Column(db.Integer, primary_key=True)
    UserID=db.Column(db.Integer)
    BookID=db.Column(db.Integer)
    Read=db.Column(db.Boolean, default=False)
    Favor=db.Column(db.Boolean, default=False)