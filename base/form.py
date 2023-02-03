from django.forms import ModelForm
from .models import Room,User
from django.contrib.auth.forms import UserCreationForm


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'  # all sẽ lấy tất cả các biến trong Room được định dạng trước để tự động tạo form lên web
        exclude = ['host', 'participants']




class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2',]
        





class Userform(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','name','username','email','bio']




















