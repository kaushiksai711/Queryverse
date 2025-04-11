import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
from src.utils.logger import setup_logger
import base64
from io import BytesIO

class CloudinaryConnector:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = setup_logger("cloudinary_connector")
    
    def connect(self) -> bool:
        try:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            # Test the connection by getting account info
            cloudinary.api.ping()
            self.logger.info("Successfully connected to Cloudinary")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Cloudinary: {str(e)}")
            return False
    
    def upload_image(self, image_data: bytes, public_id: str, folder: str = "medical_images") -> Dict[str, Any]:
        """Upload an image to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                image_data,
                public_id=f"{folder}/{public_id}",
                resource_type="image"
            )
            self.logger.info(f"Successfully uploaded image: {result['public_id']}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to upload image: {str(e)}")
            raise
    
    def upload_test_image(self) -> Dict[str, Any]:
        """Upload a small test image to verify connection"""
        # Create a small test image (1x1 pixel)
        test_image = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
        return self.upload_image(test_image, "test_connection")
    
    def delete_image(self, public_id: str) -> bool:
        """Delete an image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            self.logger.info(f"Successfully deleted image: {public_id}")
            return result.get("result") == "ok"
        except Exception as e:
            self.logger.error(f"Failed to delete image: {str(e)}")
            return False
    
    def get_image_url(self, public_id: str, transformation: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for an image with optional transformations"""
        try:
            return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
        except Exception as e:
            self.logger.error(f"Failed to get image URL: {str(e)}")
            raise
    
    def search_images(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for images using tags or other metadata"""
        try:
            result = cloudinary.Search()\
                .expression(query)\
                .max_results(max_results)\
                .execute()
            return result
        except Exception as e:
            self.logger.error(f"Failed to search images: {str(e)}")
            raise 