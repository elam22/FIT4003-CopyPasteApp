package com.example.myaccessibilityservice;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.AssetManager;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.media.AudioManager;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.Button;
import android.widget.FrameLayout;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

public class MyAccessibilityService extends AccessibilityService {

    FrameLayout mLayout;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
    }

    @Override
    public void onInterrupt() {
    }

    private void configurePowerButton() {
        Button powerButton = (Button) mLayout.findViewById(R.id.power);
        powerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                performGlobalAction(GLOBAL_ACTION_POWER_DIALOG);
            }
        });
    }

//    private void configureVolumeButton() {
//        Button volumeUpButton = (Button) mLayout.findViewById(R.id.volume_up);
//        volumeUpButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                AudioManager audioManager = (AudioManager) getSystemService(AUDIO_SERVICE);
//                audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC,
//                        AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI);
//            }
//        });
//    }

    private AccessibilityNodeInfo findScrollableNode(AccessibilityNodeInfo root) {
        Deque<AccessibilityNodeInfo> deque = new ArrayDeque<>();
        deque.add(root);
        while (!deque.isEmpty()) {
            AccessibilityNodeInfo node = deque.removeFirst();
            if (node.getActionList().contains(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)) {
                return node;
            }
            for (int i = 0; i < node.getChildCount(); i++) {
                deque.addLast(node.getChild(i));
            }
        }
        return null;
    }

    private AccessibilityNodeInfo findBatteryNode(AccessibilityNodeInfo root){
        Deque<AccessibilityNodeInfo> deque = new ArrayDeque<>();
        deque.add(root);
        AccessibilityNodeInfo nodeWanted = null;
        while (!deque.isEmpty()) {
            AccessibilityNodeInfo node = deque.removeFirst();
            System.out.println(node.getText());
            if (node.getText() != null) {
                if (node.getText().equals("Log In")) {
                    nodeWanted = node;
                } else {
                    for (int i = 0; i < node.getChildCount(); i++) {
                        deque.addLast(node.getChild(i));
                    }
                }
            } else {
                for (int i = 0; i < node.getChildCount(); i++) {
                    deque.addLast(node.getChild(i));
                }
            }
        }
        if (nodeWanted != null){
            while (true){
                if (nodeWanted.getActionList().contains(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK)){
                    return nodeWanted;
                }
                else{
                    nodeWanted = nodeWanted.getParent();
                }
            }
        }


        return null;
    }

    private AccessibilityNodeInfo findBatterySaverNode(AccessibilityNodeInfo root){
        Deque<AccessibilityNodeInfo> deque = new ArrayDeque<>();
        deque.add(root);
        AccessibilityNodeInfo nodeWanted = null;
        while (!deque.isEmpty()) {
            AccessibilityNodeInfo node = deque.removeFirst();
            System.out.println(node.getText());
            if (node.getText() != null) {
                if (node.getText().equals("Create New Facebook Account")) {
                    nodeWanted = node;
                } else {
                    for (int i = 0; i < node.getChildCount(); i++) {
                        deque.addLast(node.getChild(i));
                    }
                }
            } else {
                for (int i = 0; i < node.getChildCount(); i++) {
                    deque.addLast(node.getChild(i));
                }
            }
        }
        if (nodeWanted != null){
            while (true){
                if (nodeWanted.getActionList().contains(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK)){
                    return nodeWanted;
                }
                else{
                    nodeWanted = nodeWanted.getParent();
                }
            }
        }


        return null;
    }

    private AccessibilityNodeInfo findNode(AccessibilityNodeInfo root, String nodeText){
        Deque<AccessibilityNodeInfo> deque = new ArrayDeque<>();
        deque.add(root);
        AccessibilityNodeInfo nodeWanted = null;
        while (!deque.isEmpty()) {
            AccessibilityNodeInfo node = deque.removeFirst();
            System.out.println(node.getText());
            if (node.getText() != null) {
                if (node.getText().equals(nodeText)) {
                    nodeWanted = node;
                } else {
                    for (int i = 0; i < node.getChildCount(); i++) {
                        deque.addLast(node.getChild(i));
                    }
                }
            } else {
                for (int i = 0; i < node.getChildCount(); i++) {
                    deque.addLast(node.getChild(i));
                }
            }
        }
        if (nodeWanted != null){
            while (true){
                if (nodeWanted.getActionList().contains(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK)) {
                    return nodeWanted;
                } else {
                    nodeWanted = nodeWanted.getParent();
                }
            }
        }


        return null;
    }

//    private void configureScrollButton() {
//        Button scrollButton = (Button) mLayout.findViewById(R.id.scroll);
//        scrollButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                AccessibilityNodeInfo scrollable = findScrollableNode(getRootInActiveWindow());
//                if (scrollable != null) {
//                    scrollable.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD.getId());
//                }
//            }
//        });
//    }

