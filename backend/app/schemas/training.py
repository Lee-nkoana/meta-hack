# Training image Pydantic schemas for API validation
from marshmallow import Schema, fields, validate


class TrainingImageUploadSchema(Schema):
    """Schema for uploading training images (multipart form data)"""
    image_type = fields.Str(
        missing="printed",
        validate=validate.OneOf(["handwritten", "printed", "mixed"])
    )
    is_training_data = fields.Bool(missing=False, default=False)


class TrainingImageResponseSchema(Schema):
    """Schema for training image API responses"""
    id = fields.Int(required=True)
    user_id = fields.Int(allow_none=True)
    extracted_text = fields.Str(allow_none=True)
    corrected_text = fields.Str(allow_none=True)
    ocr_confidence = fields.Float(allow_none=True)
    image_type = fields.Str(required=True)
    is_training_data = fields.Bool(required=True)
    created_at = fields.DateTime()
    # Note: We don't return image_data by default to reduce payload size


class OCRResultSchema(Schema):
    """Schema for OCR extraction results"""
    extracted_text = fields.Str(allow_none=True)
    confidence = fields.Float(allow_none=True)
    medications_detected = fields.List(fields.Str())


class OCRFeedbackSchema(Schema):
    """Schema for submitting OCR corrections"""
    corrected_text = fields.Str(required=True)


class TrainingStatsSchema(Schema):
    """Schema for training statistics"""
    total_images = fields.Int(required=True)
    average_confidence = fields.Float(allow_none=True)
    images_corrected = fields.Int(required=True)
    by_type = fields.Dict(keys=fields.Str(), values=fields.Int())
