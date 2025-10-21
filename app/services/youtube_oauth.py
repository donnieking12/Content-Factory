"""
YouTube OAuth2 Service for Content Factory
Handles YouTube authentication and video uploads using OAuth2
"""
import os
import json
import pickle
from typing import Optional, Dict, Any
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.logging import logger


# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

# Token storage path
TOKEN_FILE = 'youtube_token.pickle'


class YouTubeOAuthService:
    """Service for handling YouTube OAuth2 authentication and uploads"""
    
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.youtube_service = None
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load existing credentials from token file"""
        token_path = Path(TOKEN_FILE)
        
        if token_path.exists():
            try:
                with open(token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
                logger.info("YouTube credentials loaded from token file")
            except Exception as e:
                logger.warning(f"Failed to load YouTube credentials: {e}")
                self.credentials = None
    
    def _save_credentials(self) -> None:
        """Save credentials to token file"""
        try:
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(self.credentials, token)
            logger.info("YouTube credentials saved to token file")
        except Exception as e:
            logger.error(f"Failed to save YouTube credentials: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with YouTube"""
        if not self.credentials:
            return False
        
        # Refresh token if expired
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self._save_credentials()
                logger.info("YouTube credentials refreshed")
            except Exception as e:
                logger.error(f"Failed to refresh YouTube credentials: {e}")
                return False
        
        return self.credentials and self.credentials.valid
    
    def get_auth_url(self, redirect_uri: Optional[str] = None) -> str:
        """
        Get the OAuth2 authorization URL for user to authenticate
        
        Args:
            redirect_uri: Optional custom redirect URI (auto-detected if not provided)
        
        Returns:
            Authorization URL for user to visit
        """
        client_secret_file = settings.YOUTUBE_CLIENT_SECRET_FILE
        
        if not os.path.exists(client_secret_file):
            raise FileNotFoundError(f"Client secret file not found: {client_secret_file}")
        
        # Auto-detect redirect URI if not provided
        if not redirect_uri:
            # Use environment variable or default to localhost
            base_url = os.getenv('APP_BASE_URL', 'http://localhost:8000')
            redirect_uri = f"{base_url}/api/v1/social-media/youtube/oauth2callback"
        
        flow = Flow.from_client_secrets_file(
            client_secret_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        logger.info(f"Generated YouTube OAuth authorization URL with redirect: {redirect_uri}")
        return auth_url
    
    def authenticate_with_code(self, code: str, redirect_uri: Optional[str] = None) -> bool:
        """
        Complete OAuth2 flow with authorization code
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Optional custom redirect URI (auto-detected if not provided)
            
        Returns:
            True if authentication successful
        """
        try:
            client_secret_file = settings.YOUTUBE_CLIENT_SECRET_FILE
            
            # Auto-detect redirect URI if not provided
            if not redirect_uri:
                base_url = os.getenv('APP_BASE_URL', 'http://localhost:8000')
                redirect_uri = f"{base_url}/api/v1/social-media/youtube/oauth2callback"
            
            flow = Flow.from_client_secrets_file(
                client_secret_file,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            
            flow.fetch_token(code=code)
            self.credentials = flow.credentials  # type: ignore
            self._save_credentials()
            
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}", exc_info=True)
            return False
    
    def get_youtube_service(self):
        """
        Get authenticated YouTube API service
        
        Returns:
            YouTube API service object
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated with YouTube. Please authenticate first.")
        
        if not self.youtube_service:
            self.youtube_service = build('youtube', 'v3', credentials=self.credentials)
        
        return self.youtube_service
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            category_id: YouTube category ID (default: 22 - People & Blogs)
            privacy_status: Privacy status (public, unlisted, private)
            tags: List of tags for the video
            
        Returns:
            Upload response with video ID and URL
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            youtube = self.get_youtube_service()
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            if tags:
                body['snippet']['tags'] = tags
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/*',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # Execute upload
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded successfully to YouTube: {video_url}")
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'response': response
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'details': e.error_details if hasattr(e, 'error_details') else None
            }
        except Exception as e:
            logger.error(f"Failed to upload video to YouTube: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user's YouTube channel
        
        Returns:
            Channel information
        """
        try:
            youtube = self.get_youtube_service()
            
            request = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                return {
                    'success': True,
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0)
                }
            else:
                return {
                    'success': False,
                    'error': 'No channel found for authenticated user'
                }
                
        except Exception as e:
            logger.error(f"Failed to get YouTube channel info: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
youtube_oauth_service = YouTubeOAuthService()
