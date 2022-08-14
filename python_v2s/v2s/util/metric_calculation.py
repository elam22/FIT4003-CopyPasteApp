# metric_calculation.py

# https://github.com/ztane/python-Levenshtein/
from Levenshtein import distance as l_dist

from util.event import ActionType, Event, GUIAction

class MetricCalculator():
    """
    Class containing methods to calculate metrics for V2S. Can be calculated
    after Phase 2 or after Phase 3 using either Actions generated in Phase 2
    or Events generated in Phase 3.

    Methods
    -------
    calculate_lev_dist(det, truth)
        Calculates Levenshtein distance metric based on event/action sequence.
    calculate_lcs(det, truth)
        Calculates longest common substring metric based on event/action sequence.
    lcsubstring(x, y, m, n) 
        Calculates the longest common substring between x and y sequences.
    calculate_precision_and_recall(det, truth)
        Calculates precision and recall metrics based on event/action sequence.
    __precision_and_recall(det_info, truth_info)
        Calculate precision and recall metrics. Private method allows
        calculate_all_metrics to not have to repeat work.
    __execute_p_r_calc(tp, fp, gt)
        Using false positives, true positives, and ground truth measures,
        calculates precision and recall.
    calculate_all_metrics(det, truth)
        Calculates all metrics based on event/action sequence.
    __get_action_information(det, truth)
        Returns dictionary with string depictions and counts of detected
        and ground truth events/actions.
    __event_string(events):
        Outputs string information if input is a sequence of events.
    __action_string(actions):
        Outputs string information if input is a sequence of actions.
    """

    @staticmethod
    def calculate_lev_dist(det, truth):
        """
        Calculates Levenshtein Distance metric based on action sequence. 
        Measures the difference between two strings.

        Parameters
        ----------
        det : 
            detected sequence of actions/events
        truth : 
            ground truth action/event sequence

        Returns
        -------
        l_dist ; 
            Levenshtein distance calculation
        """
        det_info, truth_info = MetricCalculator.__get_action_information(det, truth)
        det_sequence = det_info["sequence"]
        truth_sequence = truth_info["sequence"]
        # to be continued
        distance = l_dist(det_sequence, truth_sequence)
        return distance

    @staticmethod
    def calculate_lcs(det, truth):
        """
        Calculates longest common substring metric based on action/event sequence.

        Parameters
        ----------
        det : 
            detected sequence of actions/events
        truth : 
            ground truth action/event sequence

        Returns
        -------
        lcs_metric : 
            longest common substring calculation
        """
        det_info, truth_info = MetricCalculator.__get_action_information(det, truth)
        det_sequence = det_info["sequence"]
        det_click_count = det_info["clicks"]
        det_long_click_count = det_info["long_clicks"]
        det_swipe_count = det_info["swipes"]
        truth_sequence = truth_info["sequence"]
        lcs = MetricCalculator.lcsubstring(det_sequence, truth_sequence, 
                                           len(det_sequence), len(truth_sequence))
        lcs_metric = lcs / (det_click_count + det_long_click_count + det_swipe_count);

    @staticmethod
    def lcsubstring(x, y, m, n):
        """
        Calculates the longest common substring between x and y sequences.

        Parameters
        ----------
        x : 
            first string
        y : 
            second string
        m : 
            length of first string
        n : 
            length of second string

        Returns
        -------
        lcs : 
            computed lcs value
        """
        # Create a table to store lengths of longest common suffixes of 
        # substrings. Note that lcstuff[i][j] contains length of longest 
        # common suffix of X[0..i-1] and Y[0..j-1]. The first row and 
        # first column entries have no logical meaning, they are used only 
        # for simplicity of program 
        
        # lcstuff is initialized to None
        lcstuff =  [[None for i in range(0, n+2)] for i in range(0, m+2)]
        result = 0  # To store length of the longest common substring 
          
        # Following steps build lcstuff[m+1][n+1] in bottom up fashion 
        for i in range(0, m+1):
            for j in range(0, n+1): 
                if i == 0 or j == 0:
                    lcstuff[i][j] = 0
                elif x[i - 1] == y[j - 1]:
                    lcstuff[i][j] = lcstuff[i - 1][j - 1] + 1
                    result = max(result, lcstuff[i][j])
                else:
                    lcstuff[i][j] = 0
        return result

    @staticmethod
    def calculate_precision_and_recall(det, truth):
        """
        Calculates precision and recall metrics based on action/event sequence.

        Parameters
        ----------
        det : 
            detected sequence of events
        truth :
            ground truth action sequence

        Returns
        -------
        dict of metrics : 
            precision and recall calculations
        """
        det_info, truth_info = MetricCalculator.__get_action_information(det, truth)
        result = MetricCalculator.__precision_and_recall(det_info, truth_info)
        return result

    @staticmethod
    def __precision_and_recall(det_info, truth_info):
        """
        Calculate precision and recall metrics. Private method allows
        calculate_all_metrics to not have to repeat work.

        Parameters
        ----------
        det_info : 
            information about detected sequence of actions/events
        truth_info : 
            ground truth information about action/event sequence

        Returns
        -------
        dict of metrics : 
            precision and recall calculations
        """        
        # get access to information
        det_click_count = det_info["clicks"]
        det_long_click_count = det_info["long_clicks"]
        det_swipe_count = det_info["swipes"]
        truth_click_count = truth_info["clicks"]
        truth_long_click_count = truth_info["long_clicks"]
        truth_swipe_count = truth_info["swipes"]

        # fp = false positive
        # tp = true positive
        # t_gt = ground truth
        fp_c = 0
        fp_lc = 0
        fp_sw = 0
        tp_c = 0
        tp_lc = 0
        tp_sw = 0

        temp_clicks = truth_click_count - det_click_count
        temp_lclicks = truth_long_click_count - det_long_click_count
        temp_swipes = truth_swipe_count - det_swipe_count
        t_gt_c = truth_click_count
        t_gt_lc = truth_long_click_count
        t_gt_sw = truth_swipe_count
        # if negative fp
        if temp_clicks < 0: 
            # fewer clicks detected than actually occur
            tp_c = tp_c + truth_click_count
            fp_c = fp_c + (-1 * temp_clicks)
        else:
            # same or more clicks detected than occur
            tp_c = tp_c + det_click_count
            fp_c = fp_c + temp_clicks
        # if negative fp
        if temp_lclicks < 0:
            # fewer lclicks detected than actually occur
            tp_lc = tp_lc + truth_long_click_count
            fp_lc = fp_lc + (-1 * temp_lclicks)
        else:
            # same or more lclicks detected than occur
            tp_lc = tp_lc + det_long_click_count
            fp_lc = fp_lc + temp_lclicks
        # if negative fp
        if temp_swipes < 0:
            # fewer swipes detected than actually occur
            tp_sw = tp_sw + truth_swipe_count
            fp_sw = fp_sw + (-1 * temp_swipes)
        else:
            # same or more swipes detected than occur
            tp_sw = tp_sw + det_swipe_count
            fp_sw = fp_sw + temp_swipes

        # calculations
        p_click, r_click = MetricCalculator.__execute_p_r_calc(tp_c, fp_c, t_gt_c)
        p_lclick, r_lclick = MetricCalculator.__execute_p_r_calc(tp_lc, fp_lc, t_gt_lc)
        p_swipe, r_swipe = MetricCalculator.__execute_p_r_calc(tp_sw, fp_sw, t_gt_sw)

        result = {"prec_clicks": p_click, "rec_clicks": r_click, 
                  "prec_lclicks": p_lclick, "rec_lclicks": r_lclick, 
                  "prec_swipes": p_swipe, "rec_swipes": r_swipe}
        return result


    @staticmethod
    def __execute_p_r_calc(tp, fp, gt):
        """
        Using false positives, true positives, and ground truth measures,
        calculates precision and recall.

        Parameters
        ----------
        tp :
            number of true positives detected
        fp : 
            number of false positives detected
        gt : 
            true number of actions/events

        Returns
        -------
        (precision, recall) : tuple
            calculated p and r values
        """
        # correct division by zero errors
        try:
            precision = tp / (tp+fp)
        except ZeroDivisionError:
            precision = 1.0
        try:
            recall = tp / (gt)
        except ZeroDivisionError:
            recall = 1.0
        finally:
            return precision, recall


    @staticmethod
    def calculate_all_metrics(det, truth):
        """
        Calculates all metrics based on action/event sequence.

        Parameters
        ----------
        det : 
            detected sequence of actions/events
        truth : 
            ground truth action/event sequence

        Returns
        -------
        dict : 
            metric string : value entries
        """
        det_info, truth_info = MetricCalculator.__get_action_information(det, truth)
        det_sequence = det_info["sequence"]
        det_click_count = det_info["clicks"]
        det_long_click_count = det_info["long_clicks"]
        det_swipe_count = det_info["swipes"]
        truth_sequence = truth_info["sequence"]
        
        # precision and recall
        result = MetricCalculator.__precision_and_recall(det_info, truth_info)
        
        # longest common substring
        lcs = MetricCalculator.lcsubstring(det_sequence, truth_sequence, 
                                           len(det_sequence), len(truth_sequence))
        lcs_metric = lcs / (det_click_count + det_long_click_count + det_swipe_count);

        # Levenshtein distance
        distance = l_dist(det_sequence, truth_sequence)

        # add other calculations to the resulting dictionary from p & r calcs
        result["l_dist"] = distance
        result["lcs"] = lcs_metric
        return result

    @staticmethod
    def __get_action_information(det, truth):
        """
        Returns dictionary with string depictions and counts of detected
        and ground truth action/event. Can handle input of event or action for
        both det and truth inputs.

        Parameters
        ----------
        det : 
            detected sequence of action/event
        truth : 
            ground truth action/event sequence

        Returns
        -------
        (det_info, truth_info) : 
            tuple of action sequence information dictionaries
        """
        det_sequence = ""
        truth_sequence = ""
        det_click_count = 0
        det_long_click_count = 0
        det_swipe_count = 0
        truth_click_count = 0
        truth_long_click_count = 0
        truth_swipe_count = 0
        # calculate detected values
        if isinstance(det[0], Event):
            (det_sequence, det_click_count, det_long_click_count, 
            det_swipe_count) = MetricCalculator.__event_string(det)
        else:
            (det_sequence, det_click_count, det_long_click_count, 
            det_swipe_count) = MetricCalculator.__action_string(det)
        
        
        # depending on how the ground truth information is created, this may
        # need to change to read information in also
        # calculate truth values
        if isinstance(truth[0], GUIAction):
            (truth_sequence, truth_click_count, truth_long_click_count, 
            truth_swipe_count) = MetricCalculator.__action_string(truth)
        else:
            (truth_sequence, truth_click_count, truth_long_click_count, 
            truth_swipe_count) = MetricCalculator.__action_string(truth)
        
        det_info = {"sequence": det_sequence, "clicks": det_click_count, 
                    "long_clicks": det_long_click_count, 
                    "swipes": det_swipe_count}
        truth_info = {"sequence": truth_sequence, "clicks": truth_click_count, 
                      "long_clicks": truth_long_click_count, 
                      "swipes": truth_swipe_count}
        return (det_info, truth_info)

    @staticmethod
    def __event_string(events):
        """
        Outputs string information if input is a sequence of events.

        Parameters
        ----------
        events : list of Events
            events input to metric calculator

        Returns
        -------
        (sequence, count_c, count_lc, count_sw) : (string, int, int, int)
            string representing event sequence, then counts of each event type
        """
        sequence = ""
        count_c = 0
        count_lc = 0
        count_sw = 0

        for event in events:
    	    if not event.is_delay():
	            if event.get_event_label() == "CLICK":
	                count_c += 1
	                sequence += "0"
	            elif event.getEvent_label() == "LONG_CLICK":
                	count_lc += 1
	                sequence += "1"
	            elif event.getEvent_label() == "SWIPE":
	                count_sw += 1
	                sequence += "2"
        return sequence, count_c, count_lc, count_sw

    @staticmethod
    def __action_string(actions):
        """
        Outputs string information if input is a sequence of gui actions.

        Parameters
        ----------
        actions : list of GUIActions
            actions input to metric calculator

        Returns
        -------
        (sequence, count_c, count_lc, count_sw) : (string, int, int, int)
            string representing action sequence, then counts of each action type
        """
        sequence = ""
        count_c = 0
        count_lc = 0
        count_sw = 0

        for action in actions:
            if action.get_type() == ActionType.CLICK:
                count_c += 1
                sequence += "0"
            elif action.get_type() == ActionType.LONG_CLICK:
                count_lc += 1
                sequence += "1"
            elif action.get_type() == ActionType.SWIPE:
                count_sw += 1
                sequence += "2"

        return sequence, count_c, count_lc, count_sw

