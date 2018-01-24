from filepicker import * #SQ*
from eye_tracker_helpers import *
import pandas as pd
import os
from matplotlib import pyplot as plt
import csv
import copy



def analyseVideo(video, thresh, roi, striking_frame_list, plot, mouth_roi = None, mouth_thresh = 30, frame_range = (0,100), first_cali_vector = None):
    """
    Main analysis function
    :param video: Video class object (video_handling)
    :param thresh: threshold used to find eyes and swimbladder
    :param roi: crop each frame to ROI (if None then video is not cropped)
    :return: pandas DataFrame (frame number and vergence angles)
    """
    left = []
    right = []
    bladder_mid= []
    size_sb_list = []
    first_l_c = ()
    first_r_c = ()
    mouth_area = []

    # if there is no input of frame_range then just use the overall range
    if frame_range == (0, 100):
        frame_range = (0, video.framecount)

    count = 0

    for frame in range(frame_range[0],frame_range[1]):
        count += 1

        img = video.grabFrameN(frame)
        if roi is not None:
            img = cropImage(img, roi)

        """
        frameData() returns centres and angles for the fish axis and both eyes.
        To calculate vergence angles:
            - Angles increase CCW and a converged eye points towards the midline (CCW is counter clockwise)
            - A converged left eye has a greater CCW angle than the body axis
            - CW and CCW are reversed
            - Angles greater than 180 degrees mist be divergent
        """
        # Question. confused about this part of analysis...

        c, th, l_c, l_th, r_c, r_th, size_sb = frameData(img, thresh)  #tag
        # Note. th is the orientation/body axis

        if frame == 0:
            first_l_c = l_c
            first_r_c = r_c
            first_mid_eyes = findMidpoint(first_l_c, first_r_c)
            print first_mid_eyes
            if mouth_roi != None:
                first_c_roi = findMidpoint(mouth_roi[0], mouth_roi[1])
                first_cali_vector = vector(first_mid_eyes, first_c_roi)  #    dx = float(b[0]) - float(a[0])

        l_verg = findClockwiseAngle(th, l_th)
        r_verg = findClockwiseAngle(r_th, th)

        if l_verg > math.pi:
            l_verg -= 2 * math.pi
        if r_verg > math.pi:
            r_verg -= 2 * math.pi

        bladder_mid_distance = distance(c,findMidpoint(r_c,l_c))

        #mouth analysis section
        if mouth_roi != None:
            mouth_thresh = mouth_thresh     ########30 is roughly a good one

            mid_eyes = findMidpoint(l_c,r_c)
            cali_c_roi =  (mid_eyes[0]+first_cali_vector[0],mid_eyes[1]+first_cali_vector[1])

            bad_c_roi = findMidpoint(mouth_roi[0], mouth_roi[1])
            cali_vector_final = vector(bad_c_roi,cali_c_roi)
            p1 = (int(mouth_roi[0][0] + cali_vector_final[0]),
                  int(mouth_roi[0][1] + cali_vector_final[1]))
            p2 = (int(mouth_roi[1][0] + cali_vector_final[0]),
                  int(mouth_roi[1][1] + cali_vector_final[1]))

            #p1 = (int(mouth_roi[0][0] ),int(mouth_roi[0][1]))
            #p2 = (int(mouth_roi[1][0] ),int(mouth_roi[1][1]))
            #task. confirm this p1 and p2 is dynamically right
            #Answer. confirmed!

            mouth = img[p1[1]:p2[1] + 1, p1[0]:p2[0] + 1]
            internals = findAllContours(mouth, thresh=mouth_thresh)
            area = cv2.contourArea(internals[0])

        left.append(math.degrees(l_verg))
        right.append(math.degrees(r_verg))
        bladder_mid.append(bladder_mid_distance)
        size_sb_list.append(size_sb)
        if mouth_roi != None:
           mouth_area.append(area)
        # above are all the list


    df = pd.DataFrame(dict(left=left, right=right,bladder_mid=bladder_mid, size_sb = size_sb_list, mouth_area=mouth_area),
                      index=range(frame_range[0],frame_range[1]), columns=['left', 'right','bladder_mid','size_sb','mouth_area'])   #tag

    #PLOT THE BLADDER_MIDPOINT_DISTANCE HERE!

    n_size_sb_list = []   # normalized the size of swimbladder before plotting
    for item in size_sb_list:
        n_size_sb_list.append(item/max(size_sb_list)*min(bladder_mid))


    #PLOT THE STRIKING FRAME
    list_strike_frame = []
    # list_strike_frame = striking_frame_list

    if plot == 'yes':
       plt.plot(mouth_area, 'b')     #mouth_area is plotted here
       #plt.plot(n_size_sb_list, 'g')

       for strike_frame in list_strike_frame:
           #y = np.arange(44, 51, 0.02)
           #y = np.arange(min(min(bladder_mid), min(n_size_sb_list)), max(max(bladder_mid), max(n_size_sb_list)), 0.02)
           y = np.arange(min(mouth_area), max(mouth_area), 0.02)
           x = []
           for i in y:
               x.append(strike_frame)
           plt.plot(x, y, 'r')

       plt.savefig(video.name + "_t_" + str(thresh) + '_mthresh_' + str(mouth_thresh) + '_mroi_' + str(mouth_roi) +
                   '_range_' + str(frame_range) + '_realtime_version.png')
       plt.show()

    return df


