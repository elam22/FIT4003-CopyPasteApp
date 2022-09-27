package com.example.myaccessibilityservice;

import android.app.Application;
import android.graphics.Bitmap;


public class HashSimilarity extends Application {

    protected double computeDifference(String img1, Bitmap img2, String hash){
        System.out.println(img2.toString());
        if (hash.equals("A")){
            return computeDifferenceAHash(img1, img2);
        }
        else if (hash.equals("D")){
            return computeDifferenceDHash(img1, img2);
        }
        else if (hash.equals("P")){
            return computeDifferencePHash(img1, img2);
        }
        return 0.0;

    }

    private double computeDifferenceDHash(String img1, Bitmap img2){

        String bitHash2 = new ImageHash().imgDHash(img2);

        int dist = hammingDistance(img1, bitHash2);
        return similarity(dist, img1.length());

    }

    private double computeDifferenceAHash(String img1, Bitmap img2){

        String bitHash2 = new ImageHash().imgAHash(img2);

        System.out.println(bitHash2);
        System.out.println(img1);

        int dist = hammingDistance(img1, bitHash2);
        return similarity(dist, img1.length());
    }

    private double computeDifferencePHash(String img1, Bitmap img2){

        String hash2 = new ImageHash().imgPHash(img2);
        int dist = hammingDistance(img1, hash2);
        return similarity(dist, img1.length());
    }


    private double similarity(int dist, int length){
        double similarity = (length - dist) / (double) length;
        similarity = similarity *100;
        return similarity;
    }


    private int hammingDistance(String imgHash1, String imgHash2){
        int sum = 0;
        for (int i = 0; i < imgHash1.length(); i++) {
            if (imgHash1.charAt(i) != imgHash2.charAt(i)){
                sum += 1;
            }
        }
        return sum;
    }
}
