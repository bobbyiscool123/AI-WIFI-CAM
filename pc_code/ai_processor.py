#!/usr/bin/env python3
"""
AI Processor Module for ESP32-CAM Video Stream

This module handles AI processing of video frames using different models:
- YOLOv4 for object detection
- MediaPipe for pose estimation
- MediaPipe for face detection

Each model can be selected at runtime.
"""

import cv2
import numpy as np
import os

class AIProcessor:
    """Class to handle AI processing of video frames."""

    def __init__(self, model_name='yolov4', confidence_threshold=0.5):
        """
        Initialize the AI processor with the specified model.

        Args:
            model_name (str): Name of the AI model to use ('yolov4', 'mediapipe_pose', 'mediapipe_face')
            confidence_threshold (float): Confidence threshold for detections (0.0 to 1.0)
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.classes = None
        self.last_detection_count = 0

        # Initialize the selected model
        if model_name == 'yolov4':
            self._init_yolov4()
        elif model_name == 'mediapipe_pose':
            self._init_mediapipe_pose()
        elif model_name == 'mediapipe_face':
            self._init_mediapipe_face()
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    def _init_yolov4(self):
        """Initialize YOLOv4 model for object detection."""
        print("Initializing YOLOv4 model...")

        # Paths to model files
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        weights_path = os.path.join(model_dir, 'yolov4.weights')
        config_path = os.path.join(model_dir, 'yolov4.cfg')
        classes_path = os.path.join(model_dir, 'coco.names')

        # Check if model files exist
        if not os.path.exists(weights_path) or not os.path.exists(config_path):
            raise FileNotFoundError(
                f"YOLOv4 model files not found. Please download them to {model_dir}. "
                "See INSTALL.md for instructions."
            )

        # Load COCO class names
        with open(classes_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Load YOLOv4 model
        self.model = cv2.dnn.readNetFromDarknet(config_path, weights_path)

        # Set preferred backend and target
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # Use DNN_TARGET_CUDA for GPU

        # Get output layer names
        self.layer_names = self.model.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]

        # Generate random colors for class visualization
        np.random.seed(42)
        self.colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype=np.uint8)

    def _init_mediapipe_pose(self):
        """Initialize MediaPipe model for pose estimation."""
        try:
            import mediapipe as mp
            self.mp = mp
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.model = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=self.confidence_threshold,
                min_tracking_confidence=self.confidence_threshold
            )
            print("MediaPipe Pose model initialized")
        except ImportError:
            raise ImportError(
                "MediaPipe not installed. Please install it with: pip install mediapipe"
            )

    def _init_mediapipe_face(self):
        """Initialize MediaPipe model for face detection."""
        try:
            import mediapipe as mp
            self.mp = mp
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils
            self.model = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for short-range, 1 for full-range detection
                min_detection_confidence=self.confidence_threshold
            )
            print("MediaPipe Face Detection model initialized")
        except ImportError:
            raise ImportError(
                "MediaPipe not installed. Please install it with: pip install mediapipe"
            )

    def process_frame(self, frame):
        """
        Process a video frame with the selected AI model.

        Args:
            frame (numpy.ndarray): Input video frame

        Returns:
            numpy.ndarray: Processed frame with annotations
        """
        if self.model_name == 'yolov4':
            return self._process_yolov4(frame)
        elif self.model_name == 'mediapipe_pose':
            return self._process_mediapipe_pose(frame)
        elif self.model_name == 'mediapipe_face':
            return self._process_mediapipe_face(frame)
        else:
            return frame  # Return original frame if model not supported

    def _process_yolov4(self, frame):
        """Process frame with YOLOv4 for object detection."""
        height, width, _ = frame.shape

        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.model.setInput(blob)

        # Forward pass through the network
        outputs = self.model.forward(self.output_layers)

        # Process detections
        class_ids = []
        confidences = []
        boxes = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.confidence_threshold:
                    # YOLO returns coordinates relative to the center of the object
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maximum suppression to remove redundant overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, 0.4)

        # Update detection count
        self.last_detection_count = len(indices) if isinstance(indices, np.ndarray) else 0

        # Draw bounding boxes and labels
        result_frame = frame.copy()
        if self.last_detection_count > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]]
                confidence = confidences[i]
                color = (int(self.colors[class_ids[i]][0]),
                         int(self.colors[class_ids[i]][1]),
                         int(self.colors[class_ids[i]][2]))

                # Draw bounding box
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, 2)

                # Draw label background
                text = f"{label}: {confidence:.2f}"
                text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(result_frame, (x, y - text_size[1] - 10), (x + text_size[0], y), color, -1)

                # Draw label text
                cv2.putText(result_frame, text, (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return result_frame

    def _process_mediapipe_pose(self, frame):
        """Process frame with MediaPipe for pose estimation."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = self.model.process(rgb_frame)

        # Update detection count (1 if pose detected, 0 otherwise)
        self.last_detection_count = 1 if results.pose_landmarks else 0

        # Draw pose landmarks
        result_frame = frame.copy()
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                result_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            # Add text indicating pose detected
            cv2.putText(result_frame, "Pose Detected", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return result_frame

    def _process_mediapipe_face(self, frame):
        """Process frame with MediaPipe for face detection."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = self.model.process(rgb_frame)

        # Update detection count
        self.last_detection_count = len(results.detections) if results.detections else 0

        # Draw face detections
        result_frame = frame.copy()
        if results.detections:
            for detection in results.detections:
                # Draw bounding box
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                             int(bboxC.width * iw), int(bboxC.height * ih)

                cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw confidence score
                score = detection.score[0]
                cv2.putText(result_frame, f"Face: {score:.2f}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Add text showing number of faces detected
            cv2.putText(result_frame, f"Faces Detected: {self.last_detection_count}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return result_frame