def checkTracking(video, thresh=200, roi=None):
    """
    Check that tracking is working
    :param video: Video class object (video_handling)
    :param thresh: threshold used to find eyes and swimbladder
    :param roi: crop each frame to ROI (if None then video is not cropped)
    :return: None
    """
    winname = video.name
    video.addDisplay(winname, displayFunction=showEyes, displayKwargs={'thresh': thresh, 'roi': roi})  #tag
    cv2.waitKey(0)
    video.removeDisplay(winname)


def dt_csv_to_dict(filename):
    # Note. output is a dictionary with key as the name of videos and corresponding value is a list consists of all striking frames
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        list = [row for row in reader]

    d = dict()
    for i in range(len(list)):
        key = list[i][0]
        value_list = []
        for j in range(1,len(list[i])):
            if list[i][j] != '':
                value_list.append(list[i][j])
        d[key] = value_list

    '''
    # Note. Following is another way for transfer the csv into dictionary
    
    key_list = []
    value_list = []

    for i in range(len(list[0])):
        key_list.append(list[0][i])  # append the key column
        value_list.append([])        # put a null list as each item in value_list first

    for i in range(1, len(list)):  # the row
        for x in range(len(list[0])):  # the column
            if list[i][x] != '':
                value_list[x].append(int(list[i][x]))


    for i in range(len(key_list)):
        d[key_list[i]] = value_list[i]
    '''
    print d
    return d


