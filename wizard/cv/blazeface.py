import numpy as np


# import tensorflow as tf
# import torch.nn as nn
# import torch
# class BlazeFace(nn.Module):
class BlazeFace:
    """The BlazeFace face detection model from MediaPipe.
    The version from MediaPipe is simpler than the one in the paper;
    it does not use the "double" BlazeBlocks.
    Because we won't be training this model, it doesn't need to have
    batchnorm layers. These have already been "folded" into the conv
    weights by TFLite.
    The conversion to PyTorch is fairly straightforward, but there are
    some small differences between TFLite and PyTorch in how they handle
    padding on conv layers with stride 2.
    This version works on batches, while the MediaPipe version can only
    handle a single image at a time.
    Based on code from https://github.com/tkat0/PyTorch_BlazeFace/ and
    https://github.com/google/mediapipe/
    """

    def __init__(self, num_coords):
        super(BlazeFace, self).__init__()

        # These are the settings from the MediaPipe example graph
        # mediapipe/graphs/face_detection/face_detection_mobile_gpu.pbtxt
        self.num_classes = 1
        self.num_anchors = 896
        self.num_coords = num_coords
        self.score_clipping_thresh = 100.0
        self.x_scale = 128.0
        self.y_scale = 128.0
        self.h_scale = 128.0
        self.w_scale = 128.0
        self.min_score_thresh = 0.75
        self.min_suppression_threshold = 0.3

        # self._define_layers()

    def sigmoid(self, inX):
        if inX >= 0:
            return 1.0 / (1 + np.exp(-inX))
        else:
            return np.exp(inX) / (1 + np.exp(inX))

    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        """The output of the neural network is a tensor of shape (b, 896, 16)
        containing the bounding box regressor predictions, as well as a tensor
        of shape (b, 896, 1) with the classification confidences.
        This function converts these two "raw" tensors into proper detections.
        Returns a list of (num_detections, 17) tensors, one for each image in
        the batch.
        This is based on the source code from:
        mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.cc
        mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.proto
        """
        assert len(raw_box_tensor.shape) == 3
        assert raw_box_tensor.shape[1] == self.num_anchors
        assert raw_box_tensor.shape[2] == self.num_coords

        assert len(raw_box_tensor.shape) == 3
        assert raw_score_tensor.shape[1] == self.num_anchors
        assert raw_score_tensor.shape[2] == self.num_classes

        assert raw_box_tensor.shape[0] == raw_score_tensor.shape[0]

        detection_boxes = self._decode_boxes(raw_box_tensor, anchors)

        thresh = self.score_clipping_thresh
        raw_score_tensor = raw_score_tensor.clip(-thresh, thresh)

        detection_scores = 1 / (1 + np.exp(- raw_score_tensor)).squeeze(axis=-1)
        # detection_scores = self.sigmoid(raw_score_tensor).squeeze(axis=-1)

        # Note: we stripped off the last dimension from the scores tensor
        # because there is only has one class. Now we can simply use a mask
        # to filter out the boxes with too low confidence.
        mask = detection_scores >= self.min_score_thresh

        # Because each image from the batch can have a different number of
        # detections, process them one at a time using a loop.
        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]
            scores = np.expand_dims(detection_scores[i, mask[i]], axis=-1)
            output_detections.append(np.concatenate((boxes, scores), axis=-1))

        return output_detections

    def _decode_boxes(self, raw_boxes, anchors):
        """Converts the predictions into actual coordinates using
        the anchor boxes. Processes the entire batch at once.
        """
        boxes = np.zeros(raw_boxes.shape)

        x_center = raw_boxes[..., 0] / self.x_scale * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 1] / self.y_scale * anchors[:, 3] + anchors[:, 1]

        w = raw_boxes[..., 2] / self.w_scale * anchors[:, 2]
        h = raw_boxes[..., 3] / self.h_scale * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        for k in range(6):
            offset = 4 + k * 2
            keypoint_x = raw_boxes[..., offset] / self.x_scale * anchors[:, 2] + anchors[:, 0]
            keypoint_y = raw_boxes[..., offset + 1] / self.y_scale * anchors[:, 3] + anchors[:, 1]
            boxes[..., offset] = keypoint_x
            boxes[..., offset + 1] = keypoint_y

        return boxes

    def weighted_non_max_suppression(self, detections):
        """The alternative NMS method as mentioned in the BlazeFace paper:
        "We replace the suppression algorithm with a blending strategy that
        estimates the regression parameters of a bounding box as a weighted
        mean between the overlapping predictions."
        The original MediaPipe code assigns the score of the most confident
        detection to the weighted detection, but we take the average score
        of the overlapping detections.
        The input detections should be a Tensor of shape (count, 17).
        Returns a list of PyTorch tensors, one for each detected face.
        This is based on the source code from:
        mediapipe/calculators/util/non_max_suppression_calculator.cc
        mediapipe/calculators/util/non_max_suppression_calculator.proto
        """
        if len(detections) == 0: return []

        output_detections = []

        # Sort the detections from highest to lowest score.
        remaining = np.argsort(-detections[:, self.num_coords])
        while len(remaining) > 0:
            detection = detections[remaining[0]]

            # Compute the overlap between the first box and the other
            # remaining boxes. (Note that the other_boxes also include
            # the first_box.)
            first_box = detection[:4]
            other_boxes = detections[remaining, :4]
            ious = overlap_similarity(first_box, other_boxes)

            # If two detections don't overlap enough, they are considered
            # to be from different faces.
            mask = ious > self.min_suppression_threshold
            overlapping = remaining[mask]
            remaining = remaining[~mask]

            # Take an average of the coordinates from the overlapping
            # detections, weighted by their confidence scores.
            weighted_detection = detection.copy()
            if len(overlapping) > 1:
                coordinates = detections[overlapping, :self.num_coords]
                scores = detections[overlapping, self.num_coords: self.num_coords + 1]
                total_score = scores.sum()
                weighted = (coordinates * scores).sum(axis=0) / total_score
                weighted_detection[:self.num_coords] = weighted
                weighted_detection[self.num_coords] = total_score / len(overlapping)

            output_detections.append(weighted_detection)

        return output_detections


