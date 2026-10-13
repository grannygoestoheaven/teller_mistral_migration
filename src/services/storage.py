import os
import json
import random
import boto3

from pathlib import Path
from datetime import datetime
from scaleway import Client # or boto3 for AWS/S3
from botocore.client import Config
from src.config.settings import DATA_DIR

# --- Low-level clients ---
class LocalFileSystem:
    def upload_file(self, file_data, key):
        os.makedirs(os.path.dirname(str(DATA_DIR / key)), exist_ok=True)
        with open(str(DATA_DIR / key), "wb") as f:
            f.write(file_data)

    def download_file(self, key):
        with open(str(DATA_DIR / key), "rb") as f:
            return f.read()
    
    def generate_url(self, key):
        if key.startswith("stories/"):
            parts = key.split("/")
            story_name = parts[1]
            file_path = "/".join(parts[2:])
            return f"/api/speeches/{story_name}/{file_path}"
        elif key.startswith("audio/local_ambient_tracks/"):
            file_path = key.replace("audio/local_ambient_tracks/", "")
            return f"/api/tracks/{file_path}"
        else:
            return str(DATA_DIR / key)

    # def generate_url(self, key):
    #     return str(DATA_DIR / key)
    
    # def generate_url(self, key):
    #     if key.startswith("stories/"):
    #         return f"/api/stories/audio/{key.replace('stories/', '')}"
    #     elif key.startswith("audio/local_ambient_tracks/"):
    #         return f"/api/tracks/{key.replace('audio/local_ambient_tracks/', '')}"
    #     else:
    #         return str(DATA_DIR / key)
    
# class LocalFileSystem:
#     def upload_file(self, file_data, key):
#         os.makedirs(os.path.dirname(f"static/{key}"), exist_ok=True)
#         with open(f"static/{key}", "wb") as f:
#             f.write(file_data)
            
#     def download_file(self, key):
#         with open(f"static/{key}", "rb") as f:
#             return f.read()

#     def generate_url(self, key):
#         return f"/static/{key}"

class BucketClient:
    def __init__(self, settings):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.bucket_endpoint,
            aws_access_key_id=settings.bucket_access_key,
            aws_secret_access_key=settings.bucket_secret_key,
            config=Config(signature_version='s3v4'),
            region_name='fr-par'
        )
        self.bucket_name = settings.bucket_name
        print("Initializing this:", settings.bucket_endpoint),

    def upload_file(self, file_data, key):
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_data
        )

    def download_file(self, key):
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=key
        )
        return response['Body'].read()
    
    def generate_url(self, key):
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=3600
        )

# --- High-level backend ---
class StorageBackend:
    def __init__(self, use_bucket, settings=None):
        self.use_bucket = use_bucket
        print(f"StorageBackend initialized with use_bucket={use_bucket}")
        self.client = BucketClient(settings) if use_bucket else LocalFileSystem()
        self._tracks = []
        self._played_tracks = []
    
    # ==== STORING FUNCTIONS =====

    def save_txt_to_json_file(self, story_foldername, story_filename, story_title, tagged_story_for_tts, clean_story):
        payload = {
            "story_foldername" : story_foldername,
            "story_filename": story_filename,
            "story_title": story_title,
            "tagged_story_for_tts": tagged_story_for_tts,
            "clean_story": clean_story,
            "timestamp": datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        }
        key = f"stories/{story_foldername}/{story_filename}.json"
        print(f"Saving text to: {key}")
        self.client.upload_file(json.dumps(payload).encode('utf-8'), key)
        
        return self.client.generate_url(key)

    def save_mp3_speech_file(self, story_foldername: str, speech_filename: str, speech_audio: bytes) -> str:
        """
        Saves the speech mp3 audio content to a file in the specified directory.
        """
        key = f"stories/{story_foldername}/{speech_filename}"
        print(f"Saving mp3 file to: {key}")
        self.client.upload_file(speech_audio, key)
        
        return self.client.generate_url(key)

    # ==== FETCHING FUNCTIONS =====
    
    def get_clean_text_from_json_file(self, story_filename) -> str:
        """
        Extracts the cleaned story from the saved JSON file.
        """    
        key = f"stories/{story_filename}/{story_filename}.json"
        json_data = self.client.download_file(key)
        payload = json.loads(json_data)
        
        return payload["clean_story"]  # Return the actual text

    def get_tagged_text_from_json_file(self, story_filename) -> str:
        """
        Extracts the tagged story for TTS from the saved JSON file.
        """        
        key = f"stories/{story_filename}/{story_filename}.json"
        json_data = self.client.download_file(key)
        payload = json.loads(json_data)
        
        return payload["tagged_story_for_tts"]  # Return the actual tagged text
    
    def get_text_title_from_json_file(self, story_filename) -> str:
        """
        Returns clean title for a story from storage.
        """     
        key = f"stories/{story_filename}/{story_filename}.json"
        json_data = self.client.download_file(key)
        payload = json.loads(json_data)
        
        return payload["story_title"]  # Return the actual title
        
    def get_speech_url(self, story_filename: str) -> str:
        """
        Returns the speech URL for a story from storage.
        Returns None if the file does not exist.
        """
        key = f"stories/{story_filename}/{story_filename}.mp3"
        print(f"Retrieving filename from: {key}")
        
        file_path = str(DATA_DIR / key)
        
        # if not os.path.exists(file_path):
        #     print(f"Speech file not found: {file_path}")
        #     return None
    
        return self.client.generate_url(key)

    # ======= BACKGROUND TRACKS  =======

    def _initialize_tracks(self, tracks_dir):
        """List tracks from cloud storage or local filesystem"""
        if not self.use_bucket:
            # Local implementation
            self._tracks = [
                f.name for f in tracks_dir.iterdir()
                if f.suffix.lower() in (".mp3", ".wav", ".flac")
            ]
        else:
            # Cloud implementation - matches the bucket structure
            response = self.client.s3_client.list_objects(
                Bucket=self.client.bucket_name,
                Prefix="audio/local_ambient_tracks/"
            )
            print(response)
            self._tracks = [
                obj['Key'].split('/')[-1]  # Extracting just the filename
                for obj in response.get('Contents', [])
                if not obj['Key'].endswith('/')  # Skip directories
                and obj['Key'].endswith(('.mp3', '.wav', '.flac'))
            ]
            if 'Contents' not in response:
                print("No objects found or bucket/prefix does not exist.")
                self._tracks = []

        random.shuffle(self._tracks)

    def get_random_track_url(self, tracks_dir):
        """Generate URL for track"""
        if not self._tracks:
            self._initialize_tracks(tracks_dir)

        if not self._tracks:
            return None

        print (f"Available tracks: {self._tracks}")
        track_filename = self._tracks.pop(0)
        self._played_tracks.append(track_filename)

        if self.use_bucket:
            print(f"Generating URL for track: {track_filename}")
            return self.client.generate_url(f"audio/local_ambient_tracks/{track_filename}")
        else:
            # return f"DATA_DIR/audio/local_ambient_tracks/{track_filename}"
            return f"/api/tracks/{track_filename}"
