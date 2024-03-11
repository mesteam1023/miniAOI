class SampleDetect:
    def __init__(self,Id,partNo,typeID,sampleID,topLeft,bottomRight):
        self.Id = Id
        self.partNo = partNo
        self.typeID = typeID
        self.sampleID = sampleID
        self.topLeft = topLeft
        self.bottomRight = bottomRight

# Custom serialization function for the SampleDetect class
def serialize_sample_detect(obj):
    if isinstance(obj, SampleDetect):
        return {
            "Id": obj.Id,
            "partNo": obj.partNo,
            "typeID": obj.typeID,
            "sampleID": obj.sampleID,
            "topLeft": obj.topLeft,
            "bottomRight": obj.bottomRight,
            "coordinates_list": obj.coordinates_list
        }
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))
