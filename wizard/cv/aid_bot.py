import android

droid = android.Android()
from cvs import *
import time
import tflite_gpu

tflite = tflite_gpu.tflite()
from ssd_mobilenet_utils import *
from SimpleTracker import SimpleTracker

input_shape = [300, 300]
class_names = read_classes('/home/wizard/cv/models/coco_classes.txt')
colors = generate_colors(class_names)
tracker = SimpleTracker(max_lost=3)
threshold = 0.6


class AidBot:

    def __init__(self):
        self.speed = 92
        self.check_connection = False
        inShape = [1 * 300 * 300 * 3, ]
        outShape = [1 * 10 * 4 * 4, 1 * 10 * 4, 1 * 10 * 4, 1 * 4]
        model_path = "/home/wizard/cv/models/ssdlite_mobilenet_v3.tflite"
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))

    def run_detection(self, image):
        tflite.setTensor_Int8(image, input_shape[1], input_shape[1])
        tflite.invoke()
        boxes = tflite.getTensor_Fp32(0)
        classes = tflite.getTensor_Fp32(1)
        scores = tflite.getTensor_Fp32(2)
        num = tflite.getTensor_Fp32(3)

        box = boxes.reshape((10, 4))
        # log("boxes",box)
        # log("scores",scores)
        # log("classes",classes)
        # log("num",num)

        box, scores, classes = np.squeeze(box), np.squeeze(scores), np.squeeze(classes + 1).astype(np.int32)

        # log("boxes1",boxes)
        # log("scores1",scores)
        # log("classes1",classes)
        # log("num1",num)

        out_scores, out_boxes, out_classes = non_max_suppression(scores, box, classes)

        # log predictions info
        # log('Found {} boxes for {}'.format(len(out_boxes), 'images/dog.jpg'))

        return out_scores, out_boxes, out_classes

    def process(self, frame):
        image_data = preprocess_image_for_tflite_uint8(frame, model_image_size=300)

        out_scores, out_boxes, out_classes = self.run_detection(image_data)

        detections_bbox = np.array(
            [[out_boxes[i][0], out_boxes[i][1], out_boxes[i][2], out_boxes[i][3]] for i in range(len(out_boxes)) if
             out_classes[i] == 1 and out_scores[i] > threshold and out_boxes[i][3] - out_boxes[i][1] > 0.1]).reshape(-1,
                                                                                                                     4)

        objects = tracker.update(detections_bbox)

        leftControl, rightControl = (0.0, 0.0)

        buf = droid.UsbRead()

        h, w, _ = frame.shape

        for (objectID, centroid) in objects.items():
            text = "ID {}".format(objectID)
            log(text, centroid)
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            # centerX=(left+right)/2
            centerX = centroid[0]

            x_pos_norm = 1.0 - 2.0 * centerX / w

            if x_pos_norm > 0:
                leftControl = 1.0
                rightControl = 1.0 + x_pos_norm
            else:
                leftControl = 1.0 - x_pos_norm
                rightControl = 1.0
            break

        # Draw bounding boxes on the image file
        result = draw_boxes_and_turn(frame, out_scores, out_boxes, out_classes, class_names, colors)

        droid.sendControlToVehicle(int(leftControl * self.speed), int(rightControl * self.speed))

        return frame

    def set_speed(self, speed):
        self.speed = speed

    def set_check_connection(self, check_connection):
        self.check_connection = check_connection

    def run(self):
        camid = 0
        log("connecting to usb bot")
        r = droid.connectUsb()
        if self.check_connection and 'No Device' in r[1]:
            startcv(ConnectionRefused)
        else:
            log("sendIndicatorToVehicle: 0")
            droid.sendIndicatorToVehicle(0)
            cap = cvs.VideoCapture(camid)
            while True:
                start = time.time()
                frame = cap.read()
                if frame is None:
                    continue
                if camid == 1:
                    frame = cvs.flip(frame, 1)
                frame = self.process(frame)
                end = time.time()
                t = end - start
                fps = "time: {:.2f}".format(t * 1000)
                lbs = 'Average FPS: ' + str(1 / t)
                cvs.setLbs(lbs)
                cvs.imshow(frame)
                sleep(1)


class ConnectionRefused(App):
    def __init__(self, *args, **kwargs):
        super(ConnectionRefused, self).__init__(*args)

    def idle(self):
        pass

    def main(self):
        return ConnectionRefused.construct_ui(self)

    @staticmethod
    def construct_ui(self):
        main_container = VBox(
            style={"width": "100%", "height": "100%", "position": "absolute", "top": "0px", "left": "0px",
                   "margin": "0px", "overflow": "auto"})
        lbl = Label('链接失败，请重新尝试', width='100%', height='100%',
                    style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'color': '#ff0000',
                           'font-size': '36px'})
        main_container.append(lbl)
        return main_container


aid_bot = AidBot()

# RPC 接口
# droid.connectUSB()
