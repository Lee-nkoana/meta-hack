# Medication Pydantic schemas for API validation
from marshmallow import Schema, fields
from datetime import datetime


class MedicationBaseSchema(Schema):
    """Base schema for medication data"""
    name = fields.Str(required=True)
    url = fields.Str(allow_none=True)
    uses = fields.Str(allow_none=True)
    side_effects = fields.Str(allow_none=True)
    discontinued = fields.Bool(missing=False, default=False)
    discontinuation_reason = fields.Str(allow_none=True)


class MedicationCreateSchema(MedicationBaseSchema):
    """Schema for creating a medication"""
    pass


class MedicationResponseSchema(MedicationBaseSchema):
    """Schema for medication API responses"""
    id = fields.Int(required=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime(allow_none=True)


class MedicationSearchResponseSchema(Schema):
    """Simplified schema for search results"""
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    uses = fields.Str(allow_none=True)
    discontinued = fields.Bool(required=True)


class MedicationListResponseSchema(Schema):
    """Schema for paginated medication list"""
    medications = fields.List(fields.Nested(MedicationSearchResponseSchema))
    total = fields.Int(required=True)
    skip = fields.Int(required=True)
    limit = fields.Int(required=True)
