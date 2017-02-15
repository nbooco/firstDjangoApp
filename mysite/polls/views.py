from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Question

# View for the main page; displays the five most recent questions
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
            'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))

# View for seeing a specific question and its responses
def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

# View for seeing the results for a specific question
def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

# View for voting on a specific question
def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
