from django.shortcuts import render,redirect, HttpResponse
from .models import Room, Topic, Message,User
from django.db.models import Q #thư viện hỗ trợ cho search bar với nhiều điểu kiện khác nhau cùng lúc
from .form import RoomForm,Userform,MyUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
# rooms = [
#     {'id':1, 'name': 'This is room 1'},
#     {'id':2, 'name': 'This is room 2'},
#     {'id':3, 'name': 'This is room 3'},
# ]




def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    # q sẽ = bất cứ giá trị nào được đưa vào link ở home.html
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |  # dấu | mang ý nghĩa là "Or"
        Q(name__icontains = q) |
        Q(desciption__icontains = q) 
    )
    # nếu không add giá trị tìm kiếm vào filter thì nó sẽ hoạt động như .all và lấy tất cả object có trong database
    # icontains để tìm các từ khóa liên quan nhất đến từ khóa mà ta nhập vào link tìm kiếm hoặc search bar mà không cần phải ghi đúng hoàn toàn từ khóa đó
    # i trong icontains giúp cho việc tìm kiếm không phân biết giữa viết hoa và viết thường mà chỉ quan tâm kí tự được đưa vào
    # hai dấu gạch dưới __ là kí tự phải có mỗi khi ta dùng Field Lookups : icontains
    # Q là thư viện hỗ trợ cho search bar với nhiều điểu kiện khác nhau cùng lúc như topic, tên room, mô tả, host,....

    topics = Topic.objects.all()[:5]
    rooms_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')[:10]
    # room_messages sẽ filter tối đa 10 hoạt động gần nhấn liên quan đến topic được chọn
    # trong room__topic__name__icontains thì room là một biến trong hàm Message

    data = { 'rooms':rooms, 'topics':topics, 'rooms_count':rooms_count, 'room_messages':room_messages }
    return render(request,'base/home.html', data)




def room(request,room_id):
    rooms = Room.objects.get(id=room_id) 
    personal_messages = rooms.message_set.all().order_by('-created')
    # message_set mang ý nghĩa lấy tất cả (.all) từ các biến con (Message) được liên kết khóa chính bằng biến cha (Room) trong model
    participants = rooms.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=rooms,
            body=request.POST.get('body')
        )
        # dùng ".create()" cũng có tác dụng giống với ".save()" nhưng lưu được dạng string. Bên trong ".create()" ta dùng data thích hợp và gán nó với những biến mà hàm Message có
        rooms.participants.add(request.user)
        return redirect('room',room_id=rooms.id)

    data = {'rooms':rooms, 'personal_messages':personal_messages, 'participants':participants}
    return render(request,'base/room.html', data)



@login_required(login_url='login') 
def createRoom(request): 
    purpose = 'create'   # dùng để phân biệt giữa nhu cầu create và update của user để chọn html thích hợp bằng if else
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")
    data = {'form':form, 'purpose':purpose}
    return render(request, 'base/room_form.html',data)



# @login_required(login_url='login')
def updateroom(request, room_id):
    purpose = 'update'    # dùng để phân biệt giữa nhu cầu create và update của user để chọn html thích hợp bằng if else
    room = Room.objects.get(id=room_id)
    form = RoomForm(instance=room)

    # if request.user != room.host:
    #     messages.error(request, 'You can not edit that room')
    #     return redirect('home')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect("home")
    data = {'form':form, 'purpose':purpose}
    return render(request, 'base/room_form.html',data)



# @login_required(login_url='login')
def deleteroom(request, room_id):
    room = Room.objects.get(id=room_id)
    
    # if request.user != room.host:
    #     messages.error(request, 'You can not delete that room')
    #     return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, "base/delete.html",{'delete_object':room})



def login_user(request):
    page = 'login' # đặt để làm điều kiện phân biệt if/else ở templates login_register.html nên hiển thị login hay là register

    if request.user.is_authenticated:
        messages.success(request, 'Dont be an idiot! You are already login')
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login success')
            return redirect('home')
        else:
            messages.error(request, 'Email or Password does not correct, please try again')
        
        

    data = {'page':page}
    return render(request, "base/login_register.html",data)


def register_user(request):
    page = 'register'  # đặt để làm điều kiện phân biệt if/else ở templates login_register.html nên hiển thị login hay là register
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # "commit=False" giúp ta tạo ra object user nhưng không hoàn toàn đưa vào database mà vừa giữ tạm thời ở đó vừa để ta có thể sử dụng object
            user.username = user.username.lower()  # đưa username về dạng viết thường để tránh lỗi khi user vô tình viết hoa lên
            user.save()
            login(request,user)
            messages.success(request, 'Successful account creation, you can use this account from now on')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    data = {'page':page, 'form':form}
    return render(request, "base/login_register.html",data)



def logout_user(request):
    logout(request)
    return redirect('home')



def deleteMessage(request, message_id):
    message = Message.objects.get(id=message_id)
    
    # if request.user != message.user:
    #     messages.error(request, 'You can not delete this message')
    #     return redirect('room',message_id=message.id)

    if request.method == 'POST':
        message.delete()
        # return redirect('delete-message',message_id=message.id)
        return redirect('home')
    return render(request, "base/delete.html",{'delete_object':message})



 
def userProfile(request,user_id):
    user = User.objects.get(id=user_id)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    data = {'user':user, 'rooms':rooms,'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', data)





@login_required(login_url='login')
def updateUser(request):
    user = request.user
    forms = Userform(instance=user)
    if request.method == "POST":
        form = Userform(request.POST,request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('profile',user_id=user.id)
        else:
            messages.error(request, 'Can not update your profile because the data didnt validate')
            return redirect("update-user")
    data = {'forms':forms}
    return render(request, 'base/update-user.html',data)



def topicsPage(request): # hàm này tạo riêng một trang dành cho phiên bản mobile muốn xem mục topics
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    data={"topics":topics}
    return render(request, "base/topics.html",data)




def activityPage(request): # hàm này tạo riêng một trang dành cho phiên bản mobile muốn xem mục Recent Activity
    room_messages = Message.objects.all()
    data={"room_messages":room_messages}
    return render(request, "base/activity.html",data)
















