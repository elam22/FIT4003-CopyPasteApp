# action_classification.py
from abc import ABC, abstractmethod

from v2s.util.constants import (DISTANCE_MERGE_COMPLEX, FRAMES_PER_SECOND,
                            LONG_CLICK_FRAMES, LONG_CLICK_THRESHOLD,
                            OPACITY_THRESHOLD, SWIPE_EPSILON, SWIPES_THRESHOLD,
                            TAP_COUNT_THRESHOLD, TAP_EPSILON, TAP_THRESHOLD)
from v2s.util.event import ActionType, GUIAction
from v2s.util.general import GeneralUtils


class AbstractGUIActionClassifier(ABC):
    """
    Takes detected touches, groups them, and translates them into discrete 
    touch actions on a screen.

    Methods
    -------
    execute_classification()
        Executes GUIAction classification.
    """

    @abstractmethod
    def execute_classification(self):
        """
        Executes GUIAction classification.
        """
        pass

class GUIActionClassifier(AbstractGUIActionClassifier):
    """
    V2S Action classifier. Takes an input of touch detections, groups them, 
    and translates them into a series of GUIAction objects that can then be
    passed to Phase3.

    Attributes
    ----------
    touch_detections : list of Frames
        detected touches from Phase 1
    detected_actions : list of GUIActions
        detected actions
    
    Methods
    -------
    execute_classification()
        Completes classification steps to translate from Frames to GUIActions.
    group_consecutive_frames()
        Groups list of Frames into consecutive frames.
    group_taps_graph_alg(frame_groups)
        Uses graph algorithm to group consecutive frames into groups of taps.
    group_actions(tap_groups)
        Uses tap characteristics to group taps into a list of GUIActions.
    group_by_opacity()
        Ensures that list of GUIActions make sense based on opacity predictions
        of taps. Filters groups based on this.
    __opacity_increasing(curr_tap, next_tap, threshold)
        Determines if opacity is increasing between two taps relative to a given
        threshold.
     __fix_types_on_new_actions(actions)
        Makes sure that clicks and long clicks are classified correctly based
        on the number of frames that constitutes a long click.
    group_by_complex_action()
        Ensures that list of GUIActions is accurate for swipes and other complex
        actions. Filters groups based on this.
    __is_valid_type_action_merge(action1, action2)
        Determine if merging the actions is valid based on their types. You can
        merge a click and a swipe because separating them may have been a mistake.
    refine_gui_action_detections()
        Takes detected GUIActions and further filters these to ensure they are
        as accurate as possible. Includes grouping further by opacity and by
        complex actions.
    get_touch_detections()
        Returns touch_detections.
    set_touch_detections(dets)
        Changes touch detections to the specified value.
    get_detected_actions()
        Returns detected actions.
    set_detected_actions(actions)
        Changes detected actions to specified value.
    """

    def __init__(self, detections=None):
        """
        Parameters
        ----------
        detections : list of Frames
            list of detections to classify into actions
        """
        self.detected_actions = []
        # if none, will just have to be set later
        self.touch_detections = detections

    def execute_classification(self):
        """
        Completes classification steps to translate from Frames to GUIActions.
        """
        frame_groups = self.group_consecutive_frames()
        # fix tap frame values to be accurate
        for frame_group in frame_groups:
            for frame in frame_group:
                for tap in frame.get_screen_taps():
                    tap.set_frame(frame.get_id())
        
        tap_groups = self.group_taps_graph_alg(frame_groups)
        self.group_actions(tap_groups)
        self.group_by_opacity()
        # remove if action doesn't have enough taps associated
        # this is possible because even quickest taps last across multiple frames
        self.detected_actions = [action for action in self.detected_actions if 
                                 len(action.get_taps()) > TAP_THRESHOLD]
        self.group_by_complex_action()
        self.refine_gui_action_detections()

    def group_consecutive_frames(self):
        """
        Groups list of Frames into consecutive frames.

        Returns 
        -------
        frame_groups : list of list of Frames
            frames grouped by consecutive ids
        """
        frame_groups = []
        frame_group = []
        for frame in self.touch_detections:
            # check if consecutive frames
            # end the consecutive frame group if the group is not empty and the
            # next frame is not consecutive
            if (len(frame_group)!=0) and (frame_group[len(frame_group)-1].get_id() != frame.get_id()-1):
                # if the frame_group has enough taps in it to constitute a real
                # action, add it to the total groups
                if len(frame_group) > TAP_THRESHOLD:
                    frame_groups.append(frame_group)
                # and start a new group
                frame_group = []
            # if the group is empty or it's the next consecutive frame
            frame_group.append(frame)
        
        # take care of last frame group
        if len(frame_group) > TAP_THRESHOLD:
            frame_groups.append(frame_group)
        
        return frame_groups

    def group_taps_graph_alg(self, frame_groups):
        """
        Uses graph algorithm to group consecutive frames into groups of taps.

        Parameters
        ----------
        frame_groups : list of list of Frames
            frames grouped based on consecutive frames
        
        Returns
        -------
        tap_groups : list of list of ScreenTaps
            groups of screen taps that are output by graph algorithm
        """
        tap_groups = []

        for frame_group in frame_groups:
            initial_frame = frame_group[0]

            # implement queue using a list
            queue = []
            # add all screen taps in initial frame to queue
            queue.extend(initial_frame.get_screen_taps())
            while (len(queue)!=0):
                curr_tap = queue.pop(0)
                # if the tap has already been seen on our traversal, don't add
                # it to the tap group --> move on to the next one
                if (curr_tap.is_visited()):
                    continue
                
                # ensure that we won't process same tap twice
                curr_tap.set_visited(True)

                tap_group = []
                tap_group.append(curr_tap)
                
                # compare the current tap to the remaining frames in the group
                for i in range(1, len(frame_group)):
                    if curr_tap.get_frame() + 1 != frame_group[i].get_id():
                        continue
                    # if we reach this point, it means the frame that cur_tap
                    # belongs to is frame_group[i-1]
                    # next_taps is taps in frame directly after current frame
                    next_taps = frame_group[i].get_screen_taps()

                    best_next_tap = next_taps[0]
                    for next_tap in next_taps:
                        if next_tap.is_visited():
                            continue
                        
                        # Cycle through list of next taps to find the one closest
                        # in distance to curr_tap.
                        # Based on the idea that the taps across consecutive frames
                        # that are close to each other should be grouped together.
                        min_distance = GeneralUtils.get_distance(curr_tap, best_next_tap)
                        distance = GeneralUtils.get_distance(curr_tap, next_tap)
                        if distance < min_distance:
                            best_next_tap = next_tap;
                        # if the shortest distance from that tap hasn't been found
                        # add it to the queue
                        else:
                            queue.append(next_tap)
                    
                    # update distance after closest tap to curr_tap has been found
                    distance = GeneralUtils.get_distance(curr_tap, best_next_tap)
                    # if the distance is close enough, add the found tap to the
                    # tap group
                    if distance < TAP_EPSILON:
                        best_next_tap.set_visited(True)
                        tap_group.append(best_next_tap)
                    # otherwise, the tap group is complete
                    else:
                        tap_groups.append(tap_group)
                        break
                    
                    # find the next tap that can be linked in this group
                    curr_tap = best_next_tap

                # takes care of last tap group
                if (len(tap_group) > 0) and (tap_group not in tap_groups):
                    tap_groups.append(tap_group)
        
        i = 0
        while i < len(tap_groups):
            tap_group = tap_groups[i]
            if len(tap_group) > TAP_THRESHOLD:
                i += 1
                continue
            # last tap in the group
            curr_tap = tap_group[len(tap_group)-1]
            k = 1
            while k < len(tap_groups):
                next_tap_group = tap_groups[k]
                # first tap in the next group
                next_tap = next_tap_group[0]
                # if the tap groups occur on consecutive frames, group them
                if curr_tap.get_frame() + 1 == next_tap.get_frame():
                    tap_group.extend(tap_groups[k])
                    tap_groups.pop(k)
                    k -= 1

                curr_tap = tap_group[len(tap_group)-1]  
                k += 1
            i += 1
        return tap_groups

    def group_actions(self, tap_groups):
        """
        Uses tap characteristics to group taps into a list of GUIActions.

        Parameters
        ----------
        tap_groups : list of list of ScreenTaps
            grouped screen taps to be classified into actions
        """
        result_list_group = []
        for group in tap_groups:
            # set type to default as click or long click depending on # taps
            action_type = -1
            if len(group) < LONG_CLICK_FRAMES:
                action_type = ActionType.CLICK
            else:
                action_type = ActionType.LONG_CLICK
            initial_tap = group[0]
            for tap in group:
                # TODO : may need to change SWIPES_THRESHOLD to detect more 
                # minute swipes --> 10-25 is a good value?
                # determine if group distance deviates enough to be a swipe
                distance = GeneralUtils.get_distance(tap, initial_tap)
                if distance >= SWIPES_THRESHOLD:
                    action_type = ActionType.SWIPE
                    break
            
            # create list of frame ids for each tap
            frames = [tap.get_frame() for tap in group]
            result_list_group.append(GUIAction(group, frames, action_type))

        self.detected_actions = result_list_group;

    def group_by_opacity(self):
        """
        Ensures that list of GUIActions make sense based on opacity predictions
        of taps. I.e an action should not have an increase in opacity in the
        middle of it. Filters groups based on this.
        """
        new_actions = []

        for action in self.detected_actions:
            if ((action.get_type() == ActionType.LONG_CLICK) or 
                                       (action.get_type() == ActionType.CLICK)):
                tap_group = action.get_taps()
                new_tap_group = []
                frames = []

                current_tap = tap_group[0]

                # cycle through pairs of taps
                for i in range(1, len(tap_group)):
                    next_tap = tap_group[i]
                    
                    # see if part of the same group or not based on opacity
                    # should be included if the opacity is very high and if the opacity is not increasing
                    if ((next_tap.get_opacity_confidence() == 0.0) or 
                        (not self.__opacity_increasing(current_tap, next_tap))):
                        new_tap_group.append(current_tap)
                        frames.append(current_tap.get_frame())
                    # if it is not part of the group, make sure the group is large
                    # enough to be considered an action
                    elif len(new_tap_group) > TAP_THRESHOLD:
                        new_tap_group.append(current_tap)
                        frames.append(current_tap.get_frame())
                        new_actions.append(GUIAction(new_tap_group, frames, ActionType.CLICK))
                        new_tap_group = []
                        frames = []
                    current_tap = next_tap
                # take care of last tap
                new_tap_group.append(current_tap)
                frames.append(current_tap.get_frame())
                new_actions.append(GUIAction(new_tap_group, frames, ActionType.CLICK))
            else:
                new_actions.append(action)
        
        
        # fix types on newly classified actions
        new_actions = self.__fix_types_on_new_actions(new_actions)
        self.detected_actions = new_actions

    def __opacity_increasing(self, curr_tap, next_tap, 
                             threshold=OPACITY_THRESHOLD):
        """
        Determines if opacity is increasing between two taps relative to a given
        threshold.

        Parameters
        ----------
        curr_tap : ScreenTap
            first tap
        next_tap : ScreenTap
            second tap
        threshold : int, optional
            threshold to judge increasing
        """
        return ((curr_tap.get_opacity_confidence() < threshold) and 
                        (next_tap.get_opacity_confidence() >= threshold))

    def __fix_types_on_new_actions(self, actions):
        """
        Makes sure that clicks and long clicks are classified correctly based
        on the number of frames that constitutes a long click.

        Parameters
        ----------
        actions : list of actions
            actions to fix types on
        
        Returns
        -------
        actions : list of actions
            actions with newly assigned types
        """
        for action in actions:
            action_type = action.get_type()
            # classify actions with fewer frames than threshold as clicks
            if (action_type != ActionType.SWIPE) and (len(action.get_taps()) < LONG_CLICK_FRAMES):
                action.set_type(ActionType.CLICK)
            # else as long clicks
            elif (action_type != ActionType.SWIPE):
                action.set_type(ActionType.LONG_CLICK)
        return actions

    def group_by_complex_action(self):
        """
        Ensures that list of GUIActions is accurate for swipes and other complex
        actions. Filters groups based on this.
        """
        new_actions = []
        current = self.detected_actions[0]

        for i in range(1, len(self.detected_actions)):
            next_action = self.detected_actions[i]
            # check if it makes sense to make actions into complex actions
            if (self.__is_valid_type_action_merge(current, next_action) 
                and GeneralUtils.are_consecutive_frames(current, next_action) 
                and GeneralUtils.close_complex_actions(current, next_action, DISTANCE_MERGE_COMPLEX)):
                # combine taps, frames and change the type of the action
                current.get_taps().extend(next_action.get_taps())
                current.get_frames().extend(next_action.get_frames())
                current.set_type(ActionType.SWIPE)
            else:
                new_actions.append(current)
                current = next_action
        
        # take care of last action
        new_actions.append(current)
        self.detected_actions = new_actions

    def __is_valid_type_action_merge(self, action1, action2):
        """
        Determine if merging the actions is valid based on their types. You can
        merge a click and a swipe because separating them may have been a mistake.

        Parameters
        ----------
        action1 : GUIAction
            first action to potentially merge
        action2 : GUIAction
            next action to potentially merge

        Returns
        -------
        bool : bool
            if actions can be merged based on their types
        """
        # can merge a click, swipe or a swipe, click
        type_1 = action1.get_type()
        type_2 = action2.get_type()
        return (((type_1 == ActionType.CLICK) and (type_2 == ActionType.SWIPE)) 
            or ((type_1 == ActionType.SWIPE) and (type_2 == ActionType.CLICK)))
    
    def refine_gui_action_detections(self):
        """
        Takes detected GUIActions and further filters these to ensure they are
        as accurate as possible. Includes grouping further by opacity and by
        complex actions.
        """
        # complete more accuracy procedures
        # filter out actions that overlap with complex actions (swipes)

        # isolate swipes
        swipes = [action for action in self.detected_actions if action.get_type() == ActionType.SWIPE]
        remove = []
        for action in self.detected_actions:
            for swipe in swipes:
                swipe_frames = swipe.get_frames()
                act_frames = action.get_frames()
                # if a swipe is marked as starting before the action but ends after
                # the action, remove the action
                if ((swipe_frames[0] < act_frames[0]) and 
                    (swipe_frames[len(swipe_frames)-1] > act_frames[len(act_frames)-1])):
                    remove.append(action)
        # remove the elements in remove from detected actions
        self.detected_actions = [x for x in self.detected_actions if x not in remove]
        remove.clear()

        for action in self.detected_actions:
            total = 0
            taps = action.get_taps()
            # remove groups with very low opacity because they may not be real taps
            for tap in taps:
                # add up all average opacities across group
                total += tap.get_opacity_confidence() / len(taps)
            if (total != 0 and (total < 1.e-3 or (1-total) < 1.e-3) and (action.get_type() == ActionType.LONG_CLICK)):
                remove.append(action)
            
            # fix swipes to only include taps that move a lot of distance
            if action.get_type() == ActionType.SWIPE:
                counter = 0
                for i in range(len(taps)-1, 0, -1):
                    tap_last = taps[i]
                    tap_before = taps[i-1]
                    if GeneralUtils.get_distance(tap_last, tap_before) < 10:
                        counter += 1
                    else:
                        break

                # remove taps past counter
                action.set_taps(taps[0:len(taps)-counter])
                frames = action.get_frames()
                action.set_frames(frames[0:len(frames)-counter])
        # remove all actions that are in remove
        self.detected_actions = [x for x in self.detected_actions if x not in remove]

    def get_touch_detections(self):
        """
        Returns touch_detections.

        Returns
        -------
        touch_detections : list of Frames
            detected touches from phase 1
        """
        return self.touch_detections

    def set_touch_detections(self, dets):
        """
        Changes touch detections to the specified value.

        Parameters
        ----------
        dets : list of Frames
            new touch detections
        """
        self.touch_detections = dets

    def get_detected_actions(self):
        """
        Returns detected actions.

        Returns
        -------
        detected_actions : list of GUIActions
            classified actions
        """
        return self.detected_actions

    def set_detected_actions(self, actions):
        """
        Changes detected actions to specified value.

        Parameters
        ----------
        actions : list of GUIActions
            new GUIAction list
        """
        self.detected_actions = actions
