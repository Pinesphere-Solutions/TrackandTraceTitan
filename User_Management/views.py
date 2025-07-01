from django.shortcuts import render

def user_list(request):
    return render(request, 'User_Management/Admin_Panel.html')