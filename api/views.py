from django.contrib.auth import logout
from django.http import JsonResponse, Http404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TasksSerializer, TaskDetailSerializer, TaskCreateSerializer, ChangePasswordSerializer
from tasks.models import Tasks
from tasks.tasks import send_email_task_done, send_email_task_not_done
from users.models import User
from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView


@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Todo' : '/todo/',
        'Todo Detail' : '/todo/<str:pk>/',
        'Todo Create' : '/todo-create/',
        'Todo Update' : '/todo-update/<str:pk>/',
        'Todo Delete' : '/todo-delete/<str:pk>/',
        'Todo Is DONE': '/todo/<str:pk>/execute/',
        'Todo Is Not DONE': '/todo/<str:pk>/notexecute/',
    }
    return Response(api_urls)

@api_view(['GET'])
def taskList(request):
    task = Tasks.objects.filter(creator=request.user.id)
    serializer = TasksSerializer(task, many = True).data
    return Response(serializer)

@api_view(['GET'])
def taskDetail(request, pk):
    task = Tasks.objects.get(id=pk)
    if task.creator != request.user:
        return Response("No such Task")
    serializer = TaskDetailSerializer(task, many = False).data
    return Response(serializer)


@api_view(['POST'])
def taskCreate(request):
    serializer = TaskCreateSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save(creator=request.user)
        return Response("Taks created successfully.")
    return Response(serializer.data)

@api_view(['DELETE'])
def taskDelete(request, pk):
    task = Tasks.objects.get(id = pk)
    if task.creator != request.user:
        return Response("No such Task")
    task.delete()
    return Response("Taks deleted successfully.")


@api_view(['PATCH'])
def taskUpdate(request, pk):
    task = Tasks.objects.get(id = pk)
    serializer = TaskDetailSerializer(instance=task, data=request.data, partial=True)
    if task.creator != request.user:
        raise Http404(
                ("You don't own this object")
            )
    if serializer.is_valid():
        serializer.save()


    return Response(serializer.data)



@api_view(['POST'])
def taskMakeDone(request, pk):
    task = Tasks.objects.get(id=pk)
    serializer = TaskDetailSerializer(task, data={'is_done': True}, partial=True)
    if task.creator != request.user:
        raise Http404(
                ("You don't own this object")
            )
    if serializer.is_valid():
        serializer.save()
        send_email_task_done(request.user.email)
    return Response(serializer.data)



@api_view(['POST'])
def taskMakeNotDone(request, pk):
    task = Tasks.objects.get(id=pk)
    serializer = TaskDetailSerializer(task, data={'is_done': False}, partial=True)
    if task.creator != request.user:
        raise Http404(
                ("You don't own this object")
            )
    if serializer.is_valid():
        serializer.save()
        send_email_task_not_done(request.user.email)
    return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)