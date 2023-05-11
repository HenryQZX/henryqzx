import cv2
import numpy as np
import tflite_gpu

log = print

tflite = tflite_gpu.tflite()


class HairSegmentation:

    def __init__(self):
        self.color = (255, 0, 0)  # bgr color
        self.w, self.h = 512, 512
        self.input_shape = [self.w, self.h]
        inShape = [1 * self.w * self.h * 4 * 4, ]
        outShape = [1 * self.w * self.h * 2 * 4, ]
        model_path = "/home/wizard/cv/models/hair_segmentation.tflite"
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))
        self.in_tensor = np.zeros((512, 512, 4), dtype=np.float32)

    def process(self, frame):
        img = cv2.resize(frame, (self.input_shape[0], self.input_shape[1]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img / 255

        self.in_tensor[:, :, 0:3] = img
        log('img', img.shape)

        tflite.setTensor_Fp32(self.in_tensor, self.input_shape[1], self.input_shape[1])
        tflite.invoke()

        pred = tflite.getTensor_Fp32(0)

        pred0 = (pred[0::2]).reshape(self.w, self.h)
        pred1 = (pred[1::2]).reshape(self.w, self.h)

        back = ((pred0)).copy()
        front = ((pred1)).copy()

        mask = front - back

        mask[mask > 0.0] = 255
        mask[mask < 0.0] = 0

        out = self.transfer(frame, mask)
        return out

    def transfer(self, image, mask):
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        mask_n = np.zeros_like(image)
        mask_n[:, :, 0] = mask

        alpha = 0.7
        beta = (1.0 - alpha)
        dst = cv2.addWeighted(image, alpha, mask_n, beta, 0.0)

        return dst

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color


hair_segmentation = HairSegmentation()
