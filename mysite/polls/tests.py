import datetime
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from .models import Question, Choice


def create_question(question_text, days):
    """
    Creates a question with the given  'question_text' and published the given number of 'days' offset to now
    (negative for questions published in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text):
    """ Creates a choice for the given 'question' with the given 'choice_text' """
    return Choice.objects.create(question=question, choice_text=choice_text)


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """ was_published_recently() should return False for questions whose pub_date is in the future. """
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """ was_published_recently() should return False for questions whose pub_date is older than 1 day. """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ was_published_recently() should return True for questions whose pub_date is within the last day. """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """ If no questions exist, an appropriate message should be displayed. """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question_with_choices(self):
        """ Questions with a pub_date in the past and choices should be displayed on the index page. """
        past_question = create_question(question_text="Past question.", days=-30)
        # Ensures that question is not excluded for not having choices
        create_choice(question=past_question, choice_text='Choice 1.')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_past_question_with_no_choices(self):
        """ Questions with a pub_date in the past and no choices should not be displayed on the index page. """
        # Days value ensures that question is not excluded for being in the future
        past_question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_future_question_with_choices(self):
        """ Questions with a pub_date in the future and choices should not be displayed on the index page. """
        future_question = create_question(question_text="Future question.", days=30)
        # Ensures that question is not excluded for not having choices
        create_choice(question=future_question, choice_text='Choice 1.')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_future_question_with_no_choices(self):
        """ Questions with a pub_date in the future and no choices should not be displayed on the index page. """
        future_question = create_question(question_text="Future question.", days=30)
        # Ensures that question is not excluded for not having choices
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_with_choices_and_past_question_with_choices(self):
        """ Even if both past and future questions exist, only past questions should be displayed. """
        future_question = create_question(question_text="Future question.", days=30)
        past_question = create_question(question_text="Past question.", days=-30)
        # Ensures that questions are not excluded for not having choices
        create_choice(question=future_question, choice_text='Choice 1.')
        create_choice(question=past_question, choice_text='Choice A')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_future_question_with_choices_and_past_question_with_no_choices(self):
        """ 
        Future choices should be excluded even if they have choices; past choices should be excluded if they have no choices.
        """
        future_question = create_question(question_text="Future question.", days=30)
        past_question = create_question(question_text="Past question.", days=-30)
        # Ensures that questions are not excluded for not having choices
        create_choice(question=future_question, choice_text='Choice 1.')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_two_past_questions_with_choices(self):
        """ The questions index page may display multiple questions. """
        past_question_one = create_question(question_text="Past question 1.", days=-30)
        past_question_two = create_question(question_text="Past question 2.", days=-5)
        # Ensures that questions are not excluded for not having choices
        create_choice(question=past_question_one, choice_text='Choice 1.')
        create_choice(question=past_question_two, choice_text='Choice A')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """ The detail view of a question with a pub_date in the future should return a 404 not found. """
        future_question = create_question(question_text='Future question.', days=5)
        # Ensures that question is not excluded for not having choices
        create_choice(question=future_question, choice_text='Choice 1.')
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """ The detail view of a question with a pub_date in the past should display the question's text and choices. """
        past_question = create_question(question_text='Past Question.', days=-5)
        # Ensures that question is not excluded for not having choices
        create_choice(question=past_question, choice_text='Choice 1.')
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_detail_view_with_a_question_with_no_choices(self):
        """ The detail view of a question with no choices should return a 404 not found. """
        # Days value ensures that question is not excluded for being in the past
        choiceless_question = create_question(question_text='Choiceless question', days=-1)
        url = reverse('polls:detail', args=(choiceless_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_question_with_choices(self):
        """ The detail view of a question with choices should display the question's text and choices. """
        # Days value ensures that question is not excluded for being in the past
        question_with_choices = create_question(question_text='Question with choices.', days=-1)
        create_choice(question=question_with_choices, choice_text='Choice 1.')
        url = reverse ('polls:detail', args=(question_with_choices.id,))
        response = self.client.get(url)
        self.assertContains(response, question_with_choices.question_text)


class QuestionIndexResultsTests(TestCase):
    def test_results_view_with_a_future_question(self):
        """ The results view of a question with a pub_date in the future should return a 404 not found. """
        future_question = create_question(question_text='Future question.', days=5)
        # Ensures that question is not excluded for not having choices
        create_choice(question=future_question, choice_text='Choice 1.')
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """ 
        The results view of a question with a pub_date in the past should display the question's text and
        choices with vote totals for each.
        """
        past_question = create_question(question_text='Past question.', days=-5)
        # Ensures that question is not excluded for not having choices
        create_choice(question=past_question, choice_text='Choice 1.')
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_results_view_with_a_question_with_no_choices(self):
        """ The results view of a question with no choices should return a 404 not found. """
        # Days value ensures that question is not excluded for being in the past
        choiceless_question = create_question(question_text='Choiceless question', days=-1)
        url = reverse('polls:results', args=(choiceless_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_question_with_choices(self):
        """ The results view of a question with choices should display the question's text and choices. """
        # Days value ensures that question is not excluded for being in the past
        question_with_choices = create_question(question_text='Question with choices.', days=-1)
        create_choice(question=question_with_choices, choice_text='Choice 1.')
        url = reverse ('polls:results', args=(question_with_choices.id,))
        response = self.client.get(url)
        self.assertContains(response, question_with_choices.question_text)
