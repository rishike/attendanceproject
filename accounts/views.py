from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .models import Accounts, Captured
from django.views import View
from django.http import JsonResponse
from django.core.validators import EmailValidator
import cv2 as cv
from .forms import AddUserForm, LoginForm, CapturedForm, UpdateUserForm
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from PIL import Image
import copy
import numpy as np
from django.db import IntegrityError
import pickle
from datetime import datetime

# Create your views here.
ORIGINAL_UPLOAD_PATH = os.path.join(settings.BASE_DIR, 'original')
CAPTURED_PATH = os.path.join(settings.BASE_DIR, 'capture')
FACE_CASCADE = cv.CascadeClassifier("data/haarcascade_frontalface_alt.xml")
EYES_CASCADE = cv.CascadeClassifier("data/haarcascade_eye_tree_eyeglasses.xml")


def face_crop(image):
    face_data = os.path.join(settings.BASE_DIR, 'data', 'haarcascade_frontalface_default.xml')
    cascade = cv.CascadeClassifier(face_data)
    img = cv.imread(image)
    mini_size = (img.shape[1], img.shape[0])
    mini_frame = cv.resize(img, mini_size)
    faces = cascade.detectMultiScale(mini_frame)

    for f in faces:
        x, y, w, h = [v for v in f]
        cv.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255))

        sub_face = img[y:y + h, x:x + w]

        # Converts img array into grayscale
        gray_image = cv.cvtColor(sub_face, cv.COLOR_BGR2GRAY)

        # Converts np array back into image
        img = Image.fromarray(gray_image)

        # re-sizing to common dimension
        img = img.resize((150, 150), Image.ANTIALIAS)
    return img


def check_session(request):
    if 'username' in request.session and 'typ' in request.session and 'name' in request.session:
        context_data = dict()
        context_data['username'], context_data['typ'], context_data['name'] = request.session['username'], \
                                                                              request.session['typ'], request.session[
                                                                                  'name']
        if request.session['typ'] == 'Admin':
            context_data['permission'] = True
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


def upload_file(request, username):
    form = CapturedForm(request.POST, request.FILES)
    upload_path = CAPTURED_PATH + "/" + username + "/"

    if request.is_ajax():
        if form.is_valid():
            img_file = request.FILES['captured']
            ori_img_pth = ORIGINAL_UPLOAD_PATH + "/" + str(img_file)
            filename = img_file.name

            try:
                img = cv.imdecode(np.fromstring(img_file.read(), np.uint8), cv.IMREAD_UNCHANGED)
                gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                img_copy = copy.deepcopy(img)
                # Detect faces
                faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)
                if not faces.any():
                    return JsonResponse(
                        {'message': 'No face detect in your uploaded file. File not uploaded.', 'status': 00}
                        , status=200)

                for (x, y, w, h) in faces:
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    write = cv.imwrite(upload_path + filename, img_copy)
                    if not write:
                        return JsonResponse({'message': 'Unable to upload your file in our server.',
                                             'status': 00}, status=200)

            except Exception as e:
                print(e)
                return JsonResponse(
                    {'message': 'No face detect in your uploaded file. File not uploaded.', 'status': 00},
                    status=200)

            # Captured.objects.create(
            #     userid=Accounts.objects.filter(username=username)[0],
            #     captured=filename,
            #     file_path=upload_path
            # )

            return JsonResponse({'message': 'File successfully uploaded.', 'status': 11}, status=200)
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
        context_data = check_session(request)
        pk = kwargs['pk']
        acc_obj = get_object_or_404(Accounts, pk=pk)
        if context_data:
            if context_data.get('permission'):
                pass
            elif context_data['username'] == acc_obj.username:
                pass
            else:
                return render(request, template_name='403.html')

            context_data['uploader_username'] = acc_obj.username
            return render(request, template_name=self.template_name, context=context_data)
        else:
            return redirect('accounts:login')


class DeleteView(View):

    def get(self, request, pk):
        context_data = check_session(request)
        res = {
            'status': True
        }
        acc_obj = Accounts.objects.get(pk=pk)
        acc_obj.active = False
        acc_obj.save()
        post_data = request.GET
        if context_data.get('permission'):
            res['status'] = True
            return JsonResponse(res, status=200)
        else:
            res['status'] = 'unauthorized'
            return JsonResponse(res, status=200)


class LoginView(View):
    template_name = "accounts/login.html"
    model = Accounts

    def get_queryset(self, email, password):
        try:
            user = Accounts.objects.filter(email=email, active=1)
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
        context_data = check_session(request)
        if add_user.is_valid():
            new_user = add_user.save(commit=False)
            new_user.password = make_password(new_user.password)
            new_user.active = True
            new_user.save()
            context_data['new_userid'] = new_user.id
            pth = os.path.join(CAPTURED_PATH, new_user.username)
            if not os.path.isdir(pth):
                os.mkdir(pth, 0o666)
            return render(request, self.template_name, context_data)
        else:
            context_data['form'] = add_user
            return render(request, self.template_name, context_data)


