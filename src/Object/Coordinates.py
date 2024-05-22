import json
class Coordinates:
    def __init__(self, id,partNo,typeID,sampleID,topLeft,bottomRight,angle,threshold):
        self.id = id
        self.partNo = partNo
        self.typeID = typeID
        self.sampleID = sampleID
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.angle = angle
        self.threshold = threshold
    
# Custom serialization function for the Coordinates class
def serialize_coordinates(obj):
    if isinstance(obj, Coordinates):
        return {
            "id": obj.id,
            "partNo": obj.partNo,
            "typeID": obj.typeID,
            "sampleID": obj.sampleID,
            "topLeft": obj.topLeft,
            "bottomRight": obj.bottomRight,
            "threshold": obj.threshold,
            "angle":obj.angle
        }
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))
   