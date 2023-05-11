import cv2
import tflite_gpu

from blazeface import *

log = print
tflite = tflite_gpu.tflite()


class HandTracking:

    def __init__(self):
        self.input_shape = [128, 128]
        inShape = [1 * 128 * 128 * 3 * 4, ]
        outShape = [1 * 896 * 18 * 4, 1 * 896 * 1 * 4]
        model_path = "/home/wizard/cv/models/palm_detection.tflite"
        log('gpu:', tflite.NNModel(model_path, inShape, outShape, 4, 0))
        model_path = "/home/wizard/cv/models/hand_landmark.tflite"
        tflite.set_g_index(1)
        inShape1 = [1 * 224 * 224 * 3 * 4, ]
        outShape1 = [1 * 63 * 4, 1 * 4, 1 * 4]
        log('cpu:', tflite.NNModel(model_path, inShape1, outShape1, 4, 0))
        self.anchors = np.load('/home/wizard/cv/models/anchors.npy').astype(np.float32)

    def process(self, frame):
        bHand = False
        img = self.preprocess_image_for_tflite32(frame, 128)
        if bHand == False:
            tflite.set_g_index(0)
            tflite.setTensor_Fp32(img, self.input_shape[1], self.input_shape[1])

            tflite.invoke()

            raw_boxes = tflite.getTensor_Fp32(0)
            classificators = tflite.getTensor_Fp32(1)

            log(raw_boxes.size)
            log(classificators.size)
            detections = blazeface(raw_boxes, classificators, self.anchors, num_coords=18)

            x_min, y_min, x_max, y_max = self.plot_detections(frame, detections[0])
            if len(detections[0]) > 0:
                bHand = True
        if bHand:
            hand_nums = len(detections[0])
            if hand_nums > 2:
                hand_nums = 2
            for i in range(hand_nums):
                xmin = max(0, x_min[i])
                ymin = max(0, y_min[i])
                xmax = min(frame.shape[1], x_max[i])
                ymax = min(frame.shape[0], y_max[i])

                roi_ori = frame[ymin:ymax, xmin:xmax]
                roi = self.preprocess_image_for_tflite32(roi_ori, 224)

                tflite.set_g_index(1)
                tflite.setTensor_Fp32(roi, 224, 224)

                tflite.invoke()
                mesh = tflite.getTensor_Fp32(0)
                bHand = False

                mesh = mesh.reshape(21, 3) / 224
                cx, cy = self.calc_palm_moment(roi_ori, mesh)
                self.draw_landmarks(roi_ori, cx, cy, mesh)
                frame[ymin:ymax, xmin:xmax] = roi_ori
        return frame

    def preprocess_image_for_tflite32(self, image, model_image_size=300):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (model_image_size, model_image_size))
        image = np.expand_dims(image, axis=0)
        image = (2.0 / 255.0) * image - 1.0
        image = image.astype('float32')

        return image

    def plot_detections(self, img, detections, with_keypoints=True):
        output_img = img
        log(img.shape)
        x_min = [0, 0]
        x_max = [0, 0]
        y_min = [0, 0]
        y_max = [0, 0]
        hand_nums = len(detections)
        # if hand_nums >2:
        #     hand_nums=2
        log("Found %d hands" % hand_nums)
        if hand_nums > 2:
            hand_nums = 2
        for i in range(hand_nums):
            ymin = detections[i][0] * img.shape[0]
            xmin = detections[i][1] * img.shape[1]
            ymax = detections[i][2] * img.shape[0]
            xmax = detections[i][3] * img.shape[1]
            w = int(xmax - xmin)
            h = int(ymax - ymin)
            h = max(h, w)
            h = h * 224. / 128.
            # ymin-=0.08*h

            # xmin-=0.25*w
            # xmax=xmin+1.5*w;
            # ymax=ymin+1.0*h;

            x = (xmin + xmax) / 2.
            y = (ymin + ymax) / 2.

            xmin = x - h / 2.
            xmax = x + h / 2.
            ymin = y - h / 2. - 0.18 * h
            ymax = y + h / 2. - 0.18 * h

            # if w<h:
            #     xmin=xmin-(h+0.08*h-w)/2
            #     xmax=xmax+(h+0.08*h-w)/2
            #     ymin-=0.08*h
            #     # ymax-=0.08*h
            # else :
            #     ymin=ymin-(w-h)/2
            #     ymax=ymax+(w-h)/2

            # h=int(ymax-ymin)
            # ymin-=0.08*h
            # landmarks_xywh[:, 2:4] += (landmarks_xywh[:, 2:4] * pad_ratio).astype(np.int32) #adding some padding around detection for landmark detection step.
            # landmarks_xywh[:, 1:2] -= (landmarks_xywh[:, 3:4]*0.08).astype(np.int32)

            x_min[i] = int(xmin)
            y_min[i] = int(ymin)
            x_max[i] = int(xmax)
            y_max[i] = int(ymax)
            p1 = (int(xmin), int(ymin))
            p2 = (int(xmax), int(ymax))
            # log(p1,p2)
            cv2.rectangle(output_img, p1, p2, (0, 255, 255), 2, 1)

            # cv2.putText(output_img, "Face found! ", (p1[0]+10, p2[1]-10),cv2.FONT_ITALIC, 1, (0, 255, 129), 2)

            # if with_keypoints:
            #     for k in range(7):
            #         kp_x = int(detections[i, 4 + k*2    ] * img.shape[1])
            #         kp_y = int(detections[i, 4 + k*2 + 1] * img.shape[0])
            #         cv2.circle(output_img,(kp_x,kp_y),4,(0,255,255),4)

        return x_min, y_min, x_max, y_max

    def calc_palm_moment(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        palm_array = np.empty((0, 2), int)

        for index, landmark in enumerate(landmarks):
            landmark_x = min(int(landmark[0] * image_width), image_width - 1)
            landmark_y = min(int(landmark[1] * image_height), image_height - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            if index == 0:  # 手首1
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 1:  # 手首2
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 5:  # 人差指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 9:  # 中指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 13:  # 薬指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 17:  # 小指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
        M = cv2.moments(palm_array)
        cx, cy = 0, 0
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

        return cx, cy

    def draw_landmarks(self, image, cx, cy, landmarks):

        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # キーポイント
        for index, landmark in enumerate(landmarks):
            # if landmark.visibility < 0 or landmark.presence < 0:
            #     continue

            landmark_x = min(int(landmark[0] * image_width), image_width - 1)
            landmark_y = min(int(landmark[1] * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append((landmark_x, landmark_y))

            if index == 0:  # 手首1
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 1:  # 手首2
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 2:  # 親指：付け根
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 3:  # 親指：第1関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 4:  # 親指：指先
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
                cv2.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 2)
            if index == 5:  # 人差指：付け根
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 6:  # 人差指：第2関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 7:  # 人差指：第1関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 8:  # 人差指：指先
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
                cv2.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 2)
            if index == 9:  # 中指：付け根
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 10:  # 中指：第2関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 11:  # 中指：第1関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 12:  # 中指：指先
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
                cv2.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 2)
            if index == 13:  # 薬指：付け根
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 14:  # 薬指：第2関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 15:  # 薬指：第1関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 16:  # 薬指：指先
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
                cv2.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 2)
            if index == 17:  # 小指：付け根
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 18:  # 小指：第2関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 19:  # 小指：第1関節
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
            if index == 20:  # 小指：指先
                cv2.circle(image, (landmark_x, landmark_y), 5, (0, 255, 0), 2)
                cv2.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 2)

        # 接続線
        if len(landmark_point) > 0:
            # 親指
            cv2.line(image, landmark_point[2], landmark_point[3], (0, 255, 0), 2)
            cv2.line(image, landmark_point[3], landmark_point[4], (0, 255, 0), 2)

            # 人差指
            cv2.line(image, landmark_point[5], landmark_point[6], (0, 255, 0), 2)
            cv2.line(image, landmark_point[6], landmark_point[7], (0, 255, 0), 2)
            cv2.line(image, landmark_point[7], landmark_point[8], (0, 255, 0), 2)

            # 中指
            cv2.line(image, landmark_point[9], landmark_point[10], (0, 255, 0), 2)
            cv2.line(image, landmark_point[10], landmark_point[11], (0, 255, 0), 2)
            cv2.line(image, landmark_point[11], landmark_point[12], (0, 255, 0), 2)

            # 薬指
            cv2.line(image, landmark_point[13], landmark_point[14], (0, 255, 0), 2)
            cv2.line(image, landmark_point[14], landmark_point[15], (0, 255, 0), 2)
            cv2.line(image, landmark_point[15], landmark_point[16], (0, 255, 0), 2)

            # 小指
            cv2.line(image, landmark_point[17], landmark_point[18], (0, 255, 0), 2)
            cv2.line(image, landmark_point[18], landmark_point[19], (0, 255, 0), 2)
            cv2.line(image, landmark_point[19], landmark_point[20], (0, 255, 0), 2)

            # 手の平
            cv2.line(image, landmark_point[0], landmark_point[1], (0, 255, 0), 2)
            cv2.line(image, landmark_point[1], landmark_point[2], (0, 255, 0), 2)
            cv2.line(image, landmark_point[2], landmark_point[5], (0, 255, 0), 2)
            cv2.line(image, landmark_point[5], landmark_point[9], (0, 255, 0), 2)
            cv2.line(image, landmark_point[9], landmark_point[13], (0, 255, 0), 2)
            cv2.line(image, landmark_point[13], landmark_point[17], (0, 255, 0), 2)
            cv2.line(image, landmark_point[17], landmark_point[0], (0, 255, 0), 2)

        # 重心 + 左右
        if len(landmark_point) > 0:
            # handedness.classification[0].index
            # handedness.classification[0].score

            cv2.circle(image, (cx, cy), 12, (0, 255, 0), 2)
            # cv2.putText(image, handedness.classification[0].label[0],
            #           (cx - 6, cy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),
            #           2, cv2.LINE_AA)  # label[0]:一文字目だけ

        return image


hand_tracking = HandTracking()
