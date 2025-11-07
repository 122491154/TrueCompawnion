from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .models import Dog

# ---------------------------
# Internal/admin views (protected)
# ---------------------------

@login_required
def home(request):
    dogs = Dog.objects.all().order_by("name")
    return render(request, "dogs/home.html", {"dogs": dogs})

@login_required
def add_dog(request):
    if request.method == "POST":
        # core
        name = request.POST.get("name")
        breed = request.POST.get("breed")
        age = request.POST.get("age")
        location = request.POST.get("location")
        description = request.POST.get("description")
        adopted = True if request.POST.get("adopted") == "on" else False
        image = request.FILES.get("image")
        microchip_number = request.POST.get("microchip_number")  # NEW

        # new filters
        activity_level = request.POST.get("activity_level") or ""
        coat_grooming = request.POST.get("coat_grooming") or ""
        training_difficulty = request.POST.get("training_difficulty") or ""
        weight_kg = request.POST.get("weight_kg") or None
        height_cm = request.POST.get("height_cm") or None

        dog = Dog.objects.create(
            name=name,
            breed=breed,
            age=(int(age) if age else 0),
            location=location or "",
            description=description or "",
            adopted=adopted,
            microchip_number=microchip_number or None,   # NEW
            activity_level=activity_level,
            coat_grooming=coat_grooming,
            training_difficulty=training_difficulty,
            weight_kg=(weight_kg if weight_kg else None),
            height_cm=(height_cm if height_cm else None),
        )
        if image:
            dog.image = image
            dog.save()
        return redirect("home")

    return render(request, "dogs/add_dog.html")

@login_required
def edit_dog(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    if request.method == "POST":
        # core
        dog.name = request.POST.get("name")
        dog.breed = request.POST.get("breed")
        age = request.POST.get("age")
        dog.age = int(age) if age else 0
        dog.location = request.POST.get("location") or ""
        dog.description = request.POST.get("description") or ""
        dog.adopted = True if request.POST.get("adopted") == "on" else False
        dog.microchip_number = request.POST.get("microchip_number") or None  # NEW

        # new filters
        dog.activity_level = request.POST.get("activity_level") or ""
        dog.coat_grooming = request.POST.get("coat_grooming") or ""
        dog.training_difficulty = request.POST.get("training_difficulty") or ""
        weight_kg = request.POST.get("weight_kg") or None
        height_cm = request.POST.get("height_cm") or None
        dog.weight_kg = weight_kg if weight_kg else None
        dog.height_cm = height_cm if height_cm else None

        image = request.FILES.get("image")
        if image:
            dog.image = image

        dog.save()
        return redirect("home")

    return render(request, "dogs/edit_dog.html", {"dog": dog})

@login_required
def delete_dog(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    if request.method == "POST":
        dog.delete()
        return redirect("home")
    return render(request, "dogs/delete_dog.html", {"dog": dog})

@login_required
def view_dog(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    return render(request, "dogs/view_dog.html", {"dog": dog})


# ---------------------------
# Public signup
# ---------------------------

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# ---------------------------
# Client/public catalogue (unchanged – already handles filters)
# ---------------------------

def client_home(request):
    qs = Dog.objects.all().order_by("name")
    dog_fields = {f.name for f in Dog._meta.get_fields()}

    q = request.GET.get("q")
    breed = request.GET.get("breed")
    activity = request.GET.get("activity")
    location = request.GET.get("location")
    coat = request.GET.get("coat")
    training = request.GET.get("training")
    age_min = request.GET.get("age_min")
    age_max = request.GET.get("age_max")
    w_min = request.GET.get("weight_min")
    w_max = request.GET.get("weight_max")
    h_min = request.GET.get("height_min")
    h_max = request.GET.get("height_max")

    if q:
        qs = qs.filter(name__icontains=q)
    if breed and "breed" in dog_fields:
        qs = qs.filter(breed__icontains=breed)
    if activity and "activity_level" in dog_fields:
        qs = qs.filter(activity_level__iexact=activity)
    if location and "location" in dog_fields:
        qs = qs.filter(location__icontains=location)
    if coat and "coat_grooming" in dog_fields:
        qs = qs.filter(coat_grooming__iexact=coat)
    if training and "training_difficulty" in dog_fields:
        qs = qs.filter(training_difficulty__iexact=training)
    if "age" in dog_fields:
        if age_min: qs = qs.filter(age__gte=age_min)
        if age_max: qs = qs.filter(age__lte=age_max)
    if "weight_kg" in dog_fields:
        if w_min: qs = qs.filter(weight_kg__gte=w_min)
        if w_max: qs = qs.filter(weight_kg__lte=w_max)
    if "height_cm" in dog_fields:
        if h_min: qs = qs.filter(height_cm__gte=h_min)
        if h_max: qs = qs.filter(height_cm__lte=h_max)

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    base_params = request.GET.copy()
    if "page" in base_params: base_params.pop("page")
    query_string = base_params.urlencode()

    return render(request, "client/home.html", {
        "dogs": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "query_string": query_string,
        "filters": {
            "q": q or "", "breed": breed or "", "activity": activity or "",
            "location": location or "", "coat": coat or "", "training": training or "",
            "age_min": age_min or "", "age_max": age_max or "",
            "weight_min": w_min or "", "weight_max": w_max or "",
            "height_min": h_min or "", "height_max": h_max or "",
        }
    })

def client_dog_detail(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    return render(request, "client/dog_detail.html", {"dog": dog})


# ---------------------------
# Optional: raw binary image
# ---------------------------

def dog_photo_bytes(request, pk: int):
    dog = get_object_or_404(Dog, pk=pk)
    if not hasattr(dog, "image_blob") or not dog.image_blob:
        raise Http404("No image stored as bytes.")
    content_type = getattr(dog, "image_mime", None) or "image/jpeg"
    return HttpResponse(dog.image_blob, content_type=content_type)
