import requests

from chatbot_app.models import ChatMessage, UserLocation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt

def get_client_ip(request):
    """
        Get IP address of user from the request
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# add to same file as get_client_ip(request)
def get_location_from_ip(ip):
    """
        Fetch Geolocation Data from IP
    """
    try:
        # using ipapi.co (free up to 1,000 requests/day)
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        data = response.json()
        return {
            "ip": ip,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude")
        }
    except Exception as e:
        print(f"Error occured in fetching IP address: {e}")
        return None
    

def save_user_location(request, user):
    """
        Save user location based on user IP
    """
    ip = get_client_ip(request)
    location_data = get_location_from_ip(ip)
    if location_data:
        UserLocation.objects.update_or_create(
            user=user,
            defaults={
                'ip_address': location_data['ip'],
                'city': location_data['city'],
                'region': location_data['region'],
                'country': location_data['country'],
                'latitude': location_data['latitude'],
                'longitude': location_data['longitude']
            }
        )



# wherever the user escalates to support (e.g. view)
def notify_support_of_unread(user_id):
    unread_count = ChatMessage.objects.filter(user_id=user_id, sender='user', has_read=False).count()
    channel_layer = get_channel_layer()
    print("unread_count", unread_count)
    async_to_sync(channel_layer.group_send)(
        "support_notifications",
        {
            'type': 'send_unread_update',
            'user_id': user_id,
            'unread_count': unread_count
        }
    )


def iframe_exempt(view_cls):
    """
        Decorator to apply xframe_options_exempt to class-based views so that.
        The view which uses this decorator can be embedded into html
    """
    decorator = method_decorator(xframe_options_exempt)
    view_cls.dispatch = decorator(view_cls.dispatch)
    return view_cls
