import os
import sys
import boto3
import yt_dlp
from botocore.exceptions import ClientError

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Title: {info['title']}")
            print(f"Views: {info['view_count']}")
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

def upload_to_s3(file_path, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.client('s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    )
    try:
        s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False
    return True

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=_odcrBrvxdY&ab_channel=TopNotchProgrammer"
    output_path = "/tmp"
    s3_bucket = "ytdownloaderdocker"

    print("Downloading video...")
    video_filename = download_youtube_video(video_url, output_path)
    
    if video_filename:
        print(f"Video downloaded: {video_filename}")
        
        print("Uploading to S3...")
        if upload_to_s3(video_filename, s3_bucket):
            print(f"Video uploaded to S3 bucket: {s3_bucket}")
        else:
            print("Failed to upload video to S3")
    else:
        print("Failed to download video")

    # Print environment variables for debugging (remove in production)
    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        if key.startswith('AWS'):
            print(f"{key}: {'*' * len(value)}")  # Mask the actual values
        else:
            print(f"{key}: {value}")