if __name__ == "__main__":

    ### USER INPUT HERE FOR RANGE SPECIFIC ANALYSIS
    video_range = [(819, 908), (4423, 4565), (4931, 5000)]  #if there is no input, just put [(0,100)]

    ### USER INPUT HERE ###
    ### SELECT A FOLDER TO ANALYZE, FIND ALL AVI FILES IN THAT FOLDER ###
    #folder = pickdir()
    folder = 'D:\\DT\\2017\\December\\Dec 22th\\ctrl\\analysis'   # this should be the folder where you put all the videos for analysis
    csv_filename = ''   # this should be the file where you stored the striking frame, give the fullname including the folder!
    filenames = os.listdir(folder)
    avis = [filename for filename in filenames if os.path.splitext(filename)[1] == '.avi']

    ### CREATE A FOLDER WHERE RESULTS WILL BE SAVED ###
    output_folder = os.path.join(folder, 'mouth_results')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ### DT Read the tag csv file and store the striking-frame in a dictionary
    if csv_filename != '':
       striking_dict = dt_csv_to_dict(csv_filename)  #tag
    else:
       striking_dict = dict()
       # print striking_dict

    ### PROMPTS FOR USING ROI, CHANGING DEFAULT THRESHOLD, CHECK TRACKING FOR EACH VIDEO, PLOTTING DATA ###
    use_roi = 'n' # raw_input('draw ROI? y/n ')
    # set_threshold = raw_input('set new threshold? y/n ')
    set_threshold = 'y'
    check_tracking = 'n' # raw_input('check eye tracking for each video? y/n ')
    plot_data = 'n'  # raw_input('plot each trial once analysed? y/n ')

    ### ANALYSIS STARTS HERE (LOOP THROUGH EACH AVI FILE IN SELECTED FOLDER) ###
    for avi in avis:

        print avi  # tell the user which avi is processing

        # Load the striking frame, the tag
        if avi in striking_dict.keys():
           striking_frame_list = striking_dict[avi]
        else:
           striking_frame_list = []
           print 'No striking frame for this video!'

        ### ROI SELECTION ###
        if use_roi == 'y':
            video = Video(os.path.join(folder, avi))
            print 'choose general ROI'
            ROI = selectROI(video)
            print ROI
        else:
            ROI = None


        ### NEW SET MOUTH ROI
        video = Video(os.path.join(folder, avi))
        print 'choose the ROI for mouth analysis'
        #mouth_roi = selectROI(video)
        mouth_roi = ((338, 343), (361, 359))
        print mouth_roi
        # returned mouth_roi looks like ((249, 272), (283, 294)), <type 'tuple'>

        ### SETTING GENERAL THRESHOLD FOR EYE IDENTIFICATION
        if set_threshold == 'y':
            while (1):
                video = Video(os.path.join(folder, avi))
                thresh = setThreshold(video, 200, ROI)  # tag
                tem_data = analyseVideo(video, thresh, ROI, striking_frame_list, plot='no', mouth_roi=mouth_roi)  # tag
                # Note. I choose to plot mouth_area in analyseVideo, so plot='no' here because the threshold for mouth is not setted
                user_input = int(input('do you think the threshold ' + str(thresh) + ' is ok?'))
                if user_input == 1:  # press 1 to exit the loop, otherwise the program would pick the same avi files and process it
                    break

        else:
            video = Video(os.path.join(folder, avi))
            thresh = 200
            tem_data = analyseVideo(video, thresh, ROI, striking_frame_list, plot='no', mouth_roi=mouth_roi)  # tag
        # Note. I choose to plot mouth_area in analyseVideo, so plot='no' here because the threshold for mouth is not setted


        ### DISPLAY THE MOUTH ROI (WITH BINARIZATION?)
        ### Task. I should made change here to be able to set the threshold for mice

        video = Video(os.path.join(folder, avi))

        ###special session for cali_vector... maybe not so useful
        frame_1st = video.grabFrameN(0)
        c, th, l_c, l_th, r_c, r_th, size_sb = frameData(frame_1st, thresh)  # tag
        mid_eyes = findMidpoint(l_c, r_c)
        c_roi = findMidpoint(mouth_roi[0], mouth_roi[1])
        cali_vector = vector(mid_eyes, c_roi)

        mouth_thresh = 40

        '''
        while (1):
           print 'Now you are setting the threshold for mouth protrustion analysis'
           mouth_thresh = setmouthThreshold(video,30,ROI,mouth_roi,cali_vector,thresh)  #tag
           # the last argument 'thresh' here is actually the thresh for eye recognization
           data = analyseVideo(video, thresh, ROI, striking_frame_list, plot='yes',mouth_roi = mouth_roi, mouth_thresh = mouth_thresh)    #tag
           user_input = int(input('do you think the mouth_threshold ' + str(mouth_thresh) + ' is ok?'))
           if user_input == 1:  # press 1 to exit the loop, otherwise the program would pick the same avi files and process it
              break
        '''



        ### CREATE FILEPATH TO VIDEO FILE ###
        file_path = os.path.join(folder, avi)
        name = os.path.splitext(avi)[0]

        ### IMPROT VIDEO ###
        video = Video(file_path)
        video.name = avi


        for video_frame_range in video_range:
            # analyze each frame_range for video one by one
            print video_frame_range

            ### MAIN ANALYSIS FUNCTION ###
            data = analyseVideo(video, thresh, ROI, striking_frame_list, plot='yes',mouth_roi = mouth_roi, mouth_thresh = mouth_thresh,
                                frame_range=video_frame_range, first_cali_vector = cali_vector)    #tag

            ### PLOTTING ###
            if plot_data == 'y':
               data.plot()
               plt.show()

            ### CREATE AN OUTPUT PATH TO SAVE RESULTS ###
            output_path = os.path.join(output_folder, name + '_thresh_' + str(thresh) + '_mthresh_' + str(mouth_thresh) +
                                       '_mroi_' + str(mouth_roi) + '_range_' + str(video_frame_range) + '_realtime_version.csv')

            ### SAVE RESULTS ###
            data.to_csv(output_path)