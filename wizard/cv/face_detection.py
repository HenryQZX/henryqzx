import cv2
import tflite_gpu

from blazeface import *

log = print
tflite = tflite_gpu.tflite()


class FaceDetection:

    def __init__(self):
        self.input_shape = [128, 128]
        inShape = [1 * 128 * 128 * 3 * 4, ]
        outShape = [1 * 896 * 16 * 4, 1 * 896 * 1 * 4]
        model_path = "/home/wizard/cv/models/face_detection_front.tflite"
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))
        self.anchors = np.load('/home/wizard/cv/models/anchors.npy')

    def process(self, frame):
        img = cv2.resize(frame, (128, 128))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        img = img / 127.5 - 1.0

        tflite.setTensor_Fp32(img, self.input_shape[1], self.input_shape[1])
        tflite.invoke()

        raw_boxes = tflite.getTensor_Fp32(0)
        classificators = tflite.getTensor_Fp32(1)

        detections = blazeface(raw_boxes, classificators, self.anchors, num_coords=16)[0]
        out = self.plot(frame, detections)
        return out

    def plot(self, img, detections, with_keypoints=True):
        output_img = img

        for i in range(len(detections)):
            ymin = detections[i][0] * img.shape[0]
            xmin = detections[i][1] * img.shape[1]
            ymax = detections[i][2] * img.shape[0]
            xmax = detections[i][3] * img.shape[1]
            w = int(xmax - xmin)
            h = int(ymax - ymin)
            if w < h:
                xmin = xmin - (h - w) / 3.
                xmax = xmax + (h - w) / 3.
            else:
                ymin = ymin - (w - h) / 3.
                ymax = ymax + (w - h) / 3.

            p1 = (int(xmin), int(ymin))
            p2 = (int(xmax), int(ymax))
            log(p1, p2)
            cv2.rectangle(output_img, p1, p2, (0, 255, 255), 2, 1)

            if with_keypoints:
                for k in range(6):
                    kp_x = int(detections[i, 4 + k * 2] * img.shape[1])
                    kp_y = int(detections[i, 4 + k * 2 + 1] * img.shape[0])
                    cv2.circle(output_img, (kp_x, kp_y), 4, (0, 255, 255), 4)

        return output_img


face_detection = FaceDetection()
