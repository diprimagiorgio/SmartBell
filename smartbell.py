import face_recognition
import cv2
import numpy as np
import os



class SmartBell:

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
    tolerance = 0.6
    # dictionary of person_name : face_encoding
    known_prsn = {}
    def __init__(self):
        #get a reference to the camera
        self.video = cv2.VideoCapture(0)
        # Loop to add images in friends folder
        for file in os.listdir("profiles"):
           self.add_person(file)

    def __del__(self):
        self.video.release()

    # TODO when I'm adding a user if there is someone at the door I'm using the same structure ( lock ? )
    def add_person(self, file_name: str) -> bool:
        try:
            # Extracting person name from the image filename eg: david.jpg
            file = os.path.join("profiles/", file_name)
            known_image = face_recognition.load_image_file(file)
            self.known_prsn[file_name.replace(".jpg", "")] = face_recognition.face_encodings(known_image)[0]
            return True
        except IndexError as e:
            print (f"Impossible to find the person in the img : {file}")
            return False
        except Exception as e:
            print(f"Error in adding a person \n{e}")
            return False

    def remove_person(self, name:str) -> bool:
        try:
            # remove from the two lists
            file = os.path.join("profiles/", f"{name}.jpg")

            self.known_prsn.pop(name)

            # remove from the files
            os.remove(file)
            return True
        except Exception as e:
            print(f"Error in removing the person \n{e}")
            return False

    @property
    def get_known_face_encodings(self) -> list:
        return list(self.known_prsn.values())
    @property
    def get_known_person(self) -> list:
        return  list(self.known_prsn.keys())


    def get_people(self):
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []

        #graba single frame of the video
        success, image = self.video.read()

        process_this_frame = True

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            # return the boundary box of the face
            face_locations = face_recognition.face_locations(rgb_small_frame)
            # return a list of 128-dimensional face encodings
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s), return a list of true or false
                matches = face_recognition.compare_faces(self.get_known_face_encodings, face_encoding, tolerance=self.tolerance)
                name = "Unknown"

                # print(face_encoding)
                print(matches)
                # we can have multiple faces that match, but we want the most similar
                face_distances = face_recognition.face_distance(self.get_known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                #if the face with the minimum distance is, True because of the function compare_faces
                if matches[best_match_index]:
                    p = np.array(self.get_known_person)
                    name = p[best_match_index]

                print(name)
                # print(face_locations)
                face_names.append(name)
                print(face_names)

        process_this_frame = not process_this_frame
        return image, face_locations, face_names


    def get_frame(self):
        (image, face_locations, face_names) = self.get_people()

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(image, (left, top), (right, bottom), (255, 255, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (255, 255, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 10, bottom - 10), font, 1.0, (0, 0, 0), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes(), face_names

    # return a string with the names in the list of names
    #TODO I can do it fancier, no comma at the beginning
    @staticmethod
    def get_names_list(list_names):
        msg = ""
        for name in list_names:
            msg += " , " + name
        return msg

