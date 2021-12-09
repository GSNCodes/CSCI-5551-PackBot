#!/usr/bin/env python3

import argparse
import imutils
from imutils.video import VideoStream
import time
import cv2
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import Float64MultiArray
import rospy

global size_of_marker 
global mtx
global dist

bridge = CvBridge()
img_pub = rospy.Publisher('/usb_cam/image_aruco',Image, queue_size=1)

tvec_pub = rospy.Publisher('t_vecs', Float64MultiArray, queue_size=10)
#transform_pub = rospy.Publisher('/',,qu)

# all tags supported by cv2
ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT["DICT_6X6_250"])
arucoParams = cv2.aruco.DetectorParameters_create()
board = cv2.aruco.CharucoBoard_create(6, 4, 1, 0.8, arucoDict)

# """ def read_chessboards(images):
#     """
#     #Charuco base pose estimation.
#     """ 
#     print("POSE ESTIMATION STARTS:")
#     allCorners = []
#     allIds = []
#     decimator = 0

#     for im in images:
#         print("=> Processing image {0}".format(im))
#         frame = cv2.imread(im, 0)
#         #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         res = cv2.aruco.detectMarkers(frame, arucoDict)

#         if len(res[0])>0:
#             res2 = cv2.aruco.interpolateCornersCharuco(res[0],res[1],frame,board)
#             if res2[1] is not None and res2[2] is not None and len(res2[1])>3 and decimator%1==0:
#                 allCorners.append(res2[1])
#                 allIds.append(res2[2])

#         decimator+=1

#     imsize = frame.shape
#     return allCorners,allIds,imsize

# def calibrate_camera(allCorners,allIds,imsize):


#     """
#     #Calibrates the camera using the dected corners.
#     """
#     print("CAMERA CALIBRATION")

#     cameraMatrixInit = np.array([[ 2000.,    0., imsize[0]/2.],
#                                 [    0., 2000., imsize[1]/2.],
#                                 [    0.,    0.,           1.]])

#     distCoeffsInit = np.zeros((5,1))
#     flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL)
#     (ret, camera_matrix, distortion_coefficients0,
#     rotation_vectors, translation_vectors,
#     stdDeviationsIntrinsics, stdDeviationsExtrinsics,
#     perViewErrors) = cv2.aruco.calibrateCameraCharucoExtended(
#                     charucoCorners=allCorners,
#                     charucoIds=allIds,
#                     board=board,
#                     imageSize=imsize,
#                     cameraMatrix=cameraMatrixInit,
#                     distCoeffs=distCoeffsInit,
#                     flags=flags,
#                     criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))
    
#     return ret, camera_matrix, distortion_coefficients0, rotation_vectors, translation_vectors """

def main():
    rospy.init_node('aruco_pose',anonymous = True)
    sub = rospy.Subscriber('/usb_cam/image_raw',Image,image_callback,queue_size=1)
    #vec_sub = rospy.Subscriber('t_vecs', Float64MultiArray, queue_size=10)
    rospy.spin()

#def tvec_callback(msg:Float64MultiArray):
#    print(type(data))


def image_callback(msg:Image):
    #rospy.loginfo("Got an image!")
    frame = bridge.imgmsg_to_cv2(msg)
    #frame = imutils.resize(frame, width=1000)
    # plt.imshow(frame)
    # plt.show()
    # continue
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    rvecs,tvecs,_ = cv2.aruco.estimatePoseSingleMarkers(corners, size_of_marker , mtx, dist)
        # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        i = 0
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                (topLeft[0], topLeft[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
            cv2.putText(frame, str(int(np.linalg.norm(tvecs[i]))) + "cm",
                (topLeft[0], topLeft[1] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)
            
            i += 1

    # if tvecs is not None:
    #     for i,v in enumerate(tvecs):
    #         print(ids[i], ": ", np.linalg.norm(v))

    # plt.imshow(frame)
    # plt.show()
    # continue
    
    # show the output frame
    #cv2.imshow("Frame", frame)
    t_vecs_msg = Float64MultiArray()


    if tvecs is not None:
        #print(tvecs)
        temp_vec = np.reshape(tvecs,(tvecs.shape[0],tvecs.shape[2]))
        temp_vec_norm = np.linalg.norm(temp_vec,axis = 1)

        closest_id = ids[np.argmin(temp_vec_norm)]
        print("The closest id is: ",closest_id)
        msg = []
        for t in tvecs:
            vec = []
            for x in t:
                for val in x:
                    vec.append(val)
            msg.append(vec)
        #print(len(msg))
        t_vecs_msg.data = msg
        tvec_pub.publish(t_vecs_msg)
        #print(type(t_vecs_msg))

    imgMsg = bridge.cv2_to_imgmsg(frame, encoding = 'bgr8')
    img_pub.publish(imgMsg)
    key = cv2.waitKey(1) & 0xFF
    #time.sleep(.1)



if __name__ == "__main__":
    #imagesFolder = "/home/bharath/catkin_ws/src/aruco_detect/src/images2/"
    #images = [imagesFolder + f for f in os.listdir(imagesFolder) if f.startswith("frame")]

    #allCorners, allIds, imsize = read_chessboards(images)
    
    #ret, mtx, dist, rvecs, tvecs = calibrate_camera(allCorners,allIds,imsize)
    
    dist = np.load("/home/bharath/catkin_ws/src/aruco_detect/src/dist.npy")
    mtx = np.load("/home/bharath/catkin_ws/src/aruco_detect/src/mtx.npy")

    #np.save("/home/bharath/catkin_ws/src/aruco_detect/src/mtx.npy", mtx)
    #np.save("/home/bharath/catkin_ws/src/aruco_detect/src/dist.npy", dist)
    size_of_marker = 2.8
    main()

    #detectFromStream(size_of_marker, mtx, dist) 


