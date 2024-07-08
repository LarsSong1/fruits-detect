from django.shortcuts import render, redirect
from .forms import CreateUser
from django.utils.translation import activate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from .models import ImageModel, FruitCount
from .forms import ImageUploadForm
from urllib.error import HTTPError
import time
import os
from django.core.files import File
from django.conf import settings
import torch
import pathlib
from PIL import Image

# Create your views here.


class SingletonModel:
    _instance = None

    @staticmethod
    def get_instance():
        if SingletonModel._instance is None:
            SingletonModel()
        return SingletonModel._instance

    def __init__(self):
        if SingletonModel._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            # Deben cambiar esta ruta por la donde esta su red neuronal
            folder_path = 'C:/Users/jairg/Desktop/Frutas IA/fruitsState/IA/Aifruit.pt'
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=folder_path, force_reload=True)
            SingletonModel._instance = self



def Register(request):
    activate('es')
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CreateUser()

    return render(request, 'register.html', {'form': form})



def Home(request):
    user = request.user
    return render(request,'home.html', {
        'user': user
    })




def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username= username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')


    form = AuthenticationForm()   

    form.fields['username'].label = 'Nombre de usuario'
    form.fields['password'].label = 'Contraseña'
    return render(request, 'login.html', {"form":form})



def Logout(request):
    logout(request)
    return redirect('login')


class DetectFruits(CreateView):
    model = ImageModel
    template_name = 'detectFruit.html'
    fields = ["image"]

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                fruitImage = form.save(commit=False)
                fruitImage.user_id = request.user

                try:
                    img_path = fruitImage.image
                    imageByIa, bad_apple, bad_banana, bad_orange, bad_pomegranate, good_apple, good_banana, good_orange, good_pomegranate= fruitState(img_path)
                except HTTPError as e:
                    if e.code == 403:
                        print("Rate limit exceeded. Waiting before retrying...")
                        time.sleep(200)  # Esperar 60 segundos antes de reintentar
                        return fruitState(fruitImage.image.path)
                    else:
                        raise

              
                fruitImage.bad_apple = bad_apple
                fruitImage.bad_banana = bad_banana
                fruitImage.bad_orange = bad_orange
                fruitImage.bad_pomegrante = bad_pomegranate
                fruitImage.good_apple = good_apple
                fruitImage.good_banana = good_banana
                fruitImage.good_orange = good_orange
                fruitImage.good_pomegranate = good_pomegranate

                fruitsCount = FruitCount.objects.create()


                if bad_apple >= 1:
                    fruitImage.fruitsState += f'{bad_apple} '
                    fruitsCount.appleBad += bad_apple

                if bad_banana >= 1:
                    fruitImage.fruitsState += f'{bad_banana} '
                    fruitsCount.bananaBad

                if bad_orange >= 1:
                    fruitImage.fruitsState += f'{bad_orange} '
                    fruitsCount.orangeBad = bad_orange

                if bad_pomegranate >= 1:
                    fruitImage.fruitsState += f'{bad_pomegranate} '
                    fruitsCount.pomegranateBad = bad_pomegranate

                if good_apple >= 1:
                    fruitImage.fruitsState += f'{good_apple} '
                    fruitsCount.appleGood = good_apple

                if good_banana >= 1:
                    fruitImage.fruitsState += f'{good_banana} '
                    fruitsCount.bananaGood = good_banana

                if good_orange >= 1:
                    fruitImage.fruitsState += f'{good_orange} '
                    fruitsCount.orangeGood = good_orange

                if good_pomegranate >= 1:
                    fruitImage.fruitsState += f'{good_pomegranate} '
                    fruitsCount.pomegranateGood = good_pomegranate

                fruitsCount.save()
                fruitImage.fruitCount_id = fruitsCount
                processed_image_path = os.path.join(settings.DETECTION_MEDIA_ROOT, 'deteccion.png')
                imageByIa.save(processed_image_path)
                processed_image = File(open(processed_image_path, 'rb'))
                fruitImage.imagesDetected.save('deteccion.png', processed_image, save=False)

                fruitImage.image.name = 'mydetect.png'
                fruitImage.save()

                user_now = request.user.id
                return redirect('user-profile', user_id=user_now)
        else:
            form = ImageUploadForm()
        return render(request, 'addCocoaPhoto.html', {'form': form})


def fruitState(img_path):
    temp = pathlib.PosixPath   
    pathlib.PosixPath = pathlib.WindowsPath
    model_instance = SingletonModel.get_instance()
    model = model_instance.model
    img = Image.open(img_path)
    results = model(img)
    results.show()
    r_img = results.render()
    img_with_boxes = r_img[0]
    new_img = Image.fromarray(img_with_boxes) 

    fruits = []
    for fruta in results.xyxy[0]:
        x0, y0, x1, y1, confi, cla = fruta.numpy()
        fruits.append({
                'x0': x0,
                'y0': y0,
                'x1': x1,
                'y1': y1,
                'confianza': confi,
                'clase': cla
            })

    numBadApple = 0
    numBadOrange = 0
    numBadBanana = 0
    numBadPomegranate = 0
    numGoodApple = 0
    numGoodOrange = 0
    numGoodBanana = 0
    numGoodPomegranate = 0
    
    for dataFruits in fruits:
        if dataFruits['clase'] == 0:
            numBadApple += 1

        if dataFruits['clase'] == 1:
            numBadBanana += 1

        if dataFruits['clase'] == 2:
            numBadOrange +=1
        
        if dataFruits['clase'] == 3:
            numBadPomegranate += 1
        
        if dataFruits['clase'] == 4:
            numGoodApple += 1

        if dataFruits['clase'] == 5:
            numGoodBanana += 1

        if dataFruits['clase'] == 6:
            numGoodOrange += 1

        if dataFruits['clase'] == 7:
            numGoodPomegranate
        
    print(fruits)

    return new_img, numBadApple, numBadBanana, numBadOrange, numBadPomegranate, numGoodApple, numGoodBanana, numGoodOrange, numBadPomegranate







def Inventory(request):
    return render(request, 'inventory.html')