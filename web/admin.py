from models import Question, Answer
from django.contrib import admin

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    
admin.site.register(Question, QuestionAdmin)