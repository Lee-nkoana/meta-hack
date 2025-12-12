# OCR Service for extracting text from medical images
import base64
import io
from typing import Optional, Dict, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Placeholder for pytesseract - will be imported after package installation
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None


class OCRService:
    """Service for OCR text extraction from medical images"""
    
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        if not self.tesseract_available:
            print("Warning: pytesseract not installed. OCR features will be limited.")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Enhance contrast
        - Remove noise
        - Sharpen
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        # Apply median filter to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def extract_text_from_image(self, image_b64: str) -> Tuple[Optional[str], float]:
        """
        Extract text from base64 encoded image
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.tesseract_available:
            return ("OCR service unavailable. Please install pytesseract.", 0.0)
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(processed_image)
            
            # Get confidence data
            confidence = self._get_confidence_score(processed_image)
            
            return (extracted_text.strip(), confidence)
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return (None, 0.0)
    
    def _get_confidence_score(self, image: Image.Image) -> float:
        """
        Get OCR confidence score from image
        
        Returns:
            Average confidence score (0.0 - 1.0)
        """
        if not self.tesseract_available:
            return 0.0
        
        try:
            # Get detailed OCR data with confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence (excluding -1 values which indicate no text)
            confidences = [float(conf) for conf in data['conf'] if int(conf) != -1]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                return avg_confidence / 100.0  # Convert to 0.0 - 1.0 range
            return 0.0
            
        except Exception as e:
            print(f"Confidence calculation error: {e}")
            return 0.0
    
    def extract_with_layout(self, image_b64: str) -> Dict:
        """
        Extract text while preserving document layout
        
        Returns:
            Dictionary with text organized by blocks/lines
        """
        if not self.tesseract_available:
            return {"error": "OCR service unavailable"}
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Organize by blocks
            blocks = {}
            for i, text in enumerate(data['text']):
                if text.strip():
                    block_num = data['block_num'][i]
                    if block_num not in blocks:
                        blocks[block_num] = []
                    blocks[block_num].append({
                        'text': text,
                        'conf': float(data['conf'][i]) / 100.0,
                        'left': data['left'][i],
                        'top': data['top'][i]
                    })
            
            return {
                'blocks': blocks,
                'full_text': pytesseract.image_to_string(processed_image).strip()
            }
            
        except Exception as e:
            print(f"Layout extraction error: {e}")
            return {"error": str(e)}


# Create singleton instance
ocr_service = OCRService()
