from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.db import IntegrityError

from simplesocial.groups.models import Group, GroupMember
from . import models


class CreateGroup(LoginRequiredMixin, generic.CreateView):
	fields = ('name', 'description')
	model = Group()


class SingleGroup(generic.DetailView):
	model = Group


class ListGroup(generic.ListView):
	model = Group


class JoinGroup(LoginRequiredMixin, generic.RedirectView):

	def get_redirect_url(self, *args, **kwargs):
		return reverse("groups:single", kwargs = {"slug": self.kwargs.get("slug")})

	def get(self, request, *args, **kwargs):
		group = get_object_or_404(Group, slug = self.kwargs.get("slug"))
		try:
			GroupMember.objects.create(user = self.request.user, group = group)
		except IntegrityError:
			messages.warning(self.request, ("Already a member of {}".format(group.name)))
		else:
			messages.success(self.request, ("You ae now a member of {} group".format(group.name)))
		return super().get(request, *args, **kwargs)


class LeaveGroup(LoginRequiredMixin, generic.RedirectView):

	def get_redirect_url(self, *args, **kwargs):
		return reverse("groups:single", kwargs = {"slug": self.kwargs.get("slug")})

	def get(self, request, *args, **kwargs):
		try:
			membership = models.GroupMember.objects.filter(
				user = self.request.user,
				group__slug = self.kwargs.get("slug"),
			).get()
		except models.GroupMember.DoesNotExist:
			messages.warning(self.request, "Cannot leave group you are not a member of")
		else:
			membership.delete()
			messages.success("Successfully left the group")
			return super().get(request, *args, **kwargs)
