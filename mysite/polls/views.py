from django.shortcuts import render
from django.http import HttpResponse

# View for the main page
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

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
