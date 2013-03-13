import cv2
import numpy as np
import json
import sys
c = cv2.VideoCapture(0)


#0, 0, 40
#20, 20, 255



#Smallest Projector-off thresholds
"""
B_MIN = np.array([172, 50, 120],np.uint8)
B_MAX = np.array([173, 255, 255],np.uint8)
G_MIN = np.array([56, 25, 50],np.uint8)
G_MAX = np.array([64, 255, 255],np.uint8)
R_MIN = np.array([124, 25, 50],np.uint8)
R_MAX = np.array([127, 255, 255],np.uint8)
"""

B_MIN = np.array([167, 50, 120],np.uint8)
B_MAX = np.array([178, 255, 255],np.uint8)
G_MIN = np.array([50, 50, 50],np.uint8)
G_MAX = np.array([70, 255, 255],np.uint8)
R_MIN = np.array([110, 55, 70],np.uint8) #Increase sat to remove blue halo
R_MAX = np.array([120, 255, 255],np.uint8)

            
CANVAS_POINTS = np.array([[0,0],[0,1023],[1023,0],[1023,1023]],np.float32)
def getProjectorMaskAndTrafo(frame_HSV):
    bg_bright = frame_HSV[10][10][2]
    print "Using test brightness", bg_bright
    frame_threshed = cv2.inRange(frame_HSV, 
                                 np.array([0, 0, bg_bright+5],np.uint8), 
                                 np.array([180, 255, 255],np.uint8))
    
    # find contours in the threshold image
    contours,hierarchy = cv2.findContours(frame_threshed,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    # finding contour with maximum area and store it as best_cnt
    max_area = 0
    best_cnt_index = None
    for i,cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt_index = i
    
    if best_cnt_index is not None:
        mask = np.zeros(frame_threshed.shape, np.uint8)
        cv2.drawContours(mask, contours, best_cnt_index, 255, thickness=-1)
        
        approxCurve = cv2.approxPolyDP(contours[best_cnt_index], 100, closed=True)
        test = np.zeros(frame_threshed.shape, np.uint8)
        cv2.drawContours(test, [approxCurve], 0, color=255, thickness=2)
        #cv2.imshow("poly approx", test)
        
        #Sort by X coord (ascending) then by Y coord
        if len(approxCurve) != 4:
            print "Weird-ass curve. Abort!"
            return None
        points = map(lambda x: [x[0][0], x[0][1]], approxCurve)
        points.sort(lambda x, y: cmp(x[0], y[0]))
        if (points[0][1] > points[1][1]): 
            points[0:2] = [points[1], points[0]]
        if (points[2][1] > points[3][1]): 
            points[2:4] = [points[3], points[2]]

        perspective = cv2.getPerspectiveTransform(np.array(points, np.float32),CANVAS_POINTS)
        return (mask, perspective)
    return None
    
def getColorPoint(frame_HSV, min, max):
    frame_threshed = cv2.inRange(frame_HSV, min, max)
    
    
    # find contours in the threshold image
    contours,hierarchy = cv2.findContours(frame_threshed,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    # finding contour with maximum area and store it as best_cnt
    sorted_cnts = sorted(contours, lambda x, y: cv2.contourArea(x) > cv2.contourArea(y))
    #pts = []
    x, y = 0, 0
    numarea = 0
    
    for cnt in sorted_cnts:
        area = cv2.contourArea(cnt)
        if area < 5:
            continue
        M = cv2.moments(cnt)
        cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        x += cx * area
        y += cy * area
        numarea += area
        
        #cv2.circle(frame_threshed,(cx, cy),3,180,1)

    pts = []
    if numarea:
        pts = [(int(x / numarea), int(y / numarea))]
        #cv2.circle(frame_threshed,pts[0],8,255,1)
    
    #cv2.imshow('threshed', frame_threshed)
    return pts


T_MIN = R_MIN
T_MAX = R_MAX  
def main(callback = None):
    _,f = c.read()
    hsv_img = cv2.cvtColor(f,cv2.COLOR_RGB2HSV)
    (mask, perspective) = getProjectorMaskAndTrafo(hsv_img)
    if mask is not None:
        cv2.imshow("mask", mask)
    else:
        print "Couldn't find projector screen! Using entire image"
    #bgs = cv2.BackgroundSubtractorMOG(10*60, 1, 0.9, 0.1)
    
    while(1):
        _,f = c.read()
        #fgmask = bgs.apply(f)
        if mask is not None:
            f = cv2.bitwise_and(f, f, mask = mask)
        g = cv2.blur(f,(3,3))
        
        hsv_img = cv2.cvtColor(g,cv2.COLOR_RGB2HSV)
        
        points = {}
        #points['R'] = getColorPoint(hsv_img, R_MIN, R_MAX)
        #points['G'] = getColorPoint(hsv_img, G_MIN, G_MAX)
        points['B'] = getColorPoint(hsv_img, G_MIN, G_MAX) #TODO: Switch to blue
        
        toSend = {}
        toSend['B'] = []
        #toSend['R'] = []
        #toSend['G'] = []
        for k, v in points.iteritems():
            for i in xrange(min(1, len(v))):
                (cx, cy) = v[i]
                
                [x,y] = cv2.perspectiveTransform(np.float32([[[cx, cy]]]), perspective)[0][0]
                cv2.circle(f,(cx, cy),5,10,2)
                cv2.putText(f, "%s(%d %d)" % (k, x, y), 
                    (cx+10, cy), cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 255, 255), thickness=1)
                toSend[k].append((int(x),int(y)))
            
        cv2.imshow('tracked', f)
        
        if callback:
            callback(toSend)
        
        if cv2.waitKey(5)==27:
            break
        
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()
    
def web_socket_do_extra_handshake(request):
    pass  # Always accept.

def web_socket_transfer_data(request):
    #line = request.ws_stream.receive_message()
    #print line    
    def sendPoints(points):
        request.ws_stream.send_message(json.dumps(points))
        
    try:
        main(sendPoints)
    except:
        import traceback
        traceback.print_exc()
        return
        