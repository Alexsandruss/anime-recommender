package com.example.animerecommendationapp;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.StrictMode;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.CompoundButton;
import android.widget.Switch;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import javax.net.ssl.HttpsURLConnection;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        useALS = false;
        Switch algSwitch = (Switch) findViewById(R.id.algorithmSwitch);
        algSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                useALS = isChecked;
            }
        });

        userTitles = new ArrayList<>();
        List<String> allTitles = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(getResources().openRawResource(R.raw.anime_titles)))) {
            String line;
            while ((line = br.readLine()) != null) {
                allTitles.add(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_dropdown_item_1line, allTitles);
        final AutoCompleteTextView inputView = (AutoCompleteTextView) findViewById(R.id.insertTitleField);
        inputView.setAdapter(adapter);
    }

    public String performPostCall(String requestURL, String requestData) {
        URL url;
        String response = "";
        try {
            url = new URL(requestURL);

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setReadTimeout(60000);
            conn.setConnectTimeout(60000);
            conn.setRequestMethod("POST");
            conn.setDoInput(true);
            conn.setDoOutput(true);

            OutputStream os = conn.getOutputStream();
            BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(os, StandardCharsets.UTF_8));
            writer.write(requestData);

            writer.flush();
            writer.close();
            os.close();
            int responseCode = conn.getResponseCode();

            if (responseCode == HttpsURLConnection.HTTP_OK) {
                String line;
                BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                while ((line = br.readLine()) != null) {
                    response += line + "\n";
                }
            }
            else {
                response = "HTTP Error Code: " + responseCode;

            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return response;
    }

    private boolean useALS;
    private List<String> userTitles;

    private void updateTitles()
    {
        String newText = "";
        for (int i = 0; i < userTitles.size(); ++i)
        {
            newText += userTitles.get(i);
            if (i != userTitles.size() - 1)
                newText += "\n";
        }
        if (newText.equals(""))
        {
            newText = "None";
        }
        final TextView userTitlesView = (TextView) findViewById(R.id.userTitlesText);
        userTitlesView.setText(newText);
    }

    public void addTitle(View view) {
        final AutoCompleteTextView inputView = (AutoCompleteTextView) findViewById(R.id.insertTitleField);
        String title = inputView.getText().toString();
        userTitles.add(title);
        updateTitles();
        inputView.setText("");
    }

    public void clearTitles(View view) {
        userTitles.clear();
        updateTitles();
        final TextView recView = (TextView) findViewById(R.id.recTitlesText);
        recView.setText("None");
    }

    public void sendTitles(View view) {
        String titlesText = "";
        if (useALS)
            titlesText += "als;";
        else
            titlesText += "cosine similarity;";
        for (int i = 0; i < userTitles.size(); ++i)
        {
            titlesText += userTitles.get(i);
            if (i != userTitles.size() - 1)
                titlesText += ";";
        }
        String requestResult = performPostCall("http://10.0.2.2:8080", titlesText);

        final TextView recView = (TextView) findViewById(R.id.recTitlesText);
        recView.setText(requestResult);
    }
}
