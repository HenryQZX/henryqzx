import cv2
import numpy as np
import tflite_gpu
from scipy.ndimage.filters import maximum_filter

log = print
tflite = tflite_gpu.tflite()


class Objectron:

    def __init__(self):
        model_path = '/home/wizard/cv/models/object_detection_3d_chair_1stage.tflite'
        inShape = [1 * 640 * 480 * 3 * 4, ]
        outShape = [1 * 40 * 30 * 1 * 4, 1 * 40 * 30 * 16 * 4, 1 * 160 * 120 * 4 * 4]
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))

    def process(self, img_ori):
        img = cv2.cvtColor(img_ori, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (480, 640)).astype(np.float32)
        img = img / 128.0 - 1.0
        img = img[None]
        tflite.setTensor_Fp32(img, 480, 640)

        tflite.invoke()

        hm = tflite.getTensor_Fp32(0)
        displacements = tflite.getTensor_Fp32(1)
        log(hm.shape, displacements.shape)
        objs = self.decode(hm, displacements, threshold=0.7)
        for obj in objs:
            self.draw_box(img_ori, obj)
        return img_ori

    def detect_peak(self, image, filter_size=5, order=0.5):
        local_max = maximum_filter(image, footprint=np.ones((filter_size, filter_size)), mode='constant')
        detected_peaks = np.ma.array(image, mask=~(image == local_max))

        temp = np.ma.array(detected_peaks, mask=~(detected_peaks >= detected_peaks.max() * order))
        peaks_index = np.where((temp.mask != True))
        return peaks_index

    def decode(self, hm, displacements, threshold=0.8):
        hm = hm.reshape(40, 30)
        displacements = displacements.reshape(1, 40, 30, 16)
        peaks = self.detect_peak(hm)
        peakX = peaks[1]
        peakY = peaks[0]

        scaleX = hm.shape[1]
        scaleY = hm.shape[0]
        objs = []
        for x, y in zip(peakX, peakY):
            conf = hm[y, x]
            if conf < threshold:
                continue
            points = []
            for i in range(8):
                dx = displacements[0, y, x, i * 2]
                dy = displacements[0, y, x, i * 2 + 1]
                points.append((x / scaleX + dx, y / scaleY + dy))
            objs.append(points)
        return objs

    def draw_box(self, image, pts):
        scaleX = image.shape[1]
        scaleY = image.shape[0]

        lines = [(0, 1), (1, 3), (0, 2), (3, 2), (1, 5), (0, 4), (2, 6), (3, 7), (5, 7), (6, 7), (6, 4), (4, 5)]
        for line in lines:
            pt0 = pts[line[0]]
            pt1 = pts[line[1]]
            pt0 = (int(pt0[0] * scaleX), int(pt0[1] * scaleY))
            pt1 = (int(pt1[0] * scaleX), int(pt1[1] * scaleY))
            cv2.line(image, pt0, pt1, (255, 245, 0))

        for i in range(8):
            pt = pts[i]
            pt = (int(pt[0] * scaleX), int(pt[1] * scaleY))
            cv2.circle(image, pt, 1, (255, 245, 0), -1)
            cv2.putText(image, str(i), pt, cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)


objectron = Objectron()
