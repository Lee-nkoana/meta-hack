# Medical record Marshmallow schemas
from marshmallow import Schema, fields, validate


class MedicalRecordBaseSchema(Schema):
    """Base medical record schema"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    original_text = fields.Str(required=True, validate=validate.Length(min=1))
    record_type = fields.Str(missing="doctor_note", default="doctor_note")


class MedicalRecordCreateSchema(MedicalRecordBaseSchema):
    """Schema for creating a new medical record"""
    pass


class MedicalRecordUpdateSchema(Schema):
    """Schema for updating a medical record"""
    title = fields.Str(allow_none=True, validate=validate.Length(min=1, max=200))
    original_text = fields.Str(allow_none=True, validate=validate.Length(min=1))
    record_type = fields.Str(allow_none=True)


class MedicalRecordResponseSchema(MedicalRecordBaseSchema):
    """Schema for medical record response"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    translated_text = fields.Str(allow_none=True)
    lifestyle_suggestions = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(allow_none=True, dump_only=True)


class MedicalRecordListSchema(Schema):
    """Schema for medical record list view (summary)"""
    id = fields.Int(dump_only=True)
    title = fields.Str()
    record_type = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    has_translation = fields.Bool(missing=False, default=False)
    has_suggestions = fields.Bool(missing=False, default=False)
