from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth import authenticate, login
from .forms import UserEditForm, UserCreateForm

def view_profile(request, username=None):
    if not username:
        if not request.user:
            return HttpResponseForbidden()
        else:
            user = request.user
    else:
        user = get_object_or_404(User, username=username)
    return render(request, 'registration/profile.html', {'user': user})

def edit_user(request, next=None):
    user = User()
    user_form = UserCreateForm

    if request.method == "POST":
        form = user_form(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if username: 
                new_user = authenticate(username=request.POST['username'],
                                        password=request.POST['password'])
                login(request, new_user)
            # Do something. Should generally end with a redirect. For example:
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse("my_profile"))
    else:
        form = user_form(instance=user)
        
    context = {"form": form}
    return render(request, "registration/edit_user.html", context)