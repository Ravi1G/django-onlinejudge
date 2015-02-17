from __future__ import absolute_import
from django.test.utils import override_settings
from django.test import TestCase
from django.contrib.auth.models import User, Group, AnonymousUser, Permission
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import get_backends
from itertools import product
from datetime import datetime, timedelta
from unittest.case import skip
from django.utils import timezone
from ..models import Challenge, Contest, Submission
from ..utils import build_url


#TODO: test score logic

@override_settings(AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',))
class TestViewPermission(TestCase):
    #TODO: test index view and contest report view

    def setUp(self):
        backends = get_backends()
        backends[0].supports_inactive_user = True
        group = Group.objects.create(name="Participants")
        group.permissions.add(Permission.objects.get(codename='can_test_submission'))
        group.permissions.add(Permission.objects.get(codename='add_submission'))
        group.permissions.add(Permission.objects.get(codename='change_submission'))
        self.users = {}
        #TODO: test without Participants perms, not mandatory since currently
        # all participants i.e. all users should have those perms
        self.USERNAME_GROUPS = (  #user      active   staff  superuser   groups
                                ('admin',     True,   True,    True,    ("Participants",)),
                                ('staff',     True,   True,    False,   ("Participants",)),
                                ('active',    True,   False,   False,   ("Participants",)),
                                ('inactive',  False,  False,   False,   ("Participants",)),
                                ('anonymous', False,  False,   False,   ()),
                                )
        self.USERNAMES = map(lambda u: u[0], self.USERNAME_GROUPS)
        for username, active, staff, superuser, groupnames in self.USERNAME_GROUPS:
            if username=='anonymous':
                continue
            user = User.objects.create_user(username=username,
                                            email=username+'@mail',
                                            password=username,
                                            )
            user.is_active = active
            user.is_staff = staff
            user.is_superuser = superuser
            for groupname in groupnames:
                group = Group.objects.get(name=groupname)
                user.groups.add(group)
            user.save()
            self.users[username] = user

        self.CONTEST_TYPES = list(product(("non participant", "participant"),
                                          ("due", "active", "finished"))) 
        self.contests = {}
        for contest_type in self.CONTEST_TYPES:
            contest = Contest.objects.create(name=" ".join(contest_type),)
            self.contests[contest_type] = contest
            if contest_type[0]=="participant":
                for username, user in self.users.items():
                    contest.participants.add(user)
            if contest_type[1]=="due":
                contest.start = timezone.now() + timedelta(hours=1)
                contest.finish = timezone.now() + timedelta(hours=2)
                assert(not contest.has_started)
            elif contest_type[1]=="active":
                contest.start = timezone.now() - timedelta(minutes=30)
                contest.finish = timezone.now() + timedelta(minutes=30)
                assert(contest.is_active)
            if contest_type[1]=="finished":
                contest.start = timezone.now() - timedelta(hours=2)
                contest.finish = timezone.now() - timedelta(hours=1)
                assert(contest.is_finished)
            contest.save()
            challenge = Challenge.objects.create(name=" ".join(contest_type),
                                                 contest=contest)
            for username, user in self.users.items():
                    Submission.objects.create(challenge=challenge,
                                              author=user)

    def login_user(self, username):
        if username=='anonymous':
            return AnonymousUser()
        user = self.users[username]
        login = self.client.login(username=user.username,
                                  password=user.username)
        if username!='inactive':  # https://code.djangoproject.com/ticket/19792
            self.assertEqual(login, True, "Cant login %s" % user.username)
        return user

    def _view_permissions(self, view_name, status_codes, for_user=None,
                          method="GET", is_ajax=False):
        """ Check that access to a view with given name for given user results
        in status code based on contest status and if the request user is
        participant. """
        method = self.client.get if method=="GET" else self.client.post
        errors = []
        for contest_type, status_codes in status_codes:
            contest = self.contests[contest_type]
            challenge = contest.challenge_set.all()[0]
            for username, status_code in zip(self.USERNAMES, status_codes):
                user = self.login_user(username)
                for_user_id = user.id if for_user is None else for_user.id
                extra = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'} \
                    if is_ajax else {}
                response = method(build_url(view_name, args=[challenge.slug],
                                            get={'user_id': for_user_id}),
                                            **extra)

                if response.status_code!=status_code:
                    errors.append("Wrong status code for view %s.\n "
                                  "Request user: %s\n "
                                  "For user: %s\n "
                                  "Contest type: %s\n "
                                  "Status code: %d (excpected %d)" % \
                                  (view_name, username, for_user,
                                   " ".join(contest_type),
                                   response.status_code, status_code))
                self.client.logout()
            self.assertEqual(errors, [], "\n\n".join(errors))

    def test_challenge_access(self):
        # challenge and submission for self
        STATUS_CODES = ( #                       admin staff act inact anon
                (('participant', 'due'),          (200, 200, 403, 302, 302)),
                (('participant', 'active'),       (200, 200, 200, 302, 302)),
                (('participant', 'finished'),     (200, 200, 403, 302, 302)),
                (('non participant', 'due'),      (200, 200, 403, 302, 302)),
                (('non participant', 'active'),   (200, 200, 403, 302, 302)),
                (('non participant', 'finished'), (200, 200, 403, 302, 302)),
                        )
        self._view_permissions("challenge", STATUS_CODES)
        self._view_permissions("submission_test", STATUS_CODES,
                               method="POST", is_ajax=True)

        # challenge report for self
        STATUS_CODES = ( #                       admin staff act inact anon
                (('participant', 'due'),          (200, 200, 403, 302, 302)),
                (('participant', 'active'),       (200, 200, 403, 302, 302)),
                (('participant', 'finished'),     (200, 200, 200, 302, 302)),
                (('non participant', 'due'),      (200, 200, 403, 302, 302)),
                (('non participant', 'active'),   (200, 200, 403, 302, 302)),
                (('non participant', 'finished'), (200, 200, 403, 302, 302)),
                        )
        self._view_permissions("challenge_report", STATUS_CODES)

        # submission results for self
        STATUS_CODES = ( #                       admin staff act inact anon
                (('participant', 'due'),          (200, 200, 403, 302, 302)),
                (('participant', 'active'),       (200, 200, 200, 302, 302)),
                (('participant', 'finished'),     (200, 200, 200, 302, 302)),
                (('non participant', 'due'),      (200, 200, 403, 302, 302)),
                (('non participant', 'active'),   (200, 200, 403, 302, 302)),
                (('non participant', 'finished'), (200, 200, 403, 302, 302)),
                        )
        self._view_permissions("submission_results", STATUS_CODES,
                               is_ajax=True)

        # every view for other user
        STATUS_CODES = ( #                       admin staff act inact anon
                (('participant', 'due'),          (200, 200, 403, 302, 302)),
                (('participant', 'active'),       (200, 200, 403, 302, 302)),
                (('participant', 'finished'),     (200, 200, 403, 302, 302)),
                (('non participant', 'due'),      (200, 200, 403, 302, 302)),
                (('non participant', 'active'),   (200, 200, 403, 302, 302)),
                (('non participant', 'finished'), (200, 200, 403, 302, 302)),
                        )
        other_user = self.users["admin"]
        self._view_permissions("challenge", STATUS_CODES, other_user)
        self._view_permissions("challenge_report", STATUS_CODES, other_user)
        self._view_permissions("submission_test", STATUS_CODES, other_user,
                               method="POST", is_ajax=True)
        self._view_permissions("submission_results", STATUS_CODES, other_user,
                               is_ajax=True)

    @skip("All participants i.e. all users have this permission.")
    def test_can_test_submission(self):
        STATUS_CODES = (  #     with permission, without permission 
                 ('admin',                 (200, 200)),
                 ('staff',                 (200, 302)),
                 ('active',                (200, 302)),
                 ('inactive',              (302, 302)),
                 ('anonymous',             (302, 302)),
                 )
        USERNAMES = map(lambda (u, g): u, STATUS_CODES)
        errors = []
        for username, status_codes in STATUS_CODES:
            user = self.login_user(username)
            for (has_test_perm, status_code) in enumerate(status_codes):
                test_perm = Permission.objects.get(codename='can_test_submission')
                if has_test_perm and username!='anonymous':
                    user.user_permissions.add(test_perm)
                response = self.client.get(reverse('submission_test',
                                                   args=[self.challenge.slug]))
                if response.status_code!=status_code:
                    errors.append("Wrong status code.\nUser: %s \n"
                                  "Status code: %d (excpected %d)" % \
                                  (username, response.status_code, status_code))
            if has_test_perm and username!='anonymous':
                user.user_permissions.add(test_perm)
            self.client.logout()
