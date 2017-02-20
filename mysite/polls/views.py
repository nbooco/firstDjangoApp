from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import F

from .models import Question, Choice

# View for the main page; displays the five most recent questions
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be published in the future or those with no choices).
        """
        # Build a list of questions with choices
        questions_with_choices = set()
        for choice in Choice.objects.all():
            questions_with_choices.add(choice.question.id)
        return Question.objects.filter(
                id__in=questions_with_choices
            ).filter(
                pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


# View for seeing a specific question and its responses
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """ Excludes any questions that aren't published yet or that have no choices. """
        # Build a list of questions with choices and exclude questions not in that list
        questions_with_choices = set()
        for choice in Choice.objects.all():
            questions_with_choices.add(choice.question.id)
        # Excludes questions that don't have choices, then those that haven't been published yet
        return Question.objects.filter(id__in=questions_with_choices).filter(pub_date__lte=timezone.now())


# View for seeing the results for a specific question
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """ Excludes any questions that aren't published yet or that have no choices. """
        # Build a list of questions with choices and exclude questions not in that list
        questions_with_choices = set()
        for choice in Choice.objects.all():
            questions_with_choices.add(choice.question.id)
        # Excludes questions that don't have choices, then those that haven't been published yet
        return Question.objects.filter(id__in=questions_with_choices).filter(pub_date__lte=timezone.now())

# View for voting on a specific question
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
