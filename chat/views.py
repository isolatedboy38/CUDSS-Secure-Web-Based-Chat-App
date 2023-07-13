from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import chatMessages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserModel
from django.db.models import Q
import json,datetime
from django.core import serializers
from django.core.files.storage import FileSystemStorage
import os
import shutil
import time

# Create your views here.
@login_required
def home(request):
    User = get_user_model()
    users = User.objects.all()
    chats = {}
    if request.method == 'GET' and 'u' in request.GET:
        # chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
        chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
        chats = chats.order_by('date_created')
    context = {
        "page":"home",
        "users":users,
        "chats":chats,
        "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
    }
    print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
    return render(request,"chat/home.html",context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account successfully created!')
            return redirect('chat-login')
        context = {
            "page":"register",
            "form" : form
        }
    else:
        context = {
            "page":"register",
            "form" : UserRegistrationForm()
        }
    return render(request,"chat/register.html",context)

@login_required
def profile(request):
    context = {
        "page":"profile",
    }
    return render(request,"chat/profile.html",context)

def get_messages(request):
    chats = chatMessages.objects.filter(Q(id__gt=request.POST['last_id']),Q(user_from=request.user.id, user_to=request.POST['chat_id']) | Q(user_from=request.POST['chat_id'], user_to=request.user.id))
    new_msgs = []

    for chat in list(chats):
        data = {}
        data['id'] = chat.id
        data['user_from'] = chat.user_from.id
        data['user_to'] = chat.user_to.id
        data['message'] = chat.message
        data['can_forward'] = chat.can_forward
        data['can_ssforward'] = chat.forwarding_enabled
        data['date_created'] = chat.date_created.strftime("%b-%d-%Y %H:%M")
        
        if chat.image:
            data['image'] = chat.image.url
        else:
            data['image'] = None

        if chat.pdf_file:
            data['pdf_file'] = chat.pdf_file.url
        else:
            data['pdf_file'] = None
        
        new_msgs.append(data)
    
    return HttpResponse(json.dumps(new_msgs), content_type="application/json")


def send_chat(request):
    resp = {}
    User = get_user_model()
    
    # print("Function Called")
    if request.method == 'POST':
        post = request.POST
        u_from = User.objects.get(id=post['user_from'])
        u_to = User.objects.get(id=post['user_to'])
        message = post['message']
        image = request.FILES.get('image', None)  # Get the uploaded image file, if any
        pdf_file = request.FILES.get('pdf_file', None) # Get the uploaded pdf file, if any
        can_forward = post['toggleValue']
        insert = chatMessages(user_from=u_from, user_to=u_to, message=message, image=image, pdf_file=pdf_file, can_forward=can_forward)

        try:
            insert.save()

            # TO MOVE FILE IMAGES TO STATIC/IMAGES
            if image:
                source_folder = os.path.join('images/')
                destination_folder = os.path.join('static/images/')

                if os.listdir(source_folder):
                    for file_name in os.listdir(source_folder):
                        if file_name.endswith('.jpg') or file_name.endswith('.png'):
                            shutil.move(source_folder + file_name, destination_folder + file_name)
                else:
                    resp['status'] = 'failed'
            
            if pdf_file:
                source_folder = os.path.join('images/doc/pdf/')
                destination_folder = os.path.join('static/images/doc/pdf/')

                if os.listdir(source_folder):
                    for file_name in os.listdir(source_folder):
                        if file_name.endswith('.pdf'):
                            shutil.move(os.path.join(source_folder, file_name), os.path.join(destination_folder, file_name))
                else:
                    resp['status'] = 'failed'
            # time.sleep(2)
            resp['status'] = 'success'
        except Exception as ex:
            resp['status'] = 'failed'
            resp['mesg'] = ex
        


    else:
        resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")

    
def forward_message(request):
    resp = {}
    if request.method == 'POST':
        post = request.POST
        
        message_id = post['chat_id']
        target_user_id = post['user_to']
        can_forward = post['agree']

        User = get_user_model()
        target_user = get_object_or_404(User, id=target_user_id)
        message = get_object_or_404(chatMessages, id=message_id)
        
        
            # create a new message with the same content and recipient as the original message
        new_message = chatMessages(user_from=message.user_from, user_to=target_user, message=message.message, image=message.image, can_forward=can_forward)
        new_message.save()
        
        # create a new message with the same content and recipient as the original message
        # new_message = chatMessages(user_from=message.user_from, user_to=target_user, message=message.message, image=message.image)
        # new_message.save()
        resp['status']= 'success'

    else:
        resp['status']= 'failed'
    

    
    return HttpResponse(json.dumps(resp), content_type="application/json")




def ssforward_message(request):
    resp = {}
    if request.method == 'POST':
        post = request.POST
        
        message_id = post['chat_id']
        can_forward = post['agree']

        User = get_user_model() 
        message = get_object_or_404(chatMessages, id=message_id)
        
        if can_forward == 'False':
            # Update the forwarding status of the message
            message.forwarding_enabled = False
            message.save()

            # Update the forwarding status for all previously forwarded messages
            chatMessages.objects.filter(message=message.message).update(forwarding_enabled=False)
            chatMessages.objects.filter(message=message.message).update(can_forward=False)

        elif can_forward == 'True':
            # Update the forwarding status of the message
            message.forwarding_enabled = True
            message.save()

            # Update the forwarding status for all previously forwarded messages
            chatMessages.objects.filter(message=message.message).update(forwarding_enabled=True)
            chatMessages.objects.filter(message=message.message).update(can_forward=True)

        resp['status']= 'success'

    else:
        resp['status']= 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")