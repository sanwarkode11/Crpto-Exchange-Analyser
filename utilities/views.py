# # Create your views here.
#
# from rest_framework import views, status, pagination
# from rest_framework.exceptions import ParseError
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
#
# # from pollinate import constants
# from utilities.models import compressImage
# from utilities.storage_backends import publicMediaStorage
#
#
# # add below in urls
# # url(r'/api/v1/upload/(?P<filename>[^/]+)$', FileUploadView.as_view())
# class FileUploadView(views.APIView):
#     parser_classes = (MultiPartParser, FormParser)
#
#     def put(self, request, filename, format=None):
#         if 'file' not in request.data:
#             raise ParseError("Please send a file")
#
#         file = request.data['file']
#         file = compressImage(file)
#         file_name = publicMediaStorage.save(filename, file)
#
#         return Response(status=status.HTTP_201_CREATED, data={"file_url": publicMediaStorage.url(file_name)},
#                         content_type="application/json")
#
#
# class GeneralPagination(pagination.PageNumberPagination):
#     page_size = 20
#     page_size_query_param = 'page_size'
#     max_page_size = 1000


# class VersionViewSet(views.APIView):
#     permission_classes = []
#
#     def get(self, request):
#         return Response(constants.UPDATE_VERSION_DATA)
