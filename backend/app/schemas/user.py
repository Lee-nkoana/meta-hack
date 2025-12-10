# User Marshmallow schemas for validation and serialization
from marshmallow import Schema, fields, validate, ValidationError


class UserBaseSchema(Schema):
    """Base user schema"""
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    full_name = fields.Str(allow_none=True)


class UserCreateSchema(UserBaseSchema):
    """Schema for user registration"""
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100), load_only=True)


class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserResponseSchema(UserBaseSchema):
    """Schema for user response (public info)"""
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserProfileSchema(UserResponseSchema):
    """Schema for detailed user profile"""
    updated_at = fields.DateTime(allow_none=True, dump_only=True)
    record_count = fields.Int(missing=0, default=0)


class UserUpdateSchema(Schema):
    """Schema for updating user profile"""
    email = fields.Email(allow_none=True)
    full_name = fields.Str(allow_none=True)
    password = fields.Str(allow_none=True, validate=validate.Length(min=6, max=100), load_only=True)
