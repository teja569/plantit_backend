"""
Plant identification service using Google Gemini API
"""
import os
import io
from typing import Dict, Optional
from PIL import Image
from app.core.config import settings
from app.core.logging import logger

# Optional google-generativeai import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    logger.warning("Google Generative AI not available - install google-generativeai package")


class PlantClassifier:
    """Plant identification using Google Gemini Vision API"""
    
    def __init__(self):
        self.model = None
        self.client = None
        self.model_name = None  # Cache selected model name
        self._initialized = False
        self.initialize_gemini()
    
    def initialize_gemini(self):
        """Initialize Gemini API client"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini API not available")
            return
        
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set - plant identification will not work")
            return
        
        try:
            genai.configure(api_key=settings.gemini_api_key)
            
            # List available models and find the best one for image analysis
            try:
                available_models = list(genai.list_models())
                logger.info(f"Found {len(available_models)} total models from API")
                
                # Filter models that support generateContent (required for image analysis)
                vision_capable = []
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        model_name = model.name.split('/')[-1]  # Get just the model name
                        # Prioritize models that support vision/image analysis
                        # Check input token limits (vision models typically have higher limits)
                        input_token_limit = getattr(model, 'input_token_limit', 0)
                        
                        vision_capable.append({
                            'name': model_name,
                            'full_name': model.name,
                            'input_tokens': input_token_limit,
                            'priority': self._get_model_priority(model_name, input_token_limit)
                        })
                
                # Sort by priority (higher is better) and input token limit
                vision_capable.sort(key=lambda x: (x['priority'], x['input_tokens']), reverse=True)
                
                logger.info(f"Found {len(vision_capable)} vision-capable models")
                if vision_capable:
                    logger.info(f"Top models: {[m['name'] for m in vision_capable[:5]]}")
                
                # Try models in priority order
                model_names = [m['name'] for m in vision_capable] if vision_capable else []
                
            except Exception as e:
                logger.warning(f"Could not list models from API: {e}. Using fallback model names.")
                model_names = []
            
            # Add fallback model names (without -latest suffix, as v1beta doesn't support it)
            fallback_models = [
                'gemini-1.5-flash',      # Flash model (fast, good for images)
                'gemini-1.5-pro',        # Pro model (better accuracy)
                'gemini-pro-vision',      # Legacy vision model
                'gemini-pro',             # Basic model
            ]
            
            # Combine lists, avoiding duplicates (prioritize API-listed models)
            all_models = model_names + [m for m in fallback_models if m not in model_names]
            
            self.model = None
            last_error = None
            selected_model = None
            
            for model_name in all_models:
                try:
                    test_model = genai.GenerativeModel(model_name)
                    # Verify model is accessible
                    selected_model = model_name
                    self.model = test_model
                    logger.info(f"Successfully initialized Gemini model for image analysis: {model_name}")
                    break
                except Exception as e:
                    last_error = e
                    logger.debug(f"Failed to initialize {model_name}: {e}")
                    continue
            
            if self.model is None:
                logger.error(f"Failed to initialize any Gemini model. Last error: {last_error}")
                logger.error("Please check your API key and available models at https://aistudio.google.com/app/apikey")
                self.model = None
                self._initialized = False
            else:
                self.model_name = selected_model
                self._initialized = True
                logger.info(f"Using model '{selected_model}' for plant image analysis")
                
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.model = None
            self._initialized = False
    
    def _get_model_priority(self, model_name: str, input_tokens: int) -> int:
        """Calculate priority score for model selection (higher = better)"""
        priority = 0
        model_lower = model_name.lower()
        
        # Prefer flash models (faster, good for images)
        if 'flash' in model_lower:
            priority += 100
        # Prefer pro models (better accuracy)
        elif 'pro' in model_lower:
            priority += 80
        # Legacy vision models
        elif 'vision' in model_lower:
            priority += 60
        
        # Prefer 1.5+ models (newer, better)
        if '1.5' in model_lower or '2.0' in model_lower or '2.5' in model_lower:
            priority += 50
        
        # Prefer models with higher token limits (better for images)
        if input_tokens > 1000000:  # 1M+ tokens
            priority += 30
        elif input_tokens > 100000:  # 100K+ tokens
            priority += 20
        
        # Avoid preview/experimental models
        if 'preview' in model_lower or 'experimental' in model_lower:
            priority -= 10
        
        return priority
    
    def predict(self, image: Image.Image) -> Dict[str, any]:
        """
        Predict plant type from image using Gemini API
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with is_plant, plant_type, and confidence
        """
        # Re-initialize if needed (for serverless cold starts)
        if not self._initialized and settings.gemini_api_key:
            logger.info("Re-initializing Gemini model (cold start)")
            self.initialize_gemini()
        
        if not self.model:
            logger.error("Gemini model not initialized")
            return {
                "is_plant": False,
                "plant_type": "Error: Gemini API not configured",
                "confidence": 0.0
            }
        
        try:
            # Convert PIL Image to bytes
            img_bytes = io.BytesIO()
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Prepare the prompt for plant identification
            prompt = """Analyze this image and identify if it contains a plant. 
If it is a plant, provide the common name and scientific name (if known) of the plant.
Respond in the following JSON format:
{
    "is_plant": true/false,
    "plant_name": "Common name of the plant",
    "scientific_name": "Scientific name (if known, otherwise null)",
    "confidence": 0.0-1.0
}

If it's not a plant, respond with:
{
    "is_plant": false,
    "plant_name": "Not a plant",
    "scientific_name": null,
    "confidence": 0.0
}

Be specific and accurate. Only identify if you're confident it's a plant."""
            
            # Call Gemini API with image
            # Use the correct format for Gemini Vision API
            import google.generativeai as genai
            
            # Prepare image data
            image_data = img_bytes.getvalue()
            
            # Create image part for Gemini Vision API
            # The API accepts image as a dict with mime_type and data
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            # Generate content with both prompt and image
            # Pass as a list: [prompt, image_part]
            response = self.model.generate_content([prompt, image_part])
            
            # Parse response
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            # Gemini might return text with JSON, so we need to extract it
            import json
            import re
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the whole response
                try:
                    result = json.loads(response_text)
                except:
                    # Fallback: parse text response
                    result = self._parse_text_response(response_text)
            
            # Map to expected format
            plant_name = result.get("plant_name", "Unknown")
            is_plant = result.get("is_plant", False)
            confidence = float(result.get("confidence", 0.5 if is_plant else 0.0))
            
            logger.info(f"Gemini prediction: {plant_name} (is_plant: {is_plant}, confidence: {confidence})")
            
            return {
                "is_plant": is_plant,
                "plant_type": plant_name,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Gemini prediction failed: {e}")
            return {
                "is_plant": False,
                "plant_type": f"Error: {str(e)}",
                "confidence": 0.0
            }
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response from Gemini if JSON parsing fails"""
        text_lower = text.lower()
        
        # Check if it says it's a plant
        is_plant = any(word in text_lower for word in ["plant", "flower", "tree", "herb", "shrub"])
        
        # Try to extract plant name (first capitalized words)
        import re
        # Look for common patterns like "This is a [Plant Name]"
        name_match = re.search(r'(?:is|are|this is|this appears to be|identified as)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
        plant_name = name_match.group(1) if name_match else "Unknown Plant"
        
        return {
            "is_plant": is_plant,
            "plant_name": plant_name if is_plant else "Not a plant",
            "scientific_name": None,
            "confidence": 0.7 if is_plant else 0.3
        }


# Global classifier instance
plant_classifier = PlantClassifier()
