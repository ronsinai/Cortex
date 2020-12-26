from marshmallow import fields, Schema

class DiagnosisSchema(Schema):
    imagingId = fields.String(required=True)
    imagingType = fields.String(required=True)
    diagnosis = fields.String(required=True)
