from datetime import datetime
from django.db import models
from quiz.settings import QUIZ_DURATION
import hashlib

class Question(models.Model):
    title = models.CharField(max_length=1024)
    question = models.TextField(blank=True)
    visible = models.BooleanField()
    
    def __unicode__(self):
        return self.title
    
class Answer(models.Model):
    answer = models.TextField()
    question = models.ForeignKey(Question)
    correct = models.BooleanField()

class Quiz(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=512)
    phone = models.CharField(max_length=128)
    points = models.IntegerField()
    start = models.DateTimeField()
    currentQuestion = models.ForeignKey(Question, null=True, blank=True)
    
    @staticmethod
    def create(name, email, phone):
        q = Quiz()
        q.name = name
        q.email = email
        q.phone = phone
        
        l = Question.objects.filter(visible=True).order_by('?')
        q.currentQuestion = l[0] if l else None
        
        q.points = 0
        q.start = datetime.now()
        return q
    
    def digest(self):
        m = hashlib.md5()
        m.update(self.name)
        m.update(self.email)
        m.update(self.phone)
        m.update(self.start.ctime())
        return m.hexdigest()
    
    def end(self):
        return self.start + QUIZ_DURATION
    
    def isActive(self):
        return datetime.now() < self.end()
    
    def remainingSeconds(self):
        return (self.end() - datetime.now()).seconds if self.isActive() else -1
    
    def evalRank(self):
        if not self.isActive():
            return len(Quiz.objects.filter(points__gt=self.points).values('points').annotate()) + 1
        return None
    
    def nextQuestion(self):
        # randomly select a question that has not been answered for this quiz
        l = Question.objects.filter(visible=True).exclude(answer__quizanswer__quiz=self).order_by('?')[:1]
        return l[0] if l else None
    
class QuizAnswer(models.Model):
    quiz = models.ForeignKey(Quiz)
    answer = models.ForeignKey(Answer)
    userAnswer = models.BooleanField()