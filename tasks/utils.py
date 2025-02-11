# tasks/utils.py

import requests
from django.conf import settings
from social_django.models import UserSocialAuth

def verify_social_action(user, task):
    try:
        if task.platform == 'facebook':
            return verify_facebook_action(user, task)
        elif task.platform == 'twitter':
            return verify_twitter_action(user, task)
        elif task.platform == 'instagram':
            return verify_instagram_action(user, task)
        return False
    except Exception:
        return False

def verify_facebook_action(user, task):
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='facebook')
        access_token = social_auth.extra_data['access_token']
        
        if task.task_type == 'like':
            response = requests.get(
                f'https://graph.facebook.com/{task.content_id}/likes',
                params={
                    'access_token': access_token,
                    'summary': 'true'
                }
            )
            data = response.json()
            return data.get('summary', {}).get('has_liked', False)
            
        elif task.task_type == 'follow':
            response = requests.get(
                f'https://graph.facebook.com/me/following/{task.content_id}',
                params={'access_token': access_token}
            )
            return response.status_code == 200
            
    except Exception:
        return False

def verify_twitter_action(user, task):
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='twitter')
        access_token = social_auth.extra_data['access_token']
        
        headers = {
            'Authorization': f'Bearer {settings.TWITTER_BEARER_TOKEN}'
        }
        
        if task.task_type == 'like':
            response = requests.get(
                f'https://api.twitter.com/2/tweets/{task.content_id}/liking_users',
                headers=headers
            )
            data = response.json()
            return str(user.profile.twitter_id) in [u['id'] for u in data.get('data', [])]
            
        elif task.task_type == 'follow':
            response = requests.get(
                f'https://api.twitter.com/2/users/{task.content_id}/followers',
                headers=headers
            )
            data = response.json()
            return str(user.profile.twitter_id) in [u['id'] for u in data.get('data', [])]
            
    except Exception:
        return False

def verify_instagram_action(user, task):
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='instagram')
        access_token = social_auth.extra_data['access_token']
        
        if task.task_type == 'like':
            response = requests.get(
                f'https://graph.instagram.com/{task.content_id}/likes',
                params={'access_token': access_token}
            )
            data = response.json()
            return user.profile.instagram_id in [like['id'] for like in data.get('data', [])]
            
        elif task.task_type == 'follow':
            response = requests.get(
                f'https://graph.instagram.com/me/following',
                params={'access_token': access_token}
            )
            data = response.json()
            return task.content_id in [follow['id'] for follow in data.get('data', [])]
            
    except Exception:
        return False