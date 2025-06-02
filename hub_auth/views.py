from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HomeView(APIView):
    def get(self, request):
        """
        This is a simple test view

        It serves as a simple example of what subsequent views will look like
        Custom classes for response and error handlilng will be introduced as we progress
        """
        return Response({'message': 'Hello World!'})
    