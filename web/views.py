from django.http import Http404
from quiz.settings import QUIZ_DURATION
from datetime import datetime
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext
from django.utils.http import http_date
from quiz.web.models import Quiz, Question, QuizAnswer
from random import randint
import time

def start(request):
    if request.method == 'POST' and all(request.POST[k] != '' for k in ('name', 'email', 'phone')):
        q = Quiz.create(
            request.POST['name'][:128],
            request.POST['email'][:512],
            request.POST['phone'][:128])
        q.save()
        return redirect("/%x-%s-%x" % (q.id, q.digest(), randint(0x100, 0xFFF)))
    
    return render_to_response('start.html', context_instance=RequestContext(request))

def quiz(request, quiz, digest):
    q = get_object_or_404(Quiz, pk=int(quiz, 16))
    
    if digest != q.digest(): raise Http404
    
    ctx = { 'quiz': q, 'question': q.currentQuestion }
    
    if not q.isActive():
        return render_to_response('time-is-up.html', ctx, context_instance=RequestContext(request))
    
    if not q.currentQuestion:
        return render_to_response('out-of-Q.html', ctx, context_instance=RequestContext(request))
        
    if request.method == 'POST':
        answers = []
        for a in q.currentQuestion.answer_set.all():
            userAnswer = 'a' + str(a.id) in request.POST
            qa = QuizAnswer(quiz = q, answer = a, userAnswer = userAnswer)
            qa.save()
            answers.append(qa)
        
        q.points += 16 if all([a.userAnswer == a.answer.correct for a in answers]) else 0

        q.currentQuestion = Quiz.nextQuestion(q)
        q.save()        
        return redirect("/%x-%s-%x" % (q.id, q.digest(), randint(0x100, 0xFFF)))
        
    r = render_to_response('quiz.html', ctx, context_instance=RequestContext(request))
    r['Cache-Control'] = 'no-cache, no-store'
    return r
        
    
def question(request, question):
    q = get_object_or_404(Question, pk=question)
    return render_to_response('preview.html',
        { 'question': q}, context_instance=RequestContext(request))

def highscores(request):
    l = Quiz.objects.exclude(start__gt=(datetime.now() - QUIZ_DURATION)).order_by('-points', 'start')[:10]
    def ranking():
        for i in range(0, len(l)):
            if i == 0:
                rank = 1
            else:
                rank = rank + 1 if l[i - 1].points != l[i].points else rank
            l[i].rank = rank
            yield l[i]
        
    return render_to_response('highscore_iframe.html' if 'iframe' in request.GET else 'highscore.html',
        { 'scores': ranking(), 'totalPlayers': Quiz.objects.count() },
        context_instance=RequestContext(request))

def video(request):
    return render_to_response('video.html', context_instance=RequestContext(request))
