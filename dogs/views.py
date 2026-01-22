from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

# ✅ ADDED (minimal)
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from .models import Dog, FavouriteDog, ClientProfile, AdoptionRequest
from .forms import DogForm


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ["full_name", "phone", "county", "area", "housing_document"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "county": forms.TextInput(attrs={"placeholder": "County"}),
            "area": forms.TextInput(attrs={"placeholder": "Area"}),
        }

    def clean_housing_document(self):
        file = self.cleaned_data.get("housing_document")
        if file:
            name = file.name.lower()
            if not name.endswith(".pdf"):
                raise ValidationError("Please upload a PDF file.")
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("File is too large (max 5 MB).")
        return file


@login_required
def home(request):
    dogs = Dog.objects.all().order_by("name")
    return render(request, "dogs/home.html", {"dogs": dogs})


def client_home(request):
    dogs = Dog.objects.filter(adopted=False).order_by("name")

    activity_level = request.GET.get("activity_level") or ""
    coat_grooming = request.GET.get("coat_grooming") or ""
    training_difficulty = request.GET.get("training_difficulty") or ""
    location = request.GET.get("location") or ""
    min_age = request.GET.get("min_age") or ""
    max_age = request.GET.get("max_age") or ""
    min_weight = request.GET.get("min_weight") or ""
    max_weight = request.GET.get("max_weight") or ""

    if activity_level:
        dogs = dogs.filter(activity_level=activity_level)
    if coat_grooming:
        dogs = dogs.filter(coat_grooming=coat_grooming)
    if training_difficulty:
        dogs = dogs.filter(training_difficulty=training_difficulty)
    if location:
        dogs = dogs.filter(location__icontains=location)
    if min_age:
        dogs = dogs.filter(age__gte=min_age)
    if max_age:
        dogs = dogs.filter(age__lte=max_age)
    if min_weight:
        dogs = dogs.filter(weight_kg__gte=min_weight)
    if max_weight:
        dogs = dogs.filter(weight_kg__lte=max_weight)

    paginator = Paginator(dogs, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    favourite_ids = []
    if request.user.is_authenticated:
        favourite_ids = list(
            FavouriteDog.objects.filter(user=request.user).values_list("dog_id", flat=True)
        )

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    context = {
        "page_obj": page_obj,
        "activity_levels": Dog.ACTIVITY_LEVEL_CHOICES,
        "coat_grooming_choices": Dog.COAT_GROOMING_CHOICES,
        "training_difficulty_choices": Dog.TRAINING_DIFFICULTY_CHOICES,
        "filter_values": {
            "activity_level": activity_level,
            "coat_grooming": coat_grooming,
            "training_difficulty": training_difficulty,
            "location": location,
            "min_age": min_age,
            "max_age": max_age,
            "min_weight": min_weight,
            "max_weight": max_weight,
        },
        "favourite_ids": favourite_ids,
        "query_string": query_string,
    }
    return render(request, "Client/home.html", context)


def client_dog_detail(request, pk):
    dog = get_object_or_404(Dog, pk=pk)

    is_favourite = False
    if request.user.is_authenticated:
        is_favourite = FavouriteDog.objects.filter(user=request.user, dog=dog).exists()

    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    # For clients: show their own request (if any)
    my_adoption_request = None
    if request.user.is_authenticated and not is_admin:
        my_adoption_request = AdoptionRequest.objects.filter(dog=dog, user=request.user).first()

    # For admins: show all requests for this dog
    adoption_requests = None
    if is_admin:
        adoption_requests = (
            AdoptionRequest.objects.filter(dog=dog)
            .select_related("user", "reviewed_by")
            .order_by("-created_at")
        )

    dog = get_object_or_404(Dog, pk=pk)

    # ✅ add this
    extra_images = dog.images.all()

    return render(
        request,
        "Client/dog_detail.html",
        {
            "dog": dog,
            "extra_images": extra_images,
            "is_favourite": is_favourite,
            "is_admin": is_admin,
            "my_adoption_request": my_adoption_request,
            "adoption_requests": adoption_requests,
        },
    )


@login_required
@require_POST
def request_adoption(request, pk):
    """
    Client submits an adoption request from the dog detail page.
    Uses your unique_together(dog, user) rule:
      - If request exists already, we update it back to PENDING (unless already ACCEPTED).
      - If none exists, create new.
    """
    dog = get_object_or_404(Dog, pk=pk)

    # Admins shouldn't request adoption
    if request.user.is_staff or request.user.is_superuser:
        return redirect("client_dog_detail", pk=dog.pk)

    # Optional: prevent requesting if dog is already adopted
    if dog.status == Dog.STATUS_ADOPTED or dog.adopted:
        return redirect("client_dog_detail", pk=dog.pk)

    message_text = (request.POST.get("message") or "").strip()

    ar, created = AdoptionRequest.objects.get_or_create(
        dog=dog,
        user=request.user,
        defaults={"message": message_text, "status": AdoptionRequest.STATUS_PENDING},
    )

    if not created:
        # If already accepted, don't allow resubmission
        if ar.status == AdoptionRequest.STATUS_ACCEPTED:
            return redirect("client_dog_detail", pk=dog.pk)

        # Reset to pending + update message
        ar.message = message_text
        ar.status = AdoptionRequest.STATUS_PENDING
        ar.reviewed_at = None
        ar.reviewed_by = None
        ar.admin_note = ""
        ar.save()

    return redirect("client_dog_detail", pk=dog.pk)


@login_required
@require_POST
def review_adoption_request(request, request_id):
    """
    Admin accepts/rejects a specific adoption request.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect("client_home")

    ar = get_object_or_404(AdoptionRequest, pk=request_id)
    decision = request.POST.get("decision")  # "accept" or "reject"
    admin_note = (request.POST.get("admin_note") or "").strip()

    if decision == "accept":
        ar.mark(AdoptionRequest.STATUS_ACCEPTED, reviewed_by=request.user, admin_note=admin_note)

        # Optional: mark dog reserved/adopted depending on your flow
        # Most systems reserve first, then later mark adopted.
        ar.dog.status = Dog.STATUS_RESERVED
        ar.dog.save()

    elif decision == "reject":
        ar.mark(AdoptionRequest.STATUS_REJECTED, reviewed_by=request.user, admin_note=admin_note)

    return redirect("client_dog_detail", pk=ar.dog.pk)


@login_required
def add_to_favourites(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    FavouriteDog.objects.get_or_create(user=request.user, dog=dog)
    next_url = request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("client_dog_detail", pk=dog.pk)


@login_required
def remove_from_favourites(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    FavouriteDog.objects.filter(user=request.user, dog=dog).delete()
    next_url = request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("client_dog_detail", pk=dog.pk)


def my_favourites(request):
    # FavouriteDog model uses related_name="favourite_dogs" on user
    # and related_name="favourited_by" on dog, so this is correct:
    dogs_qs = Dog.objects.filter(favourited_by__user=request.user).distinct()

    # IMPORTANT: convert to list so custom attributes persist into the template loop
    dogs = list(dogs_qs)

    # Pull the current user's adoption requests for these dogs
    requests = AdoptionRequest.objects.filter(user=request.user, dog__in=dogs)
    req_map = {r.dog_id: r for r in requests}

    # Attach a display-friendly status to each dog
    for dog in dogs:
        r = req_map.get(dog.id)
        dog.application_status = r.get_status_display() if r else "No application"

    return render(request, "Client/my_favourites.html", {"dogs": dogs})


@login_required
def add_dog(request):
    if request.method == "POST":
        form = DogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DogForm()
    return render(request, "dogs/add_dog.html", {"form": form})


@login_required
def edit_dog(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    if request.method == "POST":
        form = DogForm(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DogForm(instance=dog)
    return render(request, "dogs/edit_dog.html", {"form": form, "dog": dog})


@login_required
def delete_dog(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    if request.method == "POST":
        dog.delete()
        return redirect("home")
    return render(request, "dogs/delete_dog.html", {"dog": dog})


@login_required
def view_dog(request, pk):
    """
    Keep your admin view working, but also show adoption requests there.
    """
    dog = get_object_or_404(Dog, pk=pk)

    adoption_requests = (
        AdoptionRequest.objects.filter(dog=dog)
        .select_related("user", "reviewed_by")
        .order_by("-created_at")
    )

    return render(request, "dogs/view_dog.html", {"dog": dog, "adoption_requests": adoption_requests})


def dog_photo_bytes(request, pk: int):
    dog = get_object_or_404(Dog, pk=pk)
    if not hasattr(dog, "image_blob") or not dog.image_blob:
        raise Http404("No image stored as bytes.")
    content_type = getattr(dog, "image_mime", None) or "image/jpeg"
    return HttpResponse(dog.image_blob, content_type=content_type)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("client_home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("client_home")


@login_required
def profile(request):
    profile_obj, _ = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ClientProfileForm(instance=profile_obj)

    context = {
        "form": form,
        "user_obj": request.user,
        "profile_obj": profile_obj,
    }
    return render(request, "Client/profile.html", context)


# ✅ ADDED (minimal): admin-only view to see a client's profile + housing document
@staff_member_required
def admin_view_profile(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    profile_obj, _ = ClientProfile.objects.get_or_create(user=user_obj)

    context = {
        "form": None,  # no editing from admin in this view (keeps your existing profile page)
        "user_obj": user_obj,
        "profile_obj": profile_obj,
    }
    return render(request, "Client/profile.html", context)
