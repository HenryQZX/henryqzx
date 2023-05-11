import cv2
import tflite_gpu

from blazeface import *

log = print
tflite = tflite_gpu.tflite()


class FaceDetectionPrecise:

    def __init__(self):
        self.input_shape = [128, 128]
        inShape = [1 * 128 * 128 * 3 * 4, ]
        outShape = [1 * 896 * 16 * 4, 1 * 896 * 1 * 4]
        model_path = "/home/wizard/cv/models/face_detection_front.tflite"
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))
        model_path = "/home/wizard/cv/models/face_landmark.tflite"
        tflite.set_g_index(1)
        inShape1 = [1 * 192 * 192 * 3 * 4, ]
        outShape1 = [1 * 1404 * 4, 1 * 4]
        log('cpu:', tflite.NNModel(model_path, inShape1, outShape1, 4, 0))
        self.anchors = np.load('/home/wizard/cv/models/anchors.npy').astype(np.float32)

    def process(self, frame):
        fface = 0
        bFace = False
        x_min, y_min, x_max, y_max = (0, 0, 0, 0)
        img_pad, img, pad = self.preprocess_img_pad(frame, 128)

        if bFace == False:
            tflite.set_g_index(0)
            tflite.setTensor_Fp32(img, self.input_shape[1], self.input_shape[1])

            tflite.invoke()

            raw_boxes = tflite.getTensor_Fp32(0)
            classificators = tflite.getTensor_Fp32(1)
            detections = blazeface(raw_boxes, classificators, self.anchors, num_coords=16)[0]
            if len(detections) > 0:
                bFace = True
        if bFace == True:
            for i in range(len(detections)):
                ymin = detections[i][0] * img_pad.shape[0]
                xmin = detections[i][1] * img_pad.shape[1]
                ymax = detections[i][2] * img_pad.shape[0]
                xmax = detections[i][3] * img_pad.shape[1]
                w = int(xmax - xmin)
                h = int(ymax - ymin)
                h = max(w, h)
                h = h * 1.5

                x = (xmin + xmax) / 2.
                y = (ymin + ymax) / 2.

                xmin = x - h / 2.
                xmax = x + h / 2.
                ymin = y - h / 2.
                ymax = y + h / 2.
                ymin = y - h / 2. - 0.08 * h
                ymax = y + h / 2. - 0.08 * h
                x_min = int(xmin)
                y_min = int(ymin)
                x_max = int(xmax)
                y_max = int(ymax)

                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(img_pad.shape[1], x_max)
                y_max = min(img_pad.shape[0], y_max)
                roi_ori = img_pad[y_min:y_max, x_min:x_max]
                roi = self.preprocess_image_for_tflite32(roi_ori, 192)

                tflite.set_g_index(1)
                tflite.setTensor_Fp32(roi, 192, 192)
                tflite.invoke()
                mesh = tflite.getTensor_Fp32(0)
                ffacetmp = tflite.getTensor_Fp32(1)[0]
                if abs(fface - ffacetmp) > 0.5:
                    bFace = False
                fface = ffacetmp

                mesh = mesh.reshape(468, 3) / 192
                self.draw_landmarks(roi_ori, mesh)

                shape = frame.shape
                x, y = img_pad.shape[0] / 2, img_pad.shape[1] / 2

                frame = img_pad[int(y - shape[0] / 2):int(y + shape[0] / 2),
                        int(x - shape[1] / 2):int(x + shape[1] / 2)]
        return frame

    def preprocess_img_pad(self, img, image_size=128):
        # fit the image into a 128x128 square
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        shape = np.r_[img.shape]
        pad_all = (shape.max() - shape[:2]).astype('uint32')
        pad = pad_all // 2
        # log ('pad_all',pad_all)
        img_pad_ori = np.pad(
            img,
            ((pad[0], pad_all[0] - pad[0]), (pad[1], pad_all[1] - pad[1]), (0, 0)),
            mode='constant')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pad = np.pad(
            img,
            ((pad[0], pad_all[0] - pad[0]), (pad[1], pad_all[1] - pad[1]), (0, 0)),
            mode='constant')
        img_small = cv2.resize(img_pad, (image_size, image_size))
        img_small = np.expand_dims(img_small, axis=0)
        # img_small = np.ascontiguousarray(img_small)
        img_small = (2.0 / 255.0) * img_small - 1.0
        img_small = img_small.astype('float32')
        # img_norm = self._im_normalize(img_small)

        return img_pad_ori, img_small, pad

    def preprocess_image_for_tflite32(self, image, model_image_size=192):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (model_image_size, model_image_size))
        image = np.expand_dims(image, axis=0)
        image = (2.0 / 255.0) * image - 1.0
        image = image.astype('float32')

        return image

    def draw_landmarks(self, image, mesh):
        image_size = image.shape[0]
        mesh = mesh * image_size
        landmark_point = []
        for point in mesh:
            landmark_point.append((int(point[0]), int(point[1])))
            # landmark_point.append((point[0],point[1]))
            cv2.circle(image, (int(point[0]), int(point[1])), 2, (255, 255, 0), -1)

        if len(landmark_point) > 0:
            # 参考：https://github.com/tensorflow/tfjs-models/blob/master/facemesh/mesh_map.jpg

            # 左眉毛(55：内側、46：外側)
            cv2.line(image, landmark_point[55], landmark_point[65], (0, 0, 255), 2, -3)
            cv2.line(image, landmark_point[65], landmark_point[52], (0, 0, 255), 2, -3)
            cv2.line(image, landmark_point[52], landmark_point[53], (0, 0, 255), 2, -3)
            cv2.line(image, landmark_point[53], landmark_point[46], (0, 0, 255), 2, -3)

            # 右眉毛(285：内側、276：外側)
            cv2.line(image, landmark_point[285], landmark_point[295], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[295], landmark_point[282], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[282], landmark_point[283], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[283], landmark_point[276], (0, 0, 255),
                     2)

            # 左目 (133：目頭、246：目尻)
            cv2.line(image, landmark_point[133], landmark_point[173], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[173], landmark_point[157], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[157], landmark_point[158], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[158], landmark_point[159], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[159], landmark_point[160], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[160], landmark_point[161], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[161], landmark_point[246], (0, 0, 255),
                     2)

            cv2.line(image, landmark_point[246], landmark_point[163], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[163], landmark_point[144], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[144], landmark_point[145], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[145], landmark_point[153], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[153], landmark_point[154], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[154], landmark_point[155], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[155], landmark_point[133], (0, 0, 255),
                     2)

            # 右目 (362：目頭、466：目尻)
            cv2.line(image, landmark_point[362], landmark_point[398], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[398], landmark_point[384], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[384], landmark_point[385], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[385], landmark_point[386], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[386], landmark_point[387], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[387], landmark_point[388], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[388], landmark_point[466], (0, 0, 255),
                     2)

            cv2.line(image, landmark_point[466], landmark_point[390], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[390], landmark_point[373], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[373], landmark_point[374], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[374], landmark_point[380], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[380], landmark_point[381], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[381], landmark_point[382], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[382], landmark_point[362], (0, 0, 255),
                     2)

            # 口 (308：右端、78：左端)
            cv2.line(image, landmark_point[308], landmark_point[415], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[415], landmark_point[310], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[310], landmark_point[311], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[311], landmark_point[312], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[312], landmark_point[13], (0, 0, 255), 2)
            cv2.line(image, landmark_point[13], landmark_point[82], (0, 0, 255), 2)
            cv2.line(image, landmark_point[82], landmark_point[81], (0, 0, 255), 2)
            cv2.line(image, landmark_point[81], landmark_point[80], (0, 0, 255), 2)
            cv2.line(image, landmark_point[80], landmark_point[191], (0, 0, 255), 2)
            cv2.line(image, landmark_point[191], landmark_point[78], (0, 0, 255), 2)

            cv2.line(image, landmark_point[78], landmark_point[95], (0, 0, 255), 2)
            cv2.line(image, landmark_point[95], landmark_point[88], (0, 0, 255), 2)
            cv2.line(image, landmark_point[88], landmark_point[178], (0, 0, 255), 2)
            cv2.line(image, landmark_point[178], landmark_point[87], (0, 0, 255), 2)
            cv2.line(image, landmark_point[87], landmark_point[14], (0, 0, 255), 2)
            cv2.line(image, landmark_point[14], landmark_point[317], (0, 0, 255), 2)
            cv2.line(image, landmark_point[317], landmark_point[402], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[402], landmark_point[318], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[318], landmark_point[324], (0, 0, 255),
                     2)
            cv2.line(image, landmark_point[324], landmark_point[308], (0, 0, 255),
                     2)

        return image


face_detection_precise = FaceDetectionPrecise()
