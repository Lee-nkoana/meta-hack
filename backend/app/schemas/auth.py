# Authentication Marshmallow schemas
from marshmallow import Schema, fields


class TokenSchema(Schema):
    """Schema for JWT token response"""
    access_token = fields.Str(required=True)
    token_type = fields.Str(missing="bearer", default="bearer")


class TokenDataSchema(Schema):
    """Schema for token payload data"""
    username = fields.Str(allow_none=True)
    user_id = fields.Int(allow_none=True)
