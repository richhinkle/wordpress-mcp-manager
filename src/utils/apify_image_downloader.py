"""
Use Apify to download Instagram images that are blocked by Instagram's CDN
"""
import requests
import os
import logging
from typing import Optional, Tuple
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class ApifyImageDownloader:
    """Download Instagram images using Apify's infrastructure to bypass restrictions"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })
    
    def download_instagram_image(self, image_url: str, output_path: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download Instagram image using Apify's web scraper to bypass CDN restrictions
        
        Args:
            image_url: Instagram image URL
            output_path: Optional path to save the image
            
        Returns:
            (success, file_path, error_message)
        """
        try:
            # Use Apify's Web Scraper to download the image
            actor_input = {
                "startUrls": [{"url": image_url}],
                "linkSelector": "",
                "pageFunction": """
                    async function pageFunction(context) {
                        const { page, request } = context;
                        
                        // Wait for the image to load
                        await page.waitForTimeout(2000);
                        
                        // Get the image as base64
                        const imageBase64 = await page.evaluate(async (url) => {
                            return new Promise((resolve, reject) => {
                                const img = new Image();
                                img.crossOrigin = 'anonymous';
                                img.onload = function() {
                                    const canvas = document.createElement('canvas');
                                    const ctx = canvas.getContext('2d');
                                    canvas.width = this.width;
                                    canvas.height = this.height;
                                    ctx.drawImage(this, 0, 0);
                                    resolve(canvas.toDataURL('image/jpeg', 0.9));
                                };
                                img.onerror = reject;
                                img.src = url;
                            });
                        }, request.url);
                        
                        return {
                            url: request.url,
                            imageData: imageBase64,
                            success: true
                        };
                    }
                """,
                "proxyConfiguration": {
                    "useApifyProxy": True
                }
            }
            
            # Start the web scraper
            run_response = self._start_actor_run('apify/web-scraper', actor_input)
            run_id = run_response['data']['id']
            
            logger.info(f"Started Apify image download run: {run_id}")
            
            # Wait for completion
            results = self._wait_for_completion(run_id, timeout=60)
            
            if not results or not results[0].get('imageData'):
                return False, None, "No image data returned from Apify"
            
            # Decode base64 image data
            image_data_b64 = results[0]['imageData']
            if image_data_b64.startswith('data:image'):
                # Remove data URL prefix
                image_data_b64 = image_data_b64.split(',')[1]
            
            import base64
            image_data = base64.b64decode(image_data_b64)
            
            # Save to file
            if not output_path:
                # Create temporary file
                temp_dir = Path(tempfile.gettempdir()) / "apify_images"
                temp_dir.mkdir(exist_ok=True)
                output_path = temp_dir / f"instagram_image_{hash(image_url)}.jpg"
            
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Successfully downloaded Instagram image via Apify: {output_path}")
            return True, str(output_path), None
            
        except Exception as e:
            logger.error(f"Apify image download failed: {e}")
            return False, None, str(e)
    
    def _start_actor_run(self, actor_id: str, actor_input: dict) -> dict:
        """Start an Apify actor run"""
        url = f"{self.base_url}/acts/{actor_id}/runs"
        response = self.session.post(url, json=actor_input)
        response.raise_for_status()
        return response.json()
    
    def _wait_for_completion(self, run_id: str, timeout: int = 60) -> list:
        """Wait for actor run completion and return results"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check status
            status_url = f"{self.base_url}/actor-runs/{run_id}"
            status_response = self.session.get(status_url)
            status_response.raise_for_status()
            
            run_data = status_response.json()['data']
            status = run_data['status']
            
            if status == 'SUCCEEDED':
                # Get results
                results_url = f"{self.base_url}/actor-runs/{run_id}/dataset/items"
                results_response = self.session.get(results_url)
                results_response.raise_for_status()
                return results_response.json()
            
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                raise Exception(f"Actor run {status}: {run_data.get('statusMessage', 'Unknown error')}")
            
            time.sleep(5)
        
        raise Exception(f"Actor run timed out after {timeout} seconds")