# from rest_framework import permissions
#
# from user_management.models import UserProfile
#
#
# class ReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.method in permissions.SAFE_METHODS
#
#
# class IsFounder(permissions.BasePermission):
#     """
#         Custom permission to only allow owners of an object to edit it
#     """
#
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         obj = UserProfile.objects.get(user=request.user)
#         return obj.is_founder
#
#
# class IsInvestor(permissions.BasePermission):
#     """
#        Custom permission to only allow owners of an object to edit it
#     """
#
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         obj = UserProfile.objects.get(user=request.user)
#         return obj.is_investor
#
#
# class IsMatchCardFundOrReadOnly(permissions.BasePermission):
#     """
#         Custom permission to only allow owners of an object to edit it
#     """
#
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         return request.user.profile.is_investor
#
#     def has_object_permission(self, request, view, obj):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         return obj.investor.user == request.user
#
#
# class IsFounderOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         if request.method in ['GET']:
#             return request.user
#         return request.user.profile.is_founder
#
#
# class IsAuthOrPatchOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         if request.method in ['PATCH']:
#             return True
#         return bool(request.user and request.user.is_authenticated)
#
#
# class IsAccelerator(permissions.BasePermission):
#     """
#         Custom permission to only allow owners of an object to edit it
#     """
#
#     def has_permission(self, request, view):
#         """
#         Return `True` if permission is granted, `False` otherwise.
#         """
#         return request.user.profile.is_accelerator
