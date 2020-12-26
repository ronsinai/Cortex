from marshmallow import fields, INCLUDE, Schema

class MetadataSchema(Schema):
    age = fields.Integer(required=True)
    sex = fields.String(required=True)

class ImagingSchema(Schema):
    _id = fields.String(required=True)
    type = fields.String(required=True)
    bodyPart = fields.String(required=True)
    metadata = fields.Nested(MetadataSchema(unknown=INCLUDE), required=True)
    path = fields.String(required=True)
