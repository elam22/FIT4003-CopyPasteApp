package com.example.myaccessibilityservice;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.ContentUris;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.ImageDecoder;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.Log;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.TimeUnit;

import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;


public class MainActivity extends AppCompatActivity {
    private static final int PERMISSION_REQUEST_CODE = 1;
    String selectedImagePath;
    int REQUEST_CODE = 3;
    EditText ipv4AddressView;
    String ipv4AddressAndPort = "192.168.20.27:8080";
    RequestBody requestBody;
    String postUrl;
    String getUrl;
    TextView responseText;
    Bitmap bitmap1;
    Bitmap bitmap2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ipv4AddressView = findViewById(R.id.IPAddress);
//        ipv4AddressAndPort = ipv4AddressView.getText().toString();
        responseText = findViewById(R.id.responseText);
        SharedPreferences sharedPref = getSharedPreferences("ACTIONS", 0);
        getUrl = sharedPref.getString("URL", null);

        if (!Environment.isExternalStorageManager()){
            Intent getpermission = new Intent();
            getpermission.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
            startActivity(getpermission);
        }

      }

    public static String getPath(final Context context, final Uri uri) {

        final boolean isKitKat = Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT;

        // DocumentProvider
        if (isKitKat && DocumentsContract.isDocumentUri(context, uri)) {
            // ExternalStorageProvider
            if (isExternalStorageDocument(uri)) {
                final String docId = DocumentsContract.getDocumentId(uri);
                final String[] split = docId.split(":");
                final String type = split[0];

                if ("primary".equalsIgnoreCase(type)) {
                    return Environment.getExternalStorageDirectory() + "/" + split[1];
                }

                // TODO handle non-primary volumes
            }
            // DownloadsProvider
            else if (isDownloadsDocument(uri)) {

                final String id = DocumentsContract.getDocumentId(uri);
//                final Uri contentUri = ContentUris.withAppendedId(
//                        Uri.parse("content://downloads/public_downloads"), Long.valueOf(id));
//
//                return getDataColumn(context, contentUri, null, null);
                if (!TextUtils.isEmpty(id)) {
                    if (id.startsWith("raw:")) {
                        return id.replaceFirst("raw:", "");
                    }
                    try {
                        final Uri contentUri = ContentUris.withAppendedId(
                                Uri.parse("content://downloads/public_downloads"), Long.valueOf(id));
                        return getDataColumn(context, contentUri, null, null);
                    } catch (NumberFormatException e) {
                        return null;
                    }
                }
            }
            // MediaProvider
            else if (isMediaDocument(uri)) {
                final String docId = DocumentsContract.getDocumentId(uri);
                final String[] split = docId.split(":");
                final String type = split[0];

                Uri contentUri = null;
                if ("image".equals(type)) {
                    contentUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
                } else if ("video".equals(type)) {
                    contentUri = MediaStore.Video.Media.EXTERNAL_CONTENT_URI;
                } else if ("audio".equals(type)) {
                    contentUri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
                }

                final String selection = "_id=?";
                final String[] selectionArgs = new String[]{
                        split[1]
                };

                return getDataColumn(context, contentUri, selection, selectionArgs);
            }
        }
        // MediaStore (and general)
        else if ("content".equalsIgnoreCase(uri.getScheme())) {
            return getDataColumn(context, uri, null, null);
        }
        // File
        else if ("file".equalsIgnoreCase(uri.getScheme())) {
            return uri.getPath();
        }

        return null;
    }

    public static String getDataColumn(Context context, Uri uri, String selection,
                                       String[] selectionArgs) {

        Cursor cursor = null;
        final String column = "_data";
        final String[] projection = {
                column
        };

        try {
            cursor = context.getContentResolver().query(uri, projection, selection, selectionArgs,
                    null);
            if (cursor != null && cursor.moveToFirst()) {
                final int column_index = cursor.getColumnIndexOrThrow(column);
                return cursor.getString(column_index);
            }
        } finally {
            if (cursor != null)
                cursor.close();
        }
        return null;
    }

    public static boolean isExternalStorageDocument(Uri uri) {
        return "com.android.externalstorage.documents".equals(uri.getAuthority());
    }

    public static boolean isDownloadsDocument(Uri uri) {
        return "com.android.providers.downloads.documents".equals(uri.getAuthority());
    }

    public static boolean isMediaDocument(Uri uri) {
        return "com.android.providers.media.documents".equals(uri.getAuthority());
    }

    public void uploadVideo(View v) {
        postUrl = "http://" + ipv4AddressAndPort + "/";

//        RequestBody postBody = new FormBody.Builder().add("value","hello").build();
//        postRequest(postUrl, postBody);
        if (selectedImagePath != null) {
            File file = new File(selectedImagePath);
            try {
                requestBody = new MultipartBody.Builder()
                        .setType(MultipartBody.FORM)
                        .addFormDataPart("file", file.getName(), RequestBody.create(file, MediaType.parse("video/mp4")))
                        .build();
                Log.i("Upload", String.valueOf(requestBody.contentType()));
                postRequest(postUrl, requestBody);
            } catch (Exception e) {
                e.printStackTrace();
                Log.i("Upload", "failed");

            }
        } else {
            Toast.makeText(getApplicationContext(), "Select a video", Toast.LENGTH_LONG).show();
        }
    }

    void postRequest(String postUrl, RequestBody postBody) {
        OkHttpClient client = new OkHttpClient();

        Request request = new Request.Builder()
                .url(postUrl)
                .post(postBody)
                .build();
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                // Cancel the post on failure.
                call.cancel();

                // In order to access the TextView inside the UI thread, the code is executed inside runOnUiThread()
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
//                        TextView responseText = findViewById(R.id.responseText);
                        responseText.setText("Failed to Connect to Server");
                        Log.i("Upload", String.valueOf(e));
                    }
                });
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                // In order to access the TextView inside the UI thread, the code is executed inside runOnUiThread()
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
//                        TextView responseText = findViewById(R.id.responseText);
                        try {
                            String responseData = response.body().string();
                            JSONArray json = new JSONArray(responseData);
                            String responseTxt = " Failed to upload";
                            JSONObject statusId = null;
                            if (Integer.parseInt(json.get(0).toString()) == 202) {
                                responseTxt = "Successfully uploaded. Please wait the video to be process";
                                statusId = json.getJSONObject(1);
                                Log.i("Json", statusId.getString("Location"));
                                getUrl = "http://" + ipv4AddressAndPort + "/" + statusId.getString("Location");

                                // save to shared preferences
                                SharedPreferences sharedPref = getSharedPreferences("ACTIONS", 0);
                                SharedPreferences.Editor editor = sharedPref.edit();
                                editor.putString("URL", getUrl);
                                editor.apply();
                            }
                            responseText.setText(responseTxt);
                            Toast.makeText(getApplicationContext(), responseText.getText().toString(), Toast.LENGTH_LONG).show();
                            checkProgress(null);
                        } catch (JSONException | IOException e) {
                            e.printStackTrace();
                        }
                    }
                });
            }
        });
    }

    public void selectVideo(View v) {
        if (Build.VERSION.SDK_INT >= 23) {
            if (checkPermission()) {
                pickVideo();
            } else {
                requestPermission();
            }
        } else {
            pickVideo();
        }
    }

    public void pickVideo() {
        Intent intent = new Intent();
        intent.setType("video/mp4");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(intent, REQUEST_CODE);
    }

    @Override
    protected void onActivityResult(int reqCode, int resCode, Intent data) {
        super.onActivityResult(reqCode, resCode, data);
        Log.i("onActivityResult", "In");
        if (resCode == RESULT_OK && data != null && reqCode == REQUEST_CODE) {
            Log.i("onActivityResult", "Good");
            Uri uri = data.getData();
            selectedImagePath = getPath(getApplicationContext(), uri);

            Log.i("onActivityResult", "Path: " + selectedImagePath);
            EditText imgPath = findViewById(R.id.vidPath);
            imgPath.setText(selectedImagePath);
            Toast.makeText(getApplicationContext(), selectedImagePath, Toast.LENGTH_LONG).show();
        }

    }


    private void requestPermission() {
        if (ActivityCompat.shouldShowRequestPermissionRationale(MainActivity.this, Manifest.permission.WRITE_EXTERNAL_STORAGE)) {
            Toast.makeText(MainActivity.this, "Please Give Permission to Upload File", Toast.LENGTH_SHORT).show();
        } else {
            ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, PERMISSION_REQUEST_CODE);
        }
    }

    private boolean checkPermission() {
        int result = ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.WRITE_EXTERNAL_STORAGE);
        return result == PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode) {
            case PERMISSION_REQUEST_CODE:
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(MainActivity.this, "Permission Successfull", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MainActivity.this, "Permission Failed", Toast.LENGTH_SHORT).show();
                }
        }
    }

    public void checkProgress(@Nullable View v) throws IOException {
//        String url_1 = "http://" + ipv4AddressAndPort + "/status/753e71d9-427a-4f50-8527-4fb289b7e42b";
//        Log.i("Json", getUrl);


        Thread thread = new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    while(true){
                        String result = getRequest(getUrl);
                        JSONObject object = new JSONObject(result);
                        String state;
                        try {
                            state = object.getString("state");

                        } catch (Exception e){
                            Thread.sleep(5000);
                            state = object.getString("state");
                        }


                        Log.i("Json", object.getString("state"));

                        //Your code goes here
                        String finalState = state;
                        MainActivity.this.runOnUiThread(new Runnable() {
                            public void run() {
                                responseText.setText(finalState);
                                Toast.makeText(getApplicationContext(), "Result is " + finalState, Toast.LENGTH_LONG).show();
                            }
                        });

                        if (state.equals("SUCCESS")) {
                            JSONArray actions = object.getJSONArray("result");
                            SharedPreferences sharedPref = getSharedPreferences("ACTIONS", 0);
                            SharedPreferences.Editor editor = sharedPref.edit();
                            editor.putString("ACTION_RESULT", actions.toString());
                            editor.apply();
                            Log.i("Json", "state is success, result saved");
                            break;
                        }

                        Thread.sleep(30000);
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        thread.start();


//        while(!result.contains("SUCCESS")){
//            try
//            {
//                Thread.sleep(30000);
//                result = getRequest(getUrl);
//            }
//            catch(InterruptedException ex)
//            {
//                Thread.currentThread().interrupt();
//            }
//        }

    }

    public String getRequest(String url) throws IOException {
        OkHttpClient client = new OkHttpClient().newBuilder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .writeTimeout(10, TimeUnit.SECONDS)
                .readTimeout(300, TimeUnit.SECONDS)
                .build();;

//        final JSONObject[] responseResult = new JSONObject[1];
        Request request = new Request.Builder()
                .url(url)
                .build();
        Response getResponse = client.newCall(request).execute();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                e.printStackTrace();
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                if (!response.isSuccessful()) {
                    throw new IOException("Unexpected code " + response);
                } else {
//                    getResponse.close();
                    response.close();
                    // do something wih the result
                }
            }
        });
        return getResponse.body().string();

    }

    private void pick_image_path(String name, Integer value) {
        Intent intent = new Intent();
        intent.setType("image/png");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        intent.putExtra(name, "true");
        startActivityForResult(intent, value);
    }

    public void image_1(View v) {
        if (Build.VERSION.SDK_INT >= 23) {
            if (checkPermission()) {
                pick_image_path("image1", 2);
            } else {
                requestPermission();
            }
        } else {
            pick_image_path("image1", 2);
        }
    }

    public void image_2(View v) {
        if (Build.VERSION.SDK_INT >= 23) {
            if (checkPermission()) {
                pick_image_path("image2", 4);
            } else {
                requestPermission();
            }
        } else {
            pick_image_path("image2", 4);

        }
    }


}