import json
from django.utils.deprecation import MiddlewareMixin
from utils import decode_jwt

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Middleware to parse JWT and attach user info to request (optional global approach)."""
    
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = decode_jwt(token)
            if payload:
                from db import users_collection
                from bson import ObjectId
                from django.http import JsonResponse
                
                user_id = payload.get('user_id')
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                
                if user and user.get('status') == 'blocked':
                    return JsonResponse({'error': 'Your account has been blocked'}, status=403)
                    
                request.user_id = user_id
                request.user_role = payload.get('role')
        
        # Parse JSON body automatically if content type is application/json
        if request.content_type == 'application/json' and request.body:
            try:
                request.json = json.loads(request.body)
            except json.JSONDecodeError:
                request.json = {}
        else:
            request.json = {}
