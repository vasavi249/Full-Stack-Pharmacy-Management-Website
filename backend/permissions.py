from django.http import JsonResponse
from functools import wraps
from authentication import login_required

def admin_required(view_func):
    """Decorator to require admin role."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request, 'user_role') and request.user_role == 'admin':
            return view_func(request, *args, **kwargs)
        return JsonResponse({'error': 'Forbidden, admin access required'}, status=403)
    return _wrapped_view
