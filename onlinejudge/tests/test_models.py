from django.test import TestCase as DjangoTestCase
from onlinejudge.models import Contest, Challenge, Submission, TestCase, TestResult
from django.contrib.auth.models import User, Group, AnonymousUser, Permission


class TestModel(DjangoTestCase):
    def setUp(self):
        challenge = Challenge.objects.create(name="faktorijel", slug="fakt", score=0)
        submission = Submission.objects.create(challenge=challenge)
        test_case1 = TestCase.objects.create(challenge=challenge)
        test_case2 = TestCase.objects.create(challenge=challenge)
        test_case3 = TestCase.objects.create(challenge=challenge)
        test_case4 = TestCase.objects.create(challenge=challenge)
        test_case5 = TestCase.objects.create(challenge=challenge)
        test_result1 = TestResult.objects.create(test_case=testcase1, submission=submission,
                        status="OK", result="OK")
        test_result2 = TestResult.objects.create(test_case=testcase2, submission=submission,
                        status="OK", result="OK")
        test_result3 = TestResult.objects.create(test_case=testcase3, submission=submission,
                        status="OK", result="OK")
        test_result4 = TestResult.objects.create(test_case=testcase4, submission=submission,
                        status="OK", result="OK")
        test_result5 = TestResult.objects.create(test_case=testcase5, submission=submission,
                        status="OK", result="OK")
        participant = User.objects.create_user("igor", 'igor@igor.com', 'pass')

    def test_all_correct(self):
        """Should produce 100% or 5/5"""
        challenge = Challenge.objects.get(slug="fakt")
        challenge.set_submission_score(submission, participant, grading_type="ungraded")
        self.assertEqual(submission.score_percentage, '100')
        print 'this never gets called!'

print 'test'
