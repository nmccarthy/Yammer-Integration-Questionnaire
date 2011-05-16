from google.appengine.ext import db

class Question(db.Model):
    text = db.StringProperty()
    product = db.StringProperty()

class Responder(db.Model):
    name = db.StringProperty()
    company = db.StringProperty()
    email = db.EmailProperty()

class ResponseSet(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    product = db.StringProperty()
    responder = db.ReferenceProperty(Responder, collection_name='responseSets')     #a foreign key to relate this response to the person who entered it

class Response(db.Model):
    text = db.StringProperty(multiline=True)
    question = db.ReferenceProperty(Question, collection_name='responses')     #a foreign key to relate this answer to the question that it's associated with
    responseSet = db.ReferenceProperty(ResponseSet, collection_name='responses')