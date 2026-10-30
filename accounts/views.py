from django.shortcuts import render
from django.contrib import messages
from .forms import RegistrationForm
from .models import Account
from django.shortcuts import redirect
from django.contrib import auth 
from django.contrib.auth.decorators import login_required

# Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Carts 
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username,phone_number = phone_number, password = password )
            user.save()

            # Activation 
            current_site = get_current_site(request)
            mail_subject = "Please activate your account "
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request,'Thank you for registering with us , We have sent you a verification email to your email address, please verify')

            return redirect('/accounts/login/?command=verification&email='+email) 
    else:
        form = RegistrationForm()
    context = {
        'form' : form
    }
    return render(request,'accounts/register.html', context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email = email, password = password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.filter(carts = cart)
                for item in cart_item:
                    item.user = user
                    item.save()
            except Exception as e :
                print("error:",e)
                
            auth.login(request, user)
            # messages.success(request, "You are now loggend")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentils ")
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "sucessfully Logged Out")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        messages.success(request, 'Congratulaion your account is activated ')
        return redirect(login)
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email = email, is_active = True).exists():
            user = Account.objects.get(email__iexact=email)
            # Reset password 
            current_site = get_current_site(request)
            mail_subject = "Please reset  your password  "
            message = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Password reset email has been sent to your email address")
            return redirect(login)
        else:
            messages.error(request, "Account doesnot exists at all ")
            return redirect(forgotPassword)
    return render(request, 'accounts/forgotPassword.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')

    else:
        messages.error(request, "THis link is expired")
        return redirect(login)


def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()

            # Prevent reuse of the same session authorization
            request.session.pop('uid', None)

            messages.success(request, "Password reset is completed")
            return redirect(login)
        else:
            messages.error(request, "Password doesnot match")
            return redirect(resetPassword)
    return render(request, 'accounts/resetPassword.html')
