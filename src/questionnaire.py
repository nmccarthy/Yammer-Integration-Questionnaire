from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from models import Question, Response, Responder, ResponseSet
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
        responseSets = ResponseSet.all()

        values = {'questions': questions, 'responseSets': responseSets}
        self.response.out.write(template.render('templates/questionAdmin.html', values))

class ResponseReview(webapp.RequestHandler):
    def get(self):
        qId = int(self.request.get('id'))
        question = Question.get_by_id(qId)
        responses = Response.all()
        responses.filter("question =", question)

        values = {'responses': responses, 'question': question}
        self.response.out.write(template.render('templates/responses.html', values))

class ResponseSetReview(webapp.RequestHandler):
    def get(self):
        qId = int(self.request.get('id'))
        responseSet = ResponseSet.get_by_id(qId)
        responses = Response.all()
        responses.filter('responseSet =', responseSet)

        values = {'responseSet': responseSet, 'responses': responses}
        self.response.out.write(template.render('templates/responseSet.html', values))

class NewQuestion(webapp.RequestHandler):
    def post(self):
        newQuestion = Question(text = self.request.get('questionText'), product = self.request.get('productChoice'))
        newQuestion.put()

        self.redirect('/qadmin')

class DeleteQuestion(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        question = Question.get_by_id(id)
        question.delete()

        self.redirect('/qadmin')

class DeleteResponseSet(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        responseSet = ResponseSet.get_by_id(id)

        #First, need to delete all the responses that are associated with the response set that I'm deleting
        responses = Response.all()
        responses.filter('responseSet =', responseSet)
        
        for response in responses:
            response.delete()

        responseSet.delete()

        self.redirect('/qadmin')

class ADRespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        set = ResponseSet(product = 'ADSync', responder = newUser)
        set.put()

        adQuestions = Question.gql('WHERE product = :1', 'ADSync')

        htmlBody = '<h2>Response to ADSync Questionnaire</h2><p><i>Submitted by ' + newUser.name +', ' + newUser.email + '</i></p>'

        for adQuestion in adQuestions:
            responseText = self.request.get('response' + str(adQuestion.key().id()))
            response = Response(text = responseText, question = adQuestion, responseSet = set)
            response.put()
            htmlBody += '<h3>' + adQuestion.text + '</h3>' + '<p>' + response.text + '</p>'

        #send email notification
        sender = 'nmccarthy@gmail.com'
        recipients = ['nmccarthy@yammer-inc.com', 'nmccarthy@muchomail.com']
        sub = newUser.name + ' from ' + newUser.company + ' responded to the ADSync Questionnaire'
        plainBody = 'Get response here: http://yammerie.appspot.com/responsesets?id=' + str(set.key().id())

        mail.send_mail(sender, recipients, sub, plainBody, html = htmlBody)

        self.redirect('/adsuccess')

class SPRespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        set = ResponseSet(product = 'SharePoint Web Part', responder = newUser)
        set.put()

        spQuestions = Question.gql('WHERE product = :1', 'SharePoint Web Part')

        htmlBody = '<h2>Response to SharePoint Questionnaire</h2><p><i>Submitted by ' + newUser.name +', ' + newUser.email + '</i></p>'

        for spQuestion in spQuestions:
            responseText = self.request.get('response' + str(spQuestion.key().id()))
            response = Response(text = responseText, question = spQuestion, responseSet = set)
            response.put()
            htmlBody += '<h3>' + spQuestion.text + '</h3>' + '<p>' + response.text + '</p>'

        #send email notification
        sender = 'nmccarthy@gmail.com'
        recipients = ['nmccarthy@yammer-inc.com', 'nmccarthy@muchomail.com']
        sub = newUser.name + ' from ' + newUser.company + ' responded to the SharePoint Questionnaire'
        plainBody = 'Get response here: http://yammerie.appspot.com/responsesets?id=' + str(set.key().id())

        mail.send_mail(sender, recipients, sub, plainBody, html = htmlBody)

        self.redirect('/spsuccess')

class SSORespond(webapp.RequestHandler):
    def post(self):
        newUser = Responder(name = self.request.get('name'), email = self.request.get('email'), company = self.request.get('company'))
        newUser.put()

        set = ResponseSet(product = 'SSO', responder = newUser)
        set.put()

        ssoQuestions = Question.gql('WHERE product = :1', 'SSO')

        htmlBody = '<h2>Response to SSO Questionnaire</h2><p><i>Submitted by ' + newUser.name +', ' + newUser.email + '</i></p>'

        for ssoQuestion in ssoQuestions:
            responseText = self.request.get('response' + str(ssoQuestion.key().id()))
            response = Response(text = responseText, question = ssoQuestion, responseSet = set)
            response.put()
            htmlBody += '<h3>' + ssoQuestion.text + '</h3>' + '<p>' + response.text + '</p>'

        #send email notification
        sender = 'nmccarthy@gmail.com'
        recipients = ['nmccarthy@yammer-inc.com', 'nmccarthy@muchomail.com']
        sub = newUser.name + ' from ' + newUser.company + ' responded to the SSO Questionnaire'
        plainBody = 'Get response here: http://yammerie.appspot.com/responsesets?id=' + str(set.key().id())

        mail.send_mail(sender, recipients, sub, plainBody, html = htmlBody)

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
                                      ('/responsesets', ResponseSetReview),
                                      ('/deleteresponse', DeleteResponseSet),
                                      ('/newquestion', NewQuestion),
                                      ('/deletequestion', DeleteQuestion)],
                                     debug=True)

if __name__ == "__main__":
    main()