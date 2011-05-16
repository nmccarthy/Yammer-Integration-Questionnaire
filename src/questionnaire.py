from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from models import Question, Response, Responder
from google.appengine.api import mail

class MainPage(webapp.RequestHandler):
    def get(self):
        numADQuestions = Question.gql('WHERE product = :1', 'ADSync').count()
        numSPQuestions = Question.gql('WHERE product = :1', 'SharePoint Web Part').count()
        numSSOQuestions = Question.gql('WHERE product = :1', 'SSO').count()

        values = { 'numADQuestions': numADQuestions, 'numSPQuestions': numSPQuestions, 'numSSOQuestions': numSSOQuestions }
        self.response.out.write(template.render('templates/index.html', values))

class ADSyncQuestionnaire(webapp.RequestHandler):
    def get(self):
        adQuestions = Question.gql('WHERE product = :1', 'ADSync')

        values = { 'adQuestions': adQuestions }
        self.response.out.write(template.render('templates/adsync.html', values))

class SharePointQuestionnaire(webapp.RequestHandler):
    def get(self):
        spQuestions = Question.gql('WHERE product = :1', 'SharePoint Web Part')

        values = { 'spQuestions': spQuestions }
        self.response.out.write(template.render('templates/sharepoint.html', values))

class SSOQuestionnaire(webapp.RequestHandler):
    def get(self):
        ssoQuestions = Question.gql('WHERE product = :1', 'SSO')

        values = { 'ssoQuestions': ssoQuestions }
        self.response.out.write(template.render('templates/sso.html', values))

class QuestionAdmin(webapp.RequestHandler):
    def get(self):
        questions = Question.all()

        values = {'questions': questions}
        self.response.out.write(template.render('templates/questionAdmin.html', values))

class ResponseReview(webapp.RequestHandler):
    def get(self):
        qId = int(self.request.get('id'))
        question = Question.get_by_id(qId)
        responses = Response.all()
        responses.filter("question =", question)

        values = {'responses': responses, 'question': question}
        self.response.out.write(template.render('templates/responses.html', values))

class NewQuestion(webapp.RequestHandler):
    def post(self):
        newQuestion = Question(text = self.request.get('questionText'), product = self.request.get('productChoice'))
        newQuestion.put()

        self.redirect('/qadmin')

class DeleteQuestion(webapp.RequestHandler):
    def get(self):
        raw_id = self.request.get('id')
        id = int(raw_id)
        question = Question.get_by_id(id)
        question.delete()

        self.redirect('/qadmin')

class ADRespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        adQuestions = Question.gql('WHERE product = :1', 'ADSync')

        for adQuestion in adQuestions:
            responseText = self.request.get('response' + str(adQuestion.key().id()))
            response = Response(text = responseText, question = adQuestion, responder = newUser)
            response.put()

        mail.send_mail('nmccarthy@gmail.com', 'nmccarthy@muchomail.com', 'Test Subject', 'Test Body')

        self.redirect('/adsuccess')

class SPRespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        spQuestions = Question.gql('WHERE product = :1', 'SharePoint Web Part')

        for spQuestion in spQuestions:
            responseText = self.request.get('response' + str(spQuestion.key().id()))
            response = Response(text = responseText, question = spQuestion, responder = newUser)
            response.put()

        self.redirect('/spsuccess')

class SSORespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        ssoQuestions = Question.gql('WHERE product = :1', 'SSO')

        for ssoQuestion in ssoQuestions:
            responseText = self.request.get('response' + str(ssoQuestion.key().id()))
            response = Response(text = responseText, question = ssoQuestion, responder = newUser)
            response.put()

        self.redirect('/ssosuccess')

class ADSuccess(webapp.RequestHandler):
    def get(self):
        values = {}
        self.response.out.write(template.render('templates/adSuccess.html', values))

class SPSuccess(webapp.RequestHandler):
    def get(self):
        values = {}
        self.response.out.write(template.render('templates/spSuccess.html', values))

class SSOSuccess(webapp.RequestHandler):
    def get(self):
        values = {}
        self.response.out.write(template.render('templates/ssoSuccess.html', values))

def main():
    run_wsgi_app(application)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/adsync', ADSyncQuestionnaire),
                                      ('/sharepoint', SharePointQuestionnaire),
                                      ('/sso', SSOQuestionnaire),
                                      ('/adrespond', ADRespond),
                                      ('/sprespond', SPRespond),
                                      ('/ssorespond', SSORespond),
                                      ('/adsuccess', ADSuccess),
                                      ('/spsuccess', SPSuccess),
                                      ('/ssosuccess', SSOSuccess),
                                      ('/qadmin', QuestionAdmin),
                                      ('/responses', ResponseReview),
                                      ('/newquestion', NewQuestion),
                                      ('/deletequestion', DeleteQuestion)],
                                     debug=True)

if __name__ == "__main__":
    main()