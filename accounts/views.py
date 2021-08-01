from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import Accounts, Captured
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.validators import EmailValidator
import cv2 as cv
import uuid
from .forms import AddUserForm, LoginForm, CapturedForm
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.conf import settings
import os


# Create your views here.


def check_session(request):
    if 'username' in request.session and 'typ' in request.session and 'name' in request.session:
        context_data = dict()
        context_data['username'], context_data['typ'], context_data['name'] = request.session['username'], \
                                                                              request.session['typ'], request.session[
                                                                                  'name']
        return context_data
    return False


def logout(request):
    try:
        del request.session['username']
        del request.session['typ']
        del request.session['name']
    except Exception as e:
        print(e)
        return redirect('accounts:login')
    return redirect('accounts:login')


def upload_file(request):
    form = CapturedForm(request.POST, request.FILES)
    username = "rishi"
    if request.is_ajax():
        if form.is_valid():
            img_file = request.FILES['captured']
            filename = img_file.name
            pth = os.path.join(settings.MEDIA_ROOT, "rishi", filename)
            with open(pth, "wb") as fp:
                for chunk in img_file.chunks():
                    fp.write(chunk)

            Captured.objects.create(
                userid=Accounts.objects.filter(username=username)[0],
                captured=filename,
                file_path=pth
            )

            return JsonResponse({'message': 'success'}, status=200)
    return JsonResponse({'message': 'fail'}, status=200)


class UploadImageView(View):
    template_name = "accounts/upload_image.html"

    # def post(self, request, **kwargs):
    #     form = CapturedForm(request.POST or None, request.FILES or None)
    #     if request.is_ajax():
    #         if form.is_valid():
    #             print(form.save())
    #     return JsonResponse({
    #         'message': 'success'
    #     },status=200)

    def get(self, request, **kwargs):
        context_data = {}
        return render(request, template_name=self.template_name, context=context_data)


class LoginView(View):
    template_name = "accounts/login.html"
    model = Accounts

    def get_queryset(self, email, password):
        try:
            user = Accounts.objects.filter(email=email)
            if not user:
                return False
            if not check_password(password, user[0].password):
                return False
            return user[0]
        except Accounts.DoesNotExist:
            return False

    def validation(self, email):
        validator = EmailValidator()
        try:
            validator(email)
            return {
                'email': email
            }
        except ValidationError:
            return {
                'error': 'Enter a valid email'
            }

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            return redirect('dashboard:home')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        validation = self.validation(email)
        if validation.get('email') and password:
            user_obj = self.get_queryset(email, password)
            if not user_obj:
                context_data = {
                    'error': True
                }
                return render(request, self.template_name, context_data)
            request.session['username'] = user_obj.username
            request.session['typ'] = user_obj.type
            request.session['name'] = user_obj.name
            return redirect('dashboard:home')
        else:
            context_data = {
                "email_error": validation.get('error'),
                "password_error": "Enter a valid password"
            }
            return render(request, self.template_name, context_data)


class AddUserView(CreateView):
    template_name = 'accounts/add_user.html'
    model = Accounts
    fields = '__all__'

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            return render(request, self.template_name, context_data)
        return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        add_user = AddUserForm(request.POST)

        if add_user.is_valid():
            new_user = add_user.save(commit=False)
            new_user.password = make_password(new_user.password)
            new_user.active = True
            new_user.save()
            context_data = {
                "userid": new_user.id,
                "name": new_user.name,
                "username": new_user.username
            }
            return render(request, self.template_name, context_data)
        else:
            context_data = {
                "form": add_user
            }
            return render(request, self.template_name, context_data)


class AllUserListView(View):
    template_name = "accounts/all_user.html"

    def get_queryset(self):
        try:
            obj = Accounts.objects.all()
            return obj
        except Exception:
            return None

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            if context_data['typ'] == 'Admin':
                context_data['userobj'] = self.get_queryset()
            return render(request, self.template_name, context_data)
        return redirect('accounts:login')


class UserListView(View):
    template_name = "accounts/profile.html"

    def get(self, request, username):
        context_data = check_session(request)
        if context_data:
            profile_obj = get_object_or_404(Accounts, username=username)
            context_data['profile_name'] = profile_obj.name
            return render(request, self.template_name, context_data)

        return redirect('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CaptureView(View):
    face_cascade = cv.CascadeClassifier("data/haarcascade_frontalface_alt.xml")
    eyes_cascade = cv.CascadeClassifier("data/haarcascade_eye_tree_eyeglasses.xml")
    img_file_path = os.path.join(settings.BASE_DIR, "capture")

    def detect_and_capture(self, frame):
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_gray = cv.equalizeHist(frame_gray)

        # -- Detect Faces
        faces = self.face_cascade.detectMultiScale(frame_gray, scaleFactor=1.5, minNeighbors=5)
        for (x, y, w, h) in faces:
            center = (x + w // 2, y + h // 2)
            face_frame = cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)

            face_roi = frame_gray[y:y + h, x:x + w]
            roi_color = face_frame[y:y + h, x:x + w]

            # -- In face, detect eyes
            eyes = self.eyes_cascade.detectMultiScale(face_roi)
            for (x2, y2, w2, h2) in eyes:
                eye_frame = cv.rectangle(roi_color, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
        cv.imshow('C for capture, Q for quit - Face detection', frame)

    def get(self, request):
        cap = cv.VideoCapture(0)
        rand_img_name = uuid.uuid4().hex
        if cap.isOpened():
            while cap.isOpened():
                ret, frame = cap.read()
                if frame is None:
                    return JsonResponse({
                        "msg": "No captured frame",
                        "status": 404
                    }, status=200)
                # cv.imwrite(f"{self.img_file_path}\{rand_img_name}.png", frame)
                self.detect_and_capture(frame)
                if cv.waitKey(25) & 0xff == ord('q'):
                    break
                if cv.waitKey(25) & 0xff == ord('c'):
                    break
            cap.release()
            cv.destroyAllWindows()

            return JsonResponse({
                "msg": "successfully captured",
                "status": 301,
                "file_name": rand_img_name + ".png"
            }, status=200)
        else:
            return JsonResponse({
                "msg": "camera not found, make sure camera is installed on your system",
                "status": 404
            }, status=200)
