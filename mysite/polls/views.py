from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Question

# View for the main page; displays the five most recent questions
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

# View for seeing a specific question and its responses
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

# View for seeing the results for a specific question
def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

# View for voting on a specific question
def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
