import requests

from chatbot_app.models import UserLocation


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