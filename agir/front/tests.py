from datetime import timedelta
from unittest import mock

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from ..events.models import Event, OrganizerConfig, EventSubtype
from ..groups.models import SupportGroup, Membership
from ..people.models import Person, PersonTag
from ..polls.models import Poll, PollOption, PollChoice


class NavbarTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "test@test.com", display_name="Machine Machin", create_role=True
        )

        self.group = SupportGroup.objects.create(name="group")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_session_info_authenticated(self):
        self.client.force_login(self.person.role)
        response = self.client.get("/api/session/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Machine Machin", response.content)


class PagesLoadingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "test@test.com",
            create_role=True,
            contact_phone="+33600000000",
            contact_phone_status=Person.CONTACT_PHONE_VERIFIED,
        )
        self.client.force_login(self.person.role)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="event", start_time=now + day, end_time=now + day + hour
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, is_creator=True
        )

        self.group = SupportGroup.objects.create(name="group")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_see_event_details(self):
        response = self.client.get("/evenements/" + str(self.event.id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_group_details(self):
        response = self.client.get("/groupes/" + str(self.group.id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_event(self):
        response = self.client.get("/evenements/creer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_see_create_group(self):
        response = self.client.get("/groupes/creer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NBUrlsTestCase(TestCase):
    def test_create_group_redirect(self):
        # new event page
        response = self.client.get("/old/users/event_pages/new?parent_id=103")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, reverse("create_event"))

    def test_unkown_gives_404(self):
        response = self.client.get("/old/nimp")

        self.assertEqual(response.status_code, 404)


class PollTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            email="participant@example.com",
            created=timezone.now() + timedelta(days=-10),
            create_role=True,
        )
        self.poll = Poll.objects.create(
            title="title",
            description="description",
            start=timezone.now() + timedelta(hours=-1),
            end=timezone.now() + timedelta(days=1),
            rules={"min_options": 2, "max_options": 2},
        )
        self.poll.tags.add(PersonTag.objects.create(label="test_tag"))
        self.poll1 = PollOption.objects.create(poll=self.poll, description="Premier")
        self.poll2 = PollOption.objects.create(poll=self.poll, description="Deuxième")
        self.poll3 = PollOption.objects.create(poll=self.poll, description="Troisième")
        self.client.force_login(self.person.role)

    def test_can_view_poll(self):
        res = self.client.get(reverse("participate_poll", args=[self.poll.pk]))

        self.assertContains(res, '<h2 class="headline">title</h2>')
        self.assertContains(res, "<p>description</p>")
        self.assertContains(res, "Premier")
        self.assertContains(res, "Deuxième")
        self.assertContains(res, "Troisième")

    def test_cannot_view_not_started_poll(self):
        self.poll.start = timezone.now() + timedelta(hours=1)
        self.poll.save()
        res = self.client.get(reverse("participate_poll", args=[self.poll.pk]))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_view_finished_poll(self):
        self.poll.start = timezone.now() + timedelta(days=-1, hours=-1)
        self.poll.end = timezone.now() + timedelta(hours=-1)
        self.poll.save()
        res = self.client.get(reverse("participate_poll", args=[self.poll.pk]))

        self.assertRedirects(res, reverse("finished_poll"))

    def test_can_participate(self):
        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={"choice": [str(self.poll1.pk), str(self.poll3.pk)]},
        )

        self.assertRedirects(res, reverse("participate_poll", args=[self.poll.pk]))
        choice = PollChoice.objects.first()
        self.assertIn("test_tag", [str(tag) for tag in self.person.tags.all()])
        self.assertEqual(choice.person, self.person)
        self.assertCountEqual(
            choice.selection, [str(self.poll1.pk), str(self.poll3.pk)]
        )

    def test_cannot_participate_if_just_registered(self):
        person = Person.objects.create_insoumise(
            email="just_created@example.com", create_role=True
        )
        self.client.force_login(person.role)

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={"choice": [str(self.poll1.pk), str(self.poll3.pk)]},
        )
        self.assertContains(res, "trop récemment", status_code=403)

    def test_cannot_participate_twice(self):
        self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={"choice": [str(self.poll1.pk), str(self.poll3.pk)]},
        )

        res = self.client.get(reverse("participate_poll", args=[self.poll.pk]))
        self.assertContains(res, "Vous avez bien participé")

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={"choice": [str(self.poll1.pk), str(self.poll3.pk)]},
        )

        self.assertContains(res, "déjà participé", status_code=403)

    def test_must_respect_choice_number(self):
        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={"choice": [str(self.poll1.pk)]},
        )
        self.assertContains(res, "minimum")

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={
                "choice": [str(self.poll1.pk), str(self.poll2.pk), str(self.poll3.pk)]
            },
        )
        self.assertContains(res, "maximum")

    def test_redirects_if_not_verified(self):
        self.poll.rules["require_verified"] = True
        self.poll.save()

        poll_url = reverse("participate_poll", args=[self.poll.pk])
        res = self.client.get(poll_url)
        self.assertRedirects(res, reverse("send_validation_sms") + "?next=" + poll_url)

    def test_cannot_post_if_not_verified(self):
        self.poll.rules["require_verified"] = True
        self.poll.save()

        res = self.client.post(
            reverse("participate_poll", args=[self.poll.pk]),
            data={
                "choice": [str(self.poll1.pk), str(self.poll2.pk), str(self.poll3.pk)]
            },
        )
        self.assertEqual(res.status_code, 403)
