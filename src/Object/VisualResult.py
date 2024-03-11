class VisualData:
    def __init__(self, top_left, bottom_right, check_type, result, final_result_image, checking_content):
        self.TopLeft = top_left
        self.BottomRight = bottom_right
        self.CheckType = check_type
        self.Result = result
        self.FinalResultImage = final_result_image
        self.CheckingContent = checking_content

class CheckStep:
    def __init__(self, step_name, step_result, step_coordinate):
        self.StepName = step_name
        self.StepResult = step_result
        self.StepCoordinate = step_coordinate

class VisualInspection:
    def __init__(self, barcode, status, order_no, line, result_data):
        self.Barcode = barcode
        self.Status = status
        self.OrderNo = order_no
        self.Line = line
        self.ResultData = result_data

def serialize_visual_data(obj):
    if isinstance(obj, VisualData):
        return {
            "TopLeft": obj.TopLeft,
            "BottomRight": obj.BottomRight,
            "CheckType": obj.CheckType,
            "Result": obj.Result,
            "FinalResultImage": obj.FinalResultImage,
            "CheckingContent": obj.CheckingContent
        }
    elif isinstance(obj, list):
        return [serialize_visual_data(item) for item in obj]
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))

def serialize_check_step(obj):
    if isinstance(obj, CheckStep):
        return {
            "StepName": obj.StepName,
            "StepResult": obj.StepResult,
            "StepCoordinate": obj.StepCoordinate
        }
    elif isinstance(obj, list):
        return [serialize_check_step(item) for item in obj]
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))

def serialize_visual_inspection(obj):
    if isinstance(obj, VisualInspection):
        return {
            "Barcode": obj.Barcode,
            "Status": obj.Status,
            "OrderNo": obj.OrderNo,
            "Line": obj.Line,
            "ResultData": serialize_visual_data(obj.ResultData)
        }
    elif isinstance(obj, list):
        return [serialize_visual_inspection(item) for item in obj]
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))
