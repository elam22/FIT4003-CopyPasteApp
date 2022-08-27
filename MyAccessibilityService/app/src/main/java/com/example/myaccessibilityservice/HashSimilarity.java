package com.example.myaccessibilityservice;

import android.app.Application;
import android.graphics.Bitmap;


public class HashSimilarity extends Application {

    protected double computeDifference(Bitmap img1, Bitmap img2, String hash){
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

    private double computeDifferenceDHash(Bitmap img1, Bitmap img2){

        String bitHash1 = new ImageHash().imgDHash(img1);
        String bitHash2 = new ImageHash().imgDHash(img2);

        int dist = hammingDistance(bitHash1, bitHash2);
        return similarity(dist, bitHash1.length());

    }

    private double computeDifferenceAHash(Bitmap img1, Bitmap img2){

        String bitHash1 = new ImageHash().imgAHash(img1);
        String bitHash2 = new ImageHash().imgAHash(img2);

        int dist = hammingDistance(bitHash1, bitHash2);
        return similarity(dist, bitHash1.length());
    }

    private double computeDifferencePHash(Bitmap img1, Bitmap img2){

        String bitHash1 = new ImageHash().imgPHash(img1);
        String bitHash2 = new ImageHash().imgPHash(img2);

        int dist = hammingDistance(bitHash1, bitHash2);
        return similarity(dist, bitHash1.length());
    }


    private double similarity(int dist, int length){
        double similarity = (length - dist) / (double) length;
        similarity = java.lang.Math.pow(similarity, 2);
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
