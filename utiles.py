from ultralytics import YOLO
import cv2
import torch
import time
torch.cuda.empty_cache()
import numpy as np
import math
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

def unix_time2data(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime("%d-%a:%B:%Y %H:%M")
    # formatted_date_HM = dt_object.strftime("%H:%M")
    return formatted_date

class DetectWash:
    def __init__(self):
        self.hand_wash_model = YOLO('best60.pt')
        self.predction_filter_car_plate  = PredictionFilter(50)


    def get_hand_wash_coor(self, frame, min_area=1500):
        hands_ret = []
        hands = self.hand_wash_model(frame, verbose=False)[0]
        for hand in hands.boxes.data.tolist():
            x1, y1, x2, y2, scorep, class_id = hand
            if class_id == 1:
                x1, y1, x2, y2 = list(map(int, [x1, y1, x2, y2]))
                hands_ret.append([x1, y1, x2, y2, scorep, class_id])
        hands_ret = self.predction_filter_car_plate.filter_near_rectangles(hands_ret, rect_only=True)
        hands_ret = self.predction_filter_car_plate.filter_area(hands_ret, min_area)
        return hands_ret
    
class Tracker:
    def __init__(self, life_time = 5, thresh_add = 0):
        self.old_objects = {}
        self.life_time = life_time
        self.thresh_add = thresh_add
        self.new_id = 0
        self.poped_objects = []

    def update(self, new_rects):
        self.poped_objects = []
        self.delete_not_found_obj()
        if len(self.old_objects)==0:
            for new_rect in new_rects:
                self.old_objects[self.new_id] = {"rect":new_rect, "not-found-times":0, "found":True, "start-time": time.time()}
                self.new_id += 1
            return [[key, self.old_objects[key]["rect"], self.old_objects[key]["found"], self.old_objects[key]["start-time"]] for key in self.old_objects.keys()]

        for key in self.old_objects.copy().keys():
            rect = self.old_objects[key]["rect"]
            # print(rect)
            old_center = [rect[0] + (rect[2]-rect[0])/2, rect[1]+(rect[3] - rect[1])/2]
            min_radius = min((rect[2]-rect[0])/2, (rect[3] - rect[1])/2)
            self.old_objects[key]["found"] = False
            for new_rect in new_rects.copy():
                new_center = [new_rect[0] + (new_rect[2]-new_rect[0])/2, new_rect[1]+(new_rect[3] - new_rect[1])/2]
                if self.dist_bet_2_points(new_center, old_center) <= min_radius + self.thresh_add:
                    # print(key, rect, new_rect, min_radius)
                    self.old_objects[key]["rect"] = new_rect
                    self.old_objects[key]["not-found-times"] = 0
                    self.old_objects[key]["found"] = True
                    new_rects.remove(new_rect)
                    break
                
            if not self.old_objects[key]["found"]:
                self.old_objects[key]["not-found-times"] +=1

        for new_rect_not_found in new_rects:
            self.old_objects[self.new_id] = {"rect":new_rect_not_found, "not-found-times":0, "found":True, "start-time": time.time()}
            self.new_id +=1

        
        if len(self.old_objects)==0:
            self.new_id = 0
        return [[key, self.old_objects[key]["rect"], self.old_objects[key]["found"], self.old_objects[key]["start-time"]] for key in self.old_objects.keys()]

    def dist_bet_2_points(self, p1, p2):
        x1,y1 = p1
        x2,y2 = p2
        return np.sqrt((x2-x1)**2+(y2-y1)**2)

    def delete_not_found_obj(self):
        # print("old", self.old_objects)
        for key in self.old_objects.copy().keys():
            if self.old_objects[key]["not-found-times"]>=self.life_time:
                self.poped_objects.append(self.old_objects.pop(key))
        # print("new", self.old_objects)
        
class PredictionFilter:
    def __init__(self, threshold_distance):
        self.threshold_distance = threshold_distance

    @staticmethod
    def calculate_center(rectangle):
        x1, y1, x2, y2 = rectangle
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y

    @staticmethod
    def are_centers_near(center1, center2, threshold_distance):
        distance = math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        return distance <= threshold_distance

    def mix_rectangles(self, rect1, rect2):
        rect1_x1, rect1_y1, rect1_x2, rect1_y2 = rect1
        rect2_x1, rect2_y1, rect2_x2, rect2_y2 = rect2
        rect3_x1 = (rect1_x1 + rect2_x1)//2
        rect3_y1 = (rect1_y1 + rect2_y1)//2
        rect3_x2 = (rect1_x2 + rect2_x2)//2
        rect3_y2 = (rect1_y2 + rect2_y2)//2
        return (rect3_x1, rect3_y1, rect3_x2, rect3_y2)

    def filter_near_rectangles(self, rectangles, rect_only=False):
        filtered_rectangles = []
        
        for rectangle in rectangles:
            rectangle_coords = rectangle[:4]
            score = rectangle[4]
            class_id = rectangle[5]
            center1 = self.calculate_center(rectangle_coords)
            is_near = False
            
            for i, filtered_rectangle in enumerate(filtered_rectangles):
                filtered_rectangle_coords = filtered_rectangle[:4]
                filtered_score = filtered_rectangle[4]
                filtered_class_id = filtered_rectangle[5]
                center2 = self.calculate_center(filtered_rectangle_coords)
                if self.are_centers_near(center1, center2, self.threshold_distance):
                    is_near = True
                    if score > filtered_score:
                        filtered_rectangles[i] = self.mix_rectangles(filtered_rectangles[i], rectangle)
                    break
            
            if not is_near:
                filtered_rectangles.append(rectangle)
        if rect_only:
            return [[x1, y1, x2, y2] for x1, y1, x2, y2, score, class_id in filtered_rectangles]
        else:
            return [[x1, y1, x2, y2, score, class_id] for x1, y1, x2, y2, score, class_id in filtered_rectangles]

    def filter_area(self, rectangles, threshold):
        output = []
        for x1,y1,x2,y2 in rectangles:
            if (x2-x1)*(y2-y1)>threshold:
                output.append([x1,y1,x2,y2])
        return output

class DB_CoMM:
    def sendToDB(self, data:dict, JSON_DB_FILE="database-of-hwd-durations-firebase-adminsdk-d3yd8-a4a0833a8f.json",
                ProjectID="database-of-hwd-durations", val=0):
        if val == 0:
            ## DON'T CHANGE THIS CODE
            cred = credentials.Certificate(JSON_DB_FILE)
            Config = {
            "apiKey": "AIzaSyCHD9raTlgFp-OT64UP3wV-oIU-pXLAd54",
            "authDomain": "database-of-hwd-durations.firebaseapp.com",
            "databaseURL": "https://database-of-hwd-durations-default-rtdb.firebaseio.com",
            "projectId": ProjectID,
            "databaseURL": "https://database-of-hwd-durations-default-rtdb.firebaseio.com/",
            "storageBucket": "database-of-hwd-durations.appspot.com",
            "messagingSenderId": "359816228479",
            "appId": "1:359816228479:web:7606ca596bbb4678c2594a",
            "measurementId": "G-ZYKYSKCF8X"}
            firebase_admin.initialize_app(cred, Config)

        ## conditions & refs
        ref = db.reference("/")

        for full_date, recorded_time in zip(data.keys(), data.values()):
            date = full_date.split(" ")[0]
            hours_min = full_date.split(" ")[1]
            db.reference(f"/{date}").update({f"{hours_min}":recorded_time})



