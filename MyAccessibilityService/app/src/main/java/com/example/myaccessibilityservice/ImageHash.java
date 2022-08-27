package com.example.myaccessibilityservice;

import android.graphics.Bitmap;

import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;

import android.graphics.Paint;

public class ImageHash {

    public String imgDHash(Bitmap img) {
        Bitmap bitOut = resize(img, 9, 8);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        return dHash(greyBitOut);
    }

    public String imgAHash(Bitmap img) {
        Bitmap bitOut = resize(img, 8, 8);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        Integer avgBit = calculateAverageColor(greyBitOut);
        return aHash(bitOut, avgBit);
    }

    public String imgPHash(Bitmap img) {
        Bitmap bitOut = resize(img, 32, 32);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        Bitmap dctVals = applyDCT(greyBitOut);
        Double avgDct = avgDCT(dctVals);
        return pHash(dctVals, avgDct);
    }

    private Double avgDCT(Bitmap bit){
        double total = 0;

        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                total += bit.getPixel(x,y);
            }
        }
        total -= bit.getPixel(0, 0);

        double avg = total / (double) ((8 * 8) - 1);

        return avg;
    }

    private double[] c;

    private void initCoefficients() {
        c = new double[32];

        for (int i = 1; i < 32; i++) {
            c[i] = 1;
        }
        c[0] = 1 / Math.sqrt(2.0);
    }

    private Bitmap applyDCT(Bitmap bitmap) {
        initCoefficients();
        int N = 32;

        Bitmap bit = Bitmap.createBitmap(N, N, Bitmap.Config.ARGB_8888);
        for (int u = 0; u < N; u++) {
            for (int v = 0; v < N; v++) {
                double sum = 0.0;
                for (int i = 0; i < N; i++) {
                    for (int j = 0; j < N; j++) {
                        sum += Math.cos(((2 * i + 1) / (2.0 * N)) * u * Math.PI) * Math.cos(((2 * j + 1) / (2.0 * N)) * v * Math.PI) * (bitmap.getPixel(u,v));
                    }
                }
                sum *= ((c[u] * c[v]) / 4.0);
                bit.setPixel(u, v, (int) sum);
            }
        }
        return bit;
    }

    private int calculateAverageColor(Bitmap bitmap) {
        int val = 0;
        for (int i=0;i<bitmap.getHeight();i++){
            for (int j=0;j<bitmap.getWidth();j++){
                val += bitmap.getPixel(i, j);
            }
        }
        return val / 64;
    }


    private Bitmap convertGreyscale(Bitmap bitImg){
        Bitmap bmp = bitImg.copy(Bitmap.Config.ARGB_8888, true);
        Bitmap bmpGrayscale = Bitmap.createBitmap(bmp.getWidth(), bmp.getHeight(), Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bmpGrayscale);
        Paint paint = new Paint();
        ColorMatrix colorMatrix = new ColorMatrix();
        colorMatrix.setSaturation(0f);
        ColorMatrixColorFilter colorMatrixFilter = new ColorMatrixColorFilter(colorMatrix);
        paint.setColorFilter(colorMatrixFilter);
        canvas.drawBitmap(bmp, 0F, 0F, paint);

        return bmpGrayscale;
    }

    private Bitmap resize(Bitmap greyBit, Integer width, Integer height){
        Bitmap resizeBit = greyBit.createScaledBitmap(greyBit, width, height, false);

        return resizeBit;
    }

    private String dHash(Bitmap bit){
        String out ="";
        int width = bit.getWidth();
        int height = bit.getHeight();

        for (int y=0;y<height;y++){
            for (int x=0; x<width-1;x++){
                if (bit.getPixel(x, y) > bit.getPixel(x +1, y)){
                    out += "1";
                }
                else{
                    out += "0";
                }
            }
        }
        return out;
    }

    private String aHash(Bitmap bit, Integer avgColour){
        String out = "";
        int width = bit.getWidth();
        int height = bit.getHeight();

        for (int y=0;y<height;y++){
            for (int x=0; x<width;x++){
                if (bit.getPixel(x, y) > avgColour){
                    out += "1";
                }
                else{
                    out += "0";
                }
            }
        }
        return out;
    }

    private String pHash(Bitmap bit, Double avgDCT){
        String out = "";
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                if (x != 0 && y != 0) {
                    if (bit.getPixel(x, y) > avgDCT) {
                        out += "1";
                    }
                    else{
                        out += "0";
                        }
                }
            }
        }
        return out;
    }
}
