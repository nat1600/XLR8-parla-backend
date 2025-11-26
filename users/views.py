from django.shortcuts import render
from django.conf import settings
import requests

# Django REST framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import User
from rest_framework.authtoken.models import Token


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_callback(request):
	"""Accepts a Google id_token (credential) from the frontend, verifies it
	with Google's tokeninfo endpoint, then creates/returns a DRF token.
	"""
	id_token = request.data.get('credential')
	if not id_token:
		return Response({'detail': 'Missing credential'}, status=status.HTTP_400_BAD_REQUEST)

	# Verify token with Google
	try:
		resp = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': id_token}, timeout=5)
	except requests.RequestException:
		return Response({'detail': 'Error verifying token with Google'}, status=status.HTTP_502_BAD_GATEWAY)

	if resp.status_code != 200:
		return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

	token_info = resp.json()

	# Confirm audience (client id)
	expected_aud = None
	try:
		expected_aud = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
	except Exception:
		expected_aud = getattr(settings, 'GOOGLE_CLIENT_ID', None)

	if expected_aud and token_info.get('aud') != expected_aud:
		return Response({'detail': 'Invalid token audience'}, status=status.HTTP_400_BAD_REQUEST)

	google_id = token_info.get('sub')
	email = token_info.get('email')
	name = token_info.get('name') or request.data.get('name')
	picture = token_info.get('picture') or request.data.get('picture')

	if not email:
		return Response({'detail': 'Email not available from Google token'}, status=status.HTTP_400_BAD_REQUEST)

	# Find existing user by google_id or email
	user = None
	if google_id:
		user = User.objects.filter(google_id=google_id).first()
	if not user:
		user = User.objects.filter(email=email).first()

	# Create a new user if none exists
	if not user:
		base_username = email.split('@')[0]
		username = base_username
		i = 1
		while User.objects.filter(username=username).exists():
			username = f"{base_username}{i}"
			i += 1

		user = User.objects.create_user(username=username, email=email)

	# Update fields
	if google_id:
		user.google_id = google_id
	if picture:
		user.profile_picture = picture
	if name and not user.get_full_name():
		# set first_name/last_name heuristically
		parts = name.split(' ', 1)
		user.first_name = parts[0]
		if len(parts) > 1:
			user.last_name = parts[1]

	user.save()

	# Create or get token
	token_obj, _ = Token.objects.get_or_create(user=user)

	return Response({
		'token': token_obj.key,
		'user': {
			'email': user.email,
			'name': user.get_full_name() or name,
			'picture': user.profile_picture,
		}
	}, status=status.HTTP_200_OK)