class AllUserListView(View):
    template_name = "accounts/all_user.html"

    def get_queryset(self):
        try:
            obj = Accounts.objects.filter(active=True)
            return obj
        except Exception:
            return None

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            if context_data['typ'] == 'Admin':
                context_data['userobj'] = self.get_queryset()
                return render(request, self.template_name, context_data)
            else:
                return render(request, template_name='403.html')
        return redirect('accounts:login')


class UserListView(View):
    template_name = "accounts/profile.html"

    def get(self, request, pk):
        context_data = check_session(request)
        profile_obj = get_object_or_404(Accounts, id=pk)
        if context_data:
            if context_data.get('permission'):
                pass
            else:
                return render(request, template_name='403.html')

            context_data['profile_obj'] = profile_obj
            return render(request, self.template_name, context_data)

        return redirect('accounts:login')

    def post(self, request, pk):
        profile_obj = get_object_or_404(Accounts, id=pk)
        context_data = check_session(request)
        post_data = request.POST
        form = {
            "username": {
                "errors": ""
            },
            "type": {
                "errors": ""
            },
            "name": {
                "errors": ""
            },
            "password": {
                "errors": ""
            }
        }
        update_data = {}

        if post_data.get('username'):
            username = post_data['username']
            if len(username) > 255:
                form['username']['errors'] = 'Username cannot be greater than 255 characters'
                form['error'] = True
            username = username.replace(" ", "_")
            update_data['username'] = username

        if post_data.get('password'):
            password = post_data.get('password')
            if len(password) < 6:
                form['password']['errors'] = 'Minimum 6 characters required for password'
                form['error'] = True
            if len(password) > 48:
                form['password']['errors'] = 'Password cannot be greater than 48 characters'
                form['error'] = True
            update_data['password'] = make_password(password)

        if post_data.get('name'):
            name = post_data['name']
            if len(name) > 255:
                form['name']['errors'] = 'Name cannot be greater than 255 characters'
                form['error'] = True
            update_data['name'] = name

        if post_data.get('type'):
            typ = post_data['type']
            if typ not in ['Admin', 'Standard User']:
                form['type']['errors'] = "Only be admin and standard user types are allowed."
                form['error'] = True
            update_data['type'] = typ

        context_data['profile_obj'] = profile_obj
        context_data['form'] = form
        if form.get('error'):
            return render(request, self.template_name, context=context_data)
        try:
            update = Accounts.objects.filter(pk=pk).update(**update_data)
            context_data['update'] = update
            return render(request, self.template_name, context=context_data)
        except IntegrityError as e:
            form['username']['errors'] = 'Duplicate username not allowed.'
            form['error'] = True
            return render(request, self.template_name, context=context_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CaptureView(View):
    img_file_path = os.path.join(settings.BASE_DIR, "capture")
    count = 0

    def detect_and_capture(self, frame, count, pth):
        frame_gr = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_gray = cv.equalizeHist(frame_gr)

        # -- Detect Faces
        faces = FACE_CASCADE.detectMultiScale(frame_gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            frame2 = copy.deepcopy(frame)
            face_frame = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            face_roi = frame_gray[y:y + h, x:x + w]
            roi_color = face_frame[y:y + h, x:x + w]

            cv.imwrite(pth + "/" + str(self.count) + '.jpg', frame2)
            self.count += 1
            # -- In face, detect eyes
            eyes = EYES_CASCADE.detectMultiScale(face_roi)
            for (x2, y2, w2, h2) in eyes:
                cv.rectangle(roi_color, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)
            cv.putText(frame, "Capturing", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.65,
                       (0, 255, 0), 1)

            cv.waitKey(250)

    def get(self, request, username):
        cap = cv.VideoCapture(0)
        res = {}
        duration = 30
        if 'username' not in request.session:
            return JsonResponse({
                "msg": "You need to login first.",
                "status": 403
            }, status=200)

        store_pth = os.path.join(CAPTURED_PATH, username)

        if cap.isOpened():
            while True:
                start_time = datetime.now()
                diff = (datetime.now() - start_time).seconds  # converting into seconds
                while diff <= duration:
                    ret, frame = cap.read()
                    if frame is None:
                        return JsonResponse({
                            "msg": "No captured frame",
                            "status": 404
                        }, status=200)

                    self.detect_and_capture(frame, self.count, store_pth)

                    # cv.putText(frame, "press q to exit", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.65,
                    #            (0, 255, 0), 1)
                    cv.imshow('Create dataset', frame)
                    cv.waitKey(1)
                    diff = (datetime.now() - start_time).seconds
                    if self.count > 50:
                        break

                if self.count < 1:
                    res['msg'] = 'unable to capture your face. Timeout.'
                    res['status'] = 22

                cap.release()
                cv.destroyAllWindows()
                if res.get('status') != 22:
                    res['msg'] = 'Successfully captured your face.'
                    res['status'] = 11

                return JsonResponse(res, status=200)
        else:
            return JsonResponse({
                "msg": "camera not found, make sure camera is installed on your system",
                "status": 404
            }, status=200)
