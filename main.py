import os
import pickle
import cv2
import numpy as np
import face_recognition

dataset_path = 'face_dataset.pkl'
if not os.path.exists(dataset_path):
    with open(dataset_path, 'wb') as f:
        pickle.dump(([], []), f)

with open(dataset_path, 'rb') as f:
    known_face_encodings, known_face_names = pickle.load(f)

def capture_poses(name):
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    angles = ["Front", "Right", "Left"]
    free_poses = [f"Pose {i+1}" for i in range(7)]
    all_poses = angles + free_poses

    captured_encodings = []

    for pose_name in all_poses:
        print(f"Please position your face for '{pose_name}' and press 'space' to save.")
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to access the camera.")
                break

            cv2.putText(frame, f"{pose_name}: Press 'Space' to capture, 'Esc' to cancel.",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Capture Face", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 32:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame)
                if face_encodings:
                    captured_encodings.append(face_encodings[0])
                    print(f"Face for '{pose_name}' saved successfully.")
                    break
                else:
                    print("Face not detected. Please retry.")
            elif key == 27:
                print("Capture cancelled.")
                video_capture.release()
                cv2.destroyAllWindows()
                return

    video_capture.release()
    cv2.destroyAllWindows()

    if len(captured_encodings) == len(all_poses):
        average_encoding = np.mean(captured_encodings, axis=0)
        known_face_encodings.append(average_encoding)
        known_face_names.append(name)

        with open(dataset_path, 'wb') as f:
            pickle.dump((known_face_encodings, known_face_names), f)

        print(f"Face '{name}' has been successfully added to the dataset.")
    else:
        print("Pose capture incomplete. Please try again.")

def recognize_face():
    tolerance = 0.4
    video_capture = cv2.VideoCapture(0)
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to read frame from camera.")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        detected = False

        if face_locations and face_encodings:
            (top, right, bottom, left) = face_locations[0]
            face_encoding = face_encodings[0]

            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            detected = True
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            if name != "Unknown":
                cv2.putText(frame, "Door Opened", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Door Closed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Door Closed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("OpenFace", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    video_capture.release()
    cv2.destroyAllWindows()

def delete_face():
    print("List of names in the dataset:")
    for i, name in enumerate(known_face_names):
        print(f"{i + 1}. {name}")

    choice = input("Enter the number of the face you want to delete (or press 'c' to cancel): ")
    if choice.lower() == 'c':
        print("Deletion cancelled.")
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(known_face_names):
            removed_name = known_face_names.pop(index)
            known_face_encodings.pop(index)

            with open(dataset_path, 'wb') as f:
                pickle.dump((known_face_encodings, known_face_names), f)

            print(f"{removed_name}'s face has been successfully removed from the dataset.")
        else:
            print("Invalid number.")
    except ValueError:
        print("Invalid input. Deletion cancelled.")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Select an option:")
        print("1. Add face to dataset")
        print("2. Recognize face using camera")
        print("3. Delete face from dataset")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            name = input("Input name: ")
            capture_poses(name)
        elif choice == '2':
            recognize_face()
        elif choice == '3':
            os.system('cls' if os.name == 'nt' else 'clear')
            delete_face()
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()