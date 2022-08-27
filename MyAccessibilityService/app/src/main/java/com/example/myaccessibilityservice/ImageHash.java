package com.example.myaccessibilityservice;

import android.graphics.Bitmap;

import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;

import android.graphics.Paint;

public class ImageHash {

    public static double pi = 3.142857;

    public String imgDHash(Bitmap img) {
        Bitmap bitOut = resize(img, 9, 8);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        return dHash(greyBitOut);
    }

    public String imgAHash(Bitmap img) {
        Bitmap bitOut = resize(img, 8, 8);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        Integer avgBit = calculateAvgColour(greyBitOut);
        return aHash(bitOut, avgBit);
    }

    public String imgPHash(Bitmap img) {
        Bitmap bitOut = resize(img, 32, 32);
        Bitmap greyBitOut = convertGreyscale(bitOut);
        Bitmap dctVals = applyDCT(greyBitOut);
        Integer avgDct = avgDCT(dctVals);
        return pHash(dctVals, avgDct);
    }

    private Integer avgDCT(Bitmap bit){
        double total = 0;

        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                total += bit.getPixel(x,y);
            }
        }
        total -= bit.getPixel(0, 0);

        double avg = total / (double) ((8 * 8) - 1);

        return (int) avg;
    }

    private Bitmap applyDCT(Bitmap bitmap) {
        int i, j, k, l;
        int width = bitmap.getWidth();
        int height = bitmap.getHeight();

        Bitmap bitOut = Bitmap.createBitmap(32, 32, Bitmap.Config.ARGB_8888);

        double ci, cj, dct1, sum;

        for (i = 0; i < width; i++)
        {
            for (j = 0; j < height; j++)
            {

                if (i == 0)
                    ci = 1 / Math.sqrt(width);
                else
                    ci = Math.sqrt(2) / Math.sqrt(width);

                if (j == 0)
                    cj = 1 / Math.sqrt(height);
                else
                    cj = Math.sqrt(2) / Math.sqrt(height);

                sum = 0;
                for (k = 0; k < width; k++)
                {
                    for (l = 0; l < height; l++)
                    {
                        dct1 = bitmap.getPixel(k, l) *
                                Math.cos((2 * k + 1) * i * pi / (2 * width)) *
                                Math.cos((2 * l + 1) * j * pi / (2 * height));
                        sum = sum + dct1;
                    }
                }
                bitOut.setPixel(i, j, (int) (ci*cj*sum));
            }
        }
        return bitOut;
    }


    private int calculateAvgColour(Bitmap bitmap){
        int redBucket = 0;
        int greenBucket = 0;
        int blueBucket = 0;

        int width = bitmap.getWidth();
        int height = bitmap.getHeight();
        int pixelCount = 0;
        int c = 0;

        for (int y = 0; y < height; y += 1) {
            for (int x = 0; x < width; x += 1) {
                c = bitmap.getPixel(x, y);

                redBucket += Color.red(c);
                greenBucket += Color.green(c);
                blueBucket += Color.blue(c);
                pixelCount++;
            }
        }

        return Color.rgb(redBucket / pixelCount, greenBucket / pixelCount,
                blueBucket / pixelCount);
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

    private String pHash(Bitmap bit, Integer avgDCT){
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