//    private void configureFacebookForgetPasswordButton() {
//        Button scrollButton = (Button) mLayout.findViewById(R.id.scroll);
//        scrollButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                AccessibilityNodeInfo node = findNode(getRootInActiveWindow(), "Login");
//                if (node != null) {
//                    node.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK.getId());
//                }
//                sleep(3000);
//                node = findNode(getRootInActiveWindow(), "Forgot Password?");
//                if (node != null){
//                    node.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK.getId());
//                }
//            }
//        });
//    }

//    private void configureSwipeButton() {
//        Button swipeButton = (Button) mLayout.findViewById(R.id.swipe);
//        swipeButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                Path swipePath = new Path();
//                swipePath.moveTo(1000, 1000);
//                swipePath.lineTo(100, 1000);
//                GestureDescription.Builder gestureBuilder = new GestureDescription.Builder();
//                gestureBuilder.addStroke(new GestureDescription.StrokeDescription(swipePath, 0, 500));
//                dispatchGesture(gestureBuilder.build(), null, null);
//            }
//        });
//    }

//    private void configureContinuousButton() {
//        Button swipeButton = (Button) mLayout.findViewById(R.id.volume_up);
//        swipeButton.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                Path dragRightPath = new Path();
//                dragRightPath.moveTo(100, 1000);
//                dragRightPath.lineTo(1000, 1000);
//                long dragRightDuration = 500; // 0.5 second
//
//                // The starting point of the second path must match
//                // the ending point of the first path.
//                Path dragDownPath = new Path();
//                dragDownPath.moveTo(1000, 1000);
//                dragDownPath.lineTo(1000, 1400);
//                long dragDownDuration = 500 ;
//                GestureDescription.StrokeDescription right =
//                        new GestureDescription.StrokeDescription(dragRightPath, 0,
//                                dragRightDuration);
//
//                GestureDescription.Builder gestureBuilderRight = new GestureDescription.Builder();
//                gestureBuilderRight.addStroke(right);
//                dispatchGesture(gestureBuilderRight.build(), null, null);
////                Log.i("act_type", rightThenDownDrag.getPath().addPath(););
//
//                sleep(1000);
//                GestureDescription.StrokeDescription down =
//                        new GestureDescription.StrokeDescription(dragDownPath, dragRightDuration,
//                                dragDownDuration);
//
//                GestureDescription.Builder gestureBuilderDown = new GestureDescription.Builder();
//                gestureBuilderDown.addStroke(down);
//                dispatchGesture(gestureBuilderDown.build(), null, null);
//            }
//        });
//    }

    private void configureDoActionButton() {
        Button swipeButton = (Button) mLayout.findViewById(R.id.power);
        swipeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String json;
                JSONArray jsonArray = null;
                try {

                    SharedPreferences sharedPref = getSharedPreferences("ACTIONS", 0);
                    String detectedActions = sharedPref.getString("ACTION_RESULT", "default");
                    Log.i("detectedActions", detectedActions);
                    AssetManager assetManager = getAssets();
                    InputStream is = assetManager.open("actions.json");
                    int size = is.available();
                    byte[] buffer = new byte[size];
                    is.read(buffer);
                    is.close();

                    json = new String(buffer, StandardCharsets.UTF_8);
                    jsonArray = new JSONArray(json);

                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject action = jsonArray.getJSONObject(i);
                        String act_type = action.getString("act_type");
                        if (act_type.equals("CLICK")) {
                            JSONObject tap = (JSONObject) action.getJSONArray("taps").get(0);
                            int x = tap.getInt("x");
                            int y = tap.getInt("y");

                            Log.i("tap", tap.getClass().toString());
                            Log.i("tap", tap.toString());
//                            Log.i("tap", String.valueOf(x));
//                            Log.i("tap", String.valueOf(y));
                            singleTapAt(x, y);
                            Thread.sleep(5000);
//                            sleep(3000);

                            AccessibilityNodeInfo currentNode=getRootInActiveWindow();
                            String content = "";
                            //System.out.println("going in to findContent function");
                            content = findContent(currentNode, content);
                            System.out.println("content: " + content);
                            content = filterNoise(content);
                            System.out.println("filteredContent: " + content);

                            // read return data and compare to get similarity
                            String result = "SearchsettingsNetworkinternetWiFimobiledatausageandhotspotLoOConnecteddevicesBluetoothAppsnotificationsRecentappsdefaultappsBatteryDisplayWallpapersleepfontsizeSoundVolumevibrationDoNotDisturbStorageusedGBfreePrivacyPermissionsaccountactivitypersonaldataLocation";
                            int similarCharacterCount = lcsCount(result, content);
                            int similarity = similarCharacterCount*100/result.length();
                            System.out.println("Similarity = " + similarity + "%\n");

                            if (similarity > 90){
                                System.out.println("Correct");
                            }

                        } else if (act_type.equals("SWIPE")) {
                            JSONArray taps = action.getJSONArray("taps");
                            JSONObject swipeStart = (JSONObject) taps.get(0);
                            JSONObject swipeEnd = (JSONObject) taps.get(taps.length() - 1);
                            int xStart = swipeStart.getInt("x");
                            int yStart = swipeStart.getInt("y");

                            int xEnd = swipeEnd.getInt("x");
                            int yEnd = swipeEnd.getInt("y");
//
                            swipe(xStart, yStart, xEnd, yEnd);
                            Thread.sleep(5000);
                        } else if(act_type.equals("LONG_CLICK")){
                            JSONObject tap = (JSONObject) action.getJSONArray("taps").get(0);
                            int x = tap.getInt("x");
                            int y = tap.getInt("y");

                            Log.i("tap", tap.getClass().toString());
                            Log.i("tap", tap.toString());
//                            Log.i("tap", String.valueOf(x));
//                            Log.i("tap", String.valueOf(y));
                            longTapAt(x, y);
                            Thread.sleep(5000);
                        }
                    }
                    Log.i("tap", "done");

                } catch (IOException | JSONException | InterruptedException e) {
                    e.printStackTrace();
                }

            }
        });
    }

    private void singleTapAt(int x, int y) {
        Path touchPath = new Path();
        touchPath.moveTo(x, y);
        touchPath.lineTo(x + 5, y + 5);
        GestureDescription.Builder gestureBuilder = new GestureDescription.Builder();
        gestureBuilder.addStroke(new GestureDescription.StrokeDescription(touchPath, 0, 200));
        dispatchGesture(gestureBuilder.build(), null, null);
    }

    private void swipe(int x, int y, int toX, int toY) {
        Path touchPath = new Path();
        touchPath.moveTo(x, y);
        touchPath.lineTo(toX, toY);
        GestureDescription.Builder gestureBuilder = new GestureDescription.Builder();
        gestureBuilder.addStroke(new GestureDescription.StrokeDescription(touchPath, 0, 500));
        dispatchGesture(gestureBuilder.build(), null, null);
    }

    private void longTapAt(int x, int y){
        Path clickPath = new Path();
        clickPath.moveTo(x, y);
        GestureDescription.StrokeDescription clickStroke = new GestureDescription.StrokeDescription(clickPath, 0, 1, true);
        GestureDescription.Builder clickBuilder = new GestureDescription.Builder();
        clickBuilder.addStroke(clickStroke);
        dispatchGesture(clickBuilder.build(), null, null);
    }

    private String findContent(AccessibilityNodeInfo currentNode, String content){
        //System.out.println("currently in findContent Function");
        Rect rect = new Rect();
        if (currentNode.getText() != null)
        {
            currentNode.getBoundsInScreen(rect);
//            System.out.println(currentNode.getText().toString());
//            System.out.println("bottom: "+rect.bottom);
//            System.out.println("left: "+rect.left);
//            System.out.println("right: "+rect.right);
//            System.out.println("top: "+rect.top);
            if (rect.top < rect.bottom)
            {
                content += currentNode.getText().toString();
                //System.out.println("success get: "+currentNode.getText().toString());
            }
        }
        for (int i = 0; i < currentNode.getChildCount(); i++){
            content = findContent(currentNode.getChild(i), content);
        }

        return content;
    }

    private String filterNoise(String content){
        String string = "";
        for (int i = 0; i < content.length(); i++){
            int currentCharValue = (int) content.charAt(i);
            if (((65 <= currentCharValue) && (currentCharValue <=90)) || (((97 <= currentCharValue) && (currentCharValue <=122)))){
                string += content.charAt(i);

            }
        }
        return string;
    }

    /* Returns length of LCS for ocr[0..m-1], acc[0..n-1] */
    private int lcsCount( String ocr, String acc)
    {
        char[] X = ocr.toCharArray();
        char[] Y = acc.toCharArray();
        int m = X.length;
        int n = Y.length;
        int L[][] = new int[m+1][n+1];

        /* Following steps build L[m+1][n+1] in bottom up fashion. Note
        that L[i][j] contains length of LCS of X[0..i-1] and Y[0..j-1] */
        for (int i=0; i<=m; i++)
        {
            for (int j=0; j<=n; j++)
            {
                if (i == 0 || j == 0)
                    L[i][j] = 0;
                else if (X[i-1] == Y[j-1])
                    L[i][j] = L[i-1][j-1] + 1;
                else
                    L[i][j] = Math.max(L[i-1][j], L[i][j-1]);
            }
        }
        return L[m][n];
    }

    private void lcs(String X, String Y)
    {
        int m = X.length();
        int n = Y.length();
        int[][] L = new int[m+1][n+1];

        // Following steps build L[m+1][n+1] in bottom up fashion. Note
        // that L[i][j] contains length of LCS of X[0..i-1] and Y[0..j-1]
        for (int i=0; i<=m; i++)
        {
            for (int j=0; j<=n; j++)
            {
                if (i == 0 || j == 0)
                    L[i][j] = 0;
                else if (X.charAt(i-1) == Y.charAt(j-1))
                    L[i][j] = L[i-1][j-1] + 1;
                else
                    L[i][j] = Math.max(L[i-1][j], L[i][j-1]);
            }
        }

        // Following code is used to print LCS
        int index = L[m][n];
        int temp = index;

        // Create a character array to store the lcs string
        char[] lcs = new char[index+1];
        lcs[index] = '\u0000'; // Set the terminating character

        // Start from the right-most-bottom-most corner and
        // one by one store characters in lcs[]
        int i = m;
        int j = n;
        while (i > 0 && j > 0)
        {
            // If current character in X[] and Y are same, then
            // current character is part of LCS
            if (X.charAt(i-1) == Y.charAt(j-1))
            {
                // Put current character in result
                lcs[index-1] = X.charAt(i-1);

                // reduce values of i, j and index
                i--;
                j--;
                index--;
            }

            // If not same, then find the larger of two and
            // go in the direction of larger value
            else if (L[i-1][j] > L[i][j-1])
                i--;
            else
                j--;
        }

        // Print the lcs
        System.out.print("LCS of "+X+" and "+Y+" is ");
        for(int k=0;k<=temp;k++)
            System.out.print(lcs[k]);
    }

