
import numpy as np
import cv2
import sys
import os

def roi_image_edit(event,x,y,flags,param):
    if param['roi_img'].marking_mode == 'segmentation':
        mark_image(event,x,y,flags,param)
    elif param['roi_img'].marking_mode == 'teeth':
        tooth_mark(event,x,y,flags,param)

def mark_image(event,x,y,flags,param):
    #orig_img = param['orig_img']
    roi_img = param['roi_img']

    if event == cv2.EVENT_LBUTTONDOWN:
        roi_img.curr_drawing = True
        cv2.circle(roi_img.marked_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
        cv2.circle(roi_img.marked_only_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
        cv2.circle(roi_img.marker_image,(x,y),param['thickness'],roi_img.marker_color_index,-1)
    elif event == cv2.EVENT_MOUSEMOVE:
        if roi_img.curr_drawing == True:
            cv2.circle(roi_img.marked_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
            cv2.circle(roi_img.marked_only_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
            cv2.circle(roi_img.marker_image,(x,y),param['thickness'],roi_img.marker_color_index,-1)
    elif event == cv2.EVENT_LBUTTONUP:
        if roi_img.curr_drawing == True:
            roi_img.curr_drawing = False
            #cv2.circle(roi_img.marked_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
            #cv2.circle(roi_img.marked_only_image,(x,y),param['thickness'],param['colors'][roi_img.marker_color_index],-1)
            #cv2.circle(roi_img.marker_image,(x,y),param['thickness'],roi_img.marker_color_index,-1)

def tooth_mark(event,x,y,flags,param):
    roi_img = param['roi_img']
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_img.curr_drawing = True
        roi_img.tooth_list.append(tooth_area(x1=x,y1=y,label=None))
        roi_img.temporary_image = roi_img.marked_image.copy()
    elif event == cv2.EVENT_MOUSEMOVE:
        roi_img.curr_x = x
        roi_img.curr_y = y
        if roi_img.curr_drawing == True:
            currtooth = roi_img.tooth_list[-1]
            roi_img.marked_image = roi_img.temporary_image.copy()
            cv2.rectangle(roi_img.marked_image,(currtooth.x1,currtooth.y1),(x,y),[255,255,0],2)
            currtooth.x2 = x
            currtooth.y2 = y
    elif event == cv2.EVENT_LBUTTONUP:
        if roi_img.curr_drawing == True:
            roi_img.curr_drawing = False
            currtooth = roi_img.tooth_list[-1]
            roi_img.marked_image = roi_img.temporary_image.copy()
            cv2.rectangle(roi_img.marked_image,(currtooth.x1,currtooth.y1),(x,y),[255,255,0],2)
            currtooth.x2 = x
            currtooth.y2 = y
            currtooth.sort_corners()
            #Check if the square has been properly drawn:
            if currtooth.compute_area() <= 25:#Minimum 25 pixels
                roi_img.tooth_list.pop()
                roi_img.marked_image = roi_img.temporary_image.copy()
            # for tooth in roi_img.tooth_list:
            #     print tooth.compute_area()
        
        

def compute_roi(event,x,y,flags,param):
    orig_img = param['orig_img']
    roi_img = param['roi_img']
    if event == cv2.EVENT_LBUTTONDOWN:
        orig_img.curr_drawing = True
        orig_img.roi_x1 = x
        orig_img.roi_y1 = y
    elif event == cv2.EVENT_MOUSEMOVE:
        if orig_img.curr_drawing == True:
            orig_img.curr_image = orig_img.orig_image.copy()
            cv2.rectangle(orig_img.curr_image,(orig_img.roi_x1,orig_img.roi_y1),(x,y),[255,0,0],2)
            orig_img.roi_x2 = x
            orig_img.roi_y2 = y
    elif event == cv2.EVENT_LBUTTONUP:
        orig_img.curr_drawing = False
        cv2.rectangle(orig_img.curr_image,(orig_img.roi_x1,orig_img.roi_y1),(x,y),[255,0,0],2)
        orig_img.roi_x2 = x
        orig_img.roi_y2 = y
        orig_img.sort_roi_edges()
        roi_img.curr_image = cv2.resize(orig_img.orig_image[orig_img.roi_y1:orig_img.roi_y2,orig_img.roi_x1:orig_img.roi_x2],(0,0),fx=orig_img.resize_roi_factor,fy=orig_img.resize_roi_factor)
        roi_img.marker_image = np.zeros(roi_img.curr_image.shape[:2],dtype=np.int32)
        roi_img.marked_image = roi_img.curr_image.copy()
        roi_img.marked_only_image = roi_img.curr_image.copy()

class input_image:
    def __init__(self,filename,resize_roi_factor=2.5):
        self.filename = filename
        self.orig_image = cv2.imread(filename)
        self.curr_image = self.orig_image.copy()
        self.curr_drawing = False
        self.roi_x1 = -1
        self.roi_x2 = -1
        self.roi_y1 = -1
        self.roi_y2 = -1
        self.resize_roi_factor = resize_roi_factor
    def sort_roi_edges(self):
        if self.roi_x1 > self.roi_x2:
            temp = self.roi_x1
            self.roi_x1 = self.roi_x2
            self.roi_x2 = temp
        if self.roi_y1 > self.roi_y2:
            temp = self.roi_y1
            self.roi_y1 = self.roi_y2
            self.roi_y2 = temp
    def roi_area(self):
        return np.abs(self.roi_x2-self.roi_x1)*np.abs(self.roi_y2-self.roi_y1)
        
class roi_image:
    def __init__(self):
        self.curr_image = None
        self.marker_image = None
        self.marked_image = None
        self.marked_only_image = None
        self.temporary_image = None
        self.watershed_image = None
        self.segmented_image = None
        self.curr_drawing = False
        self.curr_x = 0
        self.curr_y = 0
        self.watershed_bool = False
        self.marker_color_index = 1
        self.tooth_list = []
        self.marking_mode = 'segmentation'
    def redraw_teeth(self):
        self.marked_image = self.marked_only_image.copy()
        if len(self.tooth_list) > 0:
            for i in range(len(self.tooth_list)):
                cv2.rectangle(self.marked_image,(self.tooth_list[i].x1,self.tooth_list[i].y1),(self.tooth_list[i].x2,self.tooth_list[i].y2),[255,255,0],2)
    def sort_teeth(self):
        teeth_xes = np.zeros(len(self.tooth_list))
        for i in range(len(self.tooth_list)):
            teeth_xes[i] = np.array([self.tooth_list[i].x1,self.tooth_list[i].x2]).min()
        sorted_indices = np.argsort(teeth_xes)
        new_teeth = []
        for i in range(len(sorted_indices)):
            new_teeth.append(self.tooth_list[sorted_indices[i]])
        self.tooth_list = new_teeth

    def draw_teeth_output(self):
        if len(self.tooth_list) > 0:
            self.sort_teeth()
            for i in range(len(self.tooth_list)):
                text = self.tooth_list[i].label
                if text == '':
                    text = "{0:d}".format(i+1)
                fontsize = 3
                fontname = cv2.FONT_HERSHEY_PLAIN
                textsize = cv2.getTextSize(text,fontname,fontsize,3)
                textpos_bot_left = (int((self.tooth_list[i].x1+self.tooth_list[i].x2)/2.-textsize[0][0]/2.),int(self.tooth_list[i].y1-10))
                cv2.putText(self.watershed_image, text, textpos_bot_left,fontname,fontsize,[255,255,0],3)
                cv2.rectangle(self.watershed_image,(self.tooth_list[i].x1,self.tooth_list[i].y1),(self.tooth_list[i].x2,self.tooth_list[i].y2),[255,255,0],2)
        
    def write_data(self,output_file,enamel_color,dentin_color,unsure_color,resize_factor,input_image_filename):
        if len(self.tooth_list) > 0:
            self.sort_teeth()
            for i in range(len(self.tooth_list)):
                #Compute all enamel and dentin pixels:
                segment_coverage = self.segmented_image[self.tooth_list[i].y1:self.tooth_list[i].y2,self.tooth_list[i].x1:self.tooth_list[i].x2]
                enamel_coverage = self.extract_colored_pixels(segment_coverage,enamel_color)
                dentin_coverage = self.extract_colored_pixels(segment_coverage,dentin_color)
                unsure_coverage = self.extract_colored_pixels(segment_coverage,unsure_color)
                tooth_name = self.tooth_list[i].label
                if tooth_name == '':
                    tooth_name = '{0:d}'.format(i+1)
                output_file.write("{0:s},{1:s},{2:.2f},{3:.2f},{4:.2f}\n".format(input_image_filename,tooth_name,np.sum(enamel_coverage)/float(resize_factor),np.sum(dentin_coverage)/float(resize_factor),np.sum(unsure_coverage)/float(resize_factor)))
                

    def extract_colored_pixels(self,image,color):
        output_image = np.ones(image.shape[:2],dtype=np.bool)
        for i in range(len(color)):
            output_image = (output_image) & (image[:,:,i] == color[i])
        return output_image
                
    def remove_nearest_tooth(self):
        if len(self.tooth_list) > 0:
            curr_closest_tooth_index,curr_closest_tooth_dist = self.compute_nearest_tooth()
            #Now, delete it:
            self.tooth_list.pop(curr_closest_tooth_index)
            
            #Redraw image:
            self.redraw_teeth()

    def compute_nearest_tooth(self):
        if len(self.tooth_list) > 0:
            #Compute nearest tooth:
            #We'll just brute-force this, since the number of teeth is likely to be <=10:
            curr_closest_tooth_index = 0
            tooth_center = self.tooth_list[0].compute_center()
            curr_closest_tooth_dist = np.sqrt((tooth_center[0]-self.curr_x)**2+(tooth_center[1]-self.curr_y)**2)
            for i in range(1,len(self.tooth_list)):
                tooth_center = self.tooth_list[i].compute_center()
                tooth_dist = np.sqrt((tooth_center[0]-self.curr_x)**2+(tooth_center[1]-self.curr_y)**2)
                if tooth_dist < curr_closest_tooth_dist:
                    curr_closest_tooth_index = i
                    curr_closest_tooth_dist = tooth_dist
            return curr_closest_tooth_index,curr_closest_tooth_dist
        raise Exception('No teeth in list!')
            
    def label_nearest_tooth(self):
        if len(self.tooth_list) > 0:
            curr_closest_tooth_index,curr_closest_tooth_dist = self.compute_nearest_tooth()
            label = ''
            print "Type the label for the tooth, then press enter:"
            while True:
                key = 0xFF & cv2.waitKey(0)
                if key == 27: #ESC
                    break
                elif key == 127: #Backspace
                    label = label[:-1]
                elif key == 44: #Comma
                    pass
                elif (key >= ord('a') and key <= ord('z')) or (key >= ord('A') and key <= ord('Z')) or (key >= ord('0') and key <= ord('9')) or key == 63: #?A-Za-z0-9
                    label += chr(key)
                elif key == 13: #Enter
                    self.tooth_list[curr_closest_tooth_index].label = label
                    print "Accepted!"
                    break
                print label
                # if label != '':
                #     print label
                
class tooth_area:
    def __init__(self,x1=0,x2=0,y1=0,y2=0,label=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.label = label
    def sort_corners(self):
        if self.x1 > self.x2:
            temp = self.x1
            self.x1 = self.x2
            self.x2 = temp
        if self.y1 > self.y2:
            temp = self.y1
            self.y1 = self.y2
            self.y2 = temp
    def compute_area(self):
        return np.abs(self.x1-self.x2)*np.abs(self.y1-self.y2)
    def compute_center(self):
        return (self.x1+self.x2)/2.,(self.y1+self.y2)/2.
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Syntax: python tooth_wear_id.py [filename list] [output filename]")

    file_list = np.loadtxt(sys.argv[1],dtype=np.str,ndmin=1)
    output_filename = sys.argv[2]
    
    colors = [[255,255,255],[0,255,0],[0,0,255],[0,215,255],[0,127,255]]
    color_types = ['none','background','enamel','dentin','unsure']
    colors_nparr = np.int32(colors)
    
    output_file = open(output_filename,'w')
    output_file.write("#Image_Name,Tooth_ID,Enamel_Pix,Dentin_Pix,Unsure_Pix\n")
    output_file.close()

    for i in range(len(file_list)):
        filename = file_list[i]


        orig_img = input_image(filename)
        roi_img = roi_image()


        cv2.namedWindow('Original')
        cv2.namedWindow('ROI')
        cv2.namedWindow('Marker')
        cv2.namedWindow('Watershed')
        cv2.setMouseCallback('Original',compute_roi,param={'orig_img':orig_img,'roi_img':roi_img})
        cv2.setMouseCallback('ROI',roi_image_edit,param={'orig_img':orig_img,'roi_img':roi_img,'thickness':2,'colors':colors})

        #print "First choose a region of interest by clicking and dragging:"
        while True:
            cv2.imshow('Original',orig_img.curr_image)
            if orig_img.roi_area() > 0 and orig_img.curr_drawing == False:
                cv2.imshow('ROI',roi_img.marked_image)

            key = 0xFF & cv2.waitKey(1)
            if key == 27:
                break
            if key in [ord('q'),ord('Q')]:
                if roi_img.watershed_bool == True:
                    roi_img.draw_teeth_output()
                    output_file = open(output_filename,'a')
                    roi_img.write_data(output_file,colors[2],colors[3],colors[4],orig_img.resize_roi_factor,filename)
                    output_file.close()
                    outputname = os.path.splitext(filename)[0]+"_segmented"+os.path.splitext(filename)[1]
                    cv2.imwrite(outputname,roi_img.watershed_image)
                    break
                else:
                    print "Segmented image not yet created, use ESC to skip image"
            if key >= ord('1') and key <= ord('4'):
                #Change the marker color:
                roi_img.marker_color_index = int(chr(key))
                print "Currently marking {0:s}".format(color_types[roi_img.marker_color_index])
            if key == ord(' '):
                m = roi_img.marker_image.copy()
                cv2.watershed(roi_img.curr_image,m)
                overlay = colors_nparr[np.maximum(m,0)]
                vis = cv2.addWeighted(roi_img.curr_image,0.5,overlay,0.5,0.0,dtype=cv2.CV_8UC3)
                output_colorscheme = np.maximum(m,0)
                output_colorscheme[output_colorscheme == 1] = 0
                output_overlay = colors_nparr[output_colorscheme]
                roi_img.segmented_image = output_overlay
                roi_img.watershed_image = cv2.addWeighted(roi_img.curr_image,0.75,output_overlay,0.25,0.0,dtype=cv2.CV_8UC3)
                roi_img.watershed_bool = True
                cv2.imshow('Watershed',vis)

            if key in [ord('t'),ord('T')]:
                roi_img.marking_mode = 'teeth'
                print "Switching to Tooth Identification Mode, use the mouse to draw rectangles over each tooth you want to measure, press 'd' to delete the tooth rectangle nearest to the mouse:"
            if key in [ord('s'),ord('S')]:
                #Switch to marking regions of the image:
                roi_img.marking_mode = 'segmentation'
                print "Switching to Segmentation Mode:"
                print "Currently marking {0:s}".format(color_types[roi_img.marker_color_index])
            if key in [ord('d'),ord('D')]:
                if roi_img.marking_mode == 'teeth':
                    if len(roi_img.tooth_list) > 0:
                        roi_img.remove_nearest_tooth()
            if key in [ord('l'),ord('L')]:
                if roi_img.marking_mode == 'teeth':
                    if len(roi_img.tooth_list) > 0:
                        roi_img.label_nearest_tooth()
            if key in [ord('z'),ord('Z')]:
                #Reset colors drawn on ROI:
                if roi_img.marking_mode == 'segmentation':
                    roi_img.marked_image = roi_img.curr_image.copy()
                    roi_img.marked_only_image = roi_img.curr_image.copy()
                    roi_img.marker_image = np.zeros(roi_img.curr_image.shape[:2],dtype=np.int32)
                elif roi_img.marking_mode == 'teeth':
                    roi_img.tooth_list = []
                roi_img.redraw_teeth()


        cv2.destroyAllWindows()
    
