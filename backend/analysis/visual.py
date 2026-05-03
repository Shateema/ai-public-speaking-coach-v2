import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh


def analyze_gaze(video_path):
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    looking_frames = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True
    ) as face_mesh:

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # ⬇️ SAMPLE every 10th frame (VERY IMPORTANT)
            if frame_count % 10 != 0:
                continue

            total_frames += 1

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]

                # 👁️ Basic heuristic: nose near center
                nose = landmarks.landmark[1]

                if 0.4 < nose.x < 0.6:
                    looking_frames += 1

    cap.release()

    if total_frames == 0:
        return {"camera_facing_percentage": 0}

    percentage = round((looking_frames / total_frames) * 100, 2)

    return {
        "camera_facing_percentage": percentage
    }