//    private int EditDistDP(String str1, String str2)
//    {
//        int len1 = str1.length();
//        int len2 = str2.length();
//
//        // Create a DP array to memoize result
//        // of previous computations
//        int [][]DP = new int[2][len1 + 1];
//
//
//        // Base condition when second String
//        // is empty then we remove all characters
//        for (int i = 0; i <= len1; i++)
//            DP[0][i] = i;
//
//        // Start filling the DP
//        // This loop run for every
//        // character in second String
//        for (int i = 1; i <= len2; i++)
//        {
//
//            // This loop compares the char from
//            // second String with first String
//            // characters
//            for (int j = 0; j <= len1; j++)
//            {
//
//                // if first String is empty then
//                // we have to perform add character
//                // operation to get second String
//                if (j == 0)
//                    DP[i % 2][j] = i;
//
//                    // if character from both String
//                    // is same then we do not perform any
//                    // operation . here i % 2 is for bound
//                    // the row number.
//                else if (str1.charAt(j - 1) == str2.charAt(i - 1)) {
//                    DP[i % 2][j] = DP[(i - 1) % 2][j - 1];
//                }
//
//                // if character from both String is
//                // not same then we take the minimum
//                // from three specified operation
//                else {
//                    DP[i % 2][j] = 1 + Math.min(DP[(i - 1) % 2][j],
//                            Math.min(DP[i % 2][j - 1],
//                                    DP[(i - 1) % 2][j - 1]));
//                }
//            }
//        }
//
//        // after complete fill the DP array
//        // if the len2 is even then we end
//        // up in the 0th row else we end up
//        // in the 1th row so we take len2 % 2
//        // to get row
//        System.out.print(DP[len2 % 2][len1] +"\n");
//        return(DP[len2 % 2][len1]);
//    }

    @SuppressLint("RtlHardcoded")
    protected void onServiceConnected() {
        // Create an overlay and display the action bar

        WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        mLayout = new FrameLayout(this);
        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT, // Overlay must be full screen otherwise my trick will not work
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, // Allow another windows to receive touch events
                PixelFormat.TRANSLUCENT);
        lp.gravity = Gravity.CENTER | Gravity.LEFT;
        LayoutInflater inflater = LayoutInflater.from(this);
        inflater.inflate(R.layout.action_bar, mLayout);
        wm.addView(mLayout, lp);

//        WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);
//        mLayout = new FrameLayout(this);
//        WindowManager.LayoutParams lp = new WindowManager.LayoutParams();
//        lp.type = WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY;
//        lp.format = PixelFormat.TRANSLUCENT;
//        lp.flags |= WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
//        lp.width = WindowManager.LayoutParams.WRAP_CONTENT;
//        lp.height = WindowManager.LayoutParams.WRAP_CONTENT;
//        lp.gravity = Gravity.TOP;
//        LayoutInflater inflater = LayoutInflater.from(this);
//        inflater.inflate(R.layout.action_bar, mLayout);
//        wm.addView(mLayout, lp);

        configureDoActionButton();
//        configureContinuousButton();
//        configureScrollButton();
//        configureSwipeButton();

    }
}