def blazeface(raw_output_a, raw_output_b, anchors, num_coords):
    if raw_output_a.size == 896:
        raw_score_tensor = raw_output_a
        raw_box_tensor = raw_output_b
    else:
        raw_score_tensor = raw_output_b
        raw_box_tensor = raw_output_a

    assert (raw_score_tensor.size == 896)
    assert (raw_box_tensor.size == 896 * num_coords)
    raw_score_tensor = raw_score_tensor.reshape(1, 896, 1)
    raw_box_tensor = raw_box_tensor.reshape(1, 896, num_coords)

    net = BlazeFace(num_coords)
    # 3. Postprocess the raw predictions:
    detections = net.tensors_to_detections(raw_box_tensor, raw_score_tensor, anchors)
    # 4. Non-maximum suppression to remove overlapping detections:
    filtered_detections = []
    for i in range(len(detections)):
        faces = net.weighted_non_max_suppression(detections[i])
        if len(faces) > 0:
            faces = np.stack(faces)  # if len(faces) > 0 else tf.zeros((0, 17))
        # print (faces.shape)
        filtered_detections.append(faces)
    return filtered_detections


# takes the letterbox dimensions and the original dimensions to map the results in letterbox image coordinates
# to original image coordinates
def convert_to_orig_points(results, orig_dim, letter_dim, num_coords):
    # if results.ndim == 1: np.expand_dims(results, 0)
    inter_scale = min(letter_dim / orig_dim[0], letter_dim / orig_dim[1])
    inter_h, inter_w = int(inter_scale * orig_dim[0]), int(inter_scale * orig_dim[1])
    offset_x, offset_y = (letter_dim - inter_w) / 2.0 / letter_dim, (letter_dim - inter_h) / 2.0 / letter_dim
    scale_x, scale_y = letter_dim / inter_w, letter_dim / inter_h
    results[:, 0:2] = (results[:, 0:2] - [offset_x, offset_y]) * [scale_x, scale_y]
    results[:, 2:4] = results[:, 2:4] * [scale_x, scale_y]
    results[:, 4:num_coords:2] = (results[:, 4:num_coords:2] - offset_x) * scale_x
    results[:, 5:num_coords + 1:2] = (results[:, 5:num_coords + 1:2] - offset_y) * scale_y
    # converting from 0-1 range to (orign_dim) range
    results[:, 0:num_coords:2] *= orig_dim[1]
    results[:, 1:num_coords + 1:2] *= orig_dim[0]

    return results.astype(np.int32)


def overlap_similarity(box, other_boxes):
    """Computes the IOU between a bounding box and set of other boxes."""

    def union(A, B):
        x1, y1, x2, y2 = A
        a = (x2 - x1) * (y2 - y1)
        x1, y1, x2, y2 = B
        b = (x2 - x1) * (y2 - y1)
        ret = a + b - intersect(A, B)
        return ret

    def intersect(A, B):
        x1 = max(A[0], B[0])
        y1 = max(A[1], B[1])
        x2 = min(A[2], B[2])
        y2 = min(A[3], B[3])
        return (x2 - x1) * (y2 - y1)

    ret = np.array([max(0, intersect(box, b) / union(box, b)) for b in other_boxes])
    return ret
