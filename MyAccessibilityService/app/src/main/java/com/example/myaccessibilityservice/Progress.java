package com.example.myaccessibilityservice;

import static java.lang.Thread.sleep;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;


import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;
import okio.Buffer;
import okio.BufferedSource;
import okio.ForwardingSource;
import okio.Okio;
import okio.Source;

public class Progress extends AppCompatActivity {

    TextView progressFeedBack;
    String getUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_progress);
        progressFeedBack = findViewById(R.id.progress_feedback);


        new java.util.Timer().schedule(
                new java.util.TimerTask() {
                    @Override
                    public void run() {

                        Intent intent = getIntent();
                        getUrl = intent.getExtras().getString("getUrl");




                        // your code here
                        getProgress();
                    }
                },
                40000
        );

        progressFeedBack.setText(getUrl);


    }

        public void getProgress(){

            Thread thread = new Thread(new Runnable() {

                @SuppressLint("SetTextI18n")
                @Override
                public void run() {
                    try {
                        while (true) {
                            String result = getRequest(getUrl);
                            Log.i("Json", getUrl);
                            JSONObject object = new JSONObject(result);
                            String state = object.getString("state");
                            Log.i("Json", object.getString("state"));

                            //Your code goes here
                            Progress.this.runOnUiThread(new Runnable() {
                                public void run() {
                                    if (state.equals("PROCESSING")){
                                        progressFeedBack.setText("Video is being processed" );
                                    } else if (state.equals("SUCCESS")){
                                        progressFeedBack.setText("SUCCESS" );
                                    } else if(state.equals("FAILED")){
                                        progressFeedBack.setText("failed" );
                                    }

//                                  Toast.makeText(getApplicationContext(), "Result is " + state, Toast.LENGTH_LONG).show();
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



                            sleep(60000);


                        }

                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
            thread.start();
    }

    public String getRequest(String url) throws IOException {
        OkHttpClient client = new OkHttpClient.Builder()
                .retryOnConnectionFailure(true)
                .build();

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
                    getResponse.close();
                    response.close();
                    // do something wih the result
                }
            }
        });

        return getResponse.body().string();

    }
}


