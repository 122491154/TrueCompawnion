from django.shortcuts import render, redirect, get_object_or_404
from .models import Dog
from .forms import DogForm

def dog_list(request):
    dogs = Dog.objects.all()
    return render(request, 'dogs/dog_list.html', {'dogs': dogs})

def add_dog(request):
    if request.method == 'POST':
        form = DogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dog_list')
    else:
        form = DogForm()
    return render(request, 'dogs/add_dog.html', {'form': form})

def edit_dog(request, dog_id):
    dog = get_object_or_404(Dog, id=dog_id)
    if request.method == 'POST':
        form = DogForm(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            return redirect('dog_list')
    else:
        form = DogForm(instance=dog)
    return render(request, 'dogs/edit_dog.html', {'form': form, 'dog': dog})

def delete_dog(request, dog_id):
    dog = get_object_or_404(Dog, id=dog_id)
    dog.delete()
    return redirect('dog_list')

