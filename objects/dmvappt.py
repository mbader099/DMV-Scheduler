import json
import datetime


def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d %I:%M%p')
    else:
        return value.__dict__


class DMVAppt:
    def __init__(self, startDateTime, duration, locId, categoryId, categoryName, apptTypeId, apptTypeName, apptTypeDesc):
        self.startDateTime = startDateTime
        self.duration = duration
        self.locId = locId
        self.categoryId = categoryId
        self.categoryName = categoryName
        self.apptTypeId = apptTypeId
        self.apptTypeName = apptTypeName
        self.apptTypeDesc = apptTypeDesc

    def toJSON(self):
        return json.dumps(self, default=json_default, sort_keys=True, indent=4)
