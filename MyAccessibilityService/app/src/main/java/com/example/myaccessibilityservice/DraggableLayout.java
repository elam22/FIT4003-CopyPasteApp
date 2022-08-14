package com.example.myaccessibilityservice;

import android.content.Context;
import android.graphics.Point;
import android.util.AttributeSet;
import android.util.Log;
import android.view.DragEvent;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import androidx.annotation.Nullable;

public class DraggableLayout extends LinearLayout implements View.OnDragListener {

    GestureDetector mLongClickDetector;
    Point mPickPoint;

    public DraggableLayout(Context context) {
        this(context, null, 0);
    }

    public DraggableLayout(Context context, @Nullable AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public DraggableLayout(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        // When user performs a long press, we begin dragging
        mLongClickDetector = new GestureDetector(context, new GestureDetector.SimpleOnGestureListener() {
            public void onLongPress(MotionEvent e) {
                mPickPoint = new Point((int) e.getX(), (int) e.getY());
                View.DragShadowBuilder shadowBuilder = new View.DragShadowBuilder(DraggableLayout.this) {
                    @Override
                    public void onProvideShadowMetrics(Point outShadowSize, Point outShadowTouchPoint) {
                        outShadowSize.set(getWidth(), getHeight());
                        outShadowTouchPoint.set(mPickPoint.x, mPickPoint.y);
                    }
                };
                startDrag(null, shadowBuilder, null, 0);
            }
        });
    }

    @Override
    protected void onAttachedToWindow() {
        // We should register this class as OnDragListener to parent view to catch DROP events from it
        ((ViewGroup) getParent()).setOnDragListener(this);
        super.onAttachedToWindow();
    }

    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        //This is also an important point: we must intercept touch events before the child elements (Buttons and so on)
        return mLongClickDetector.onTouchEvent(ev);
    }

    @Override
    public boolean onDragEvent(DragEvent event) {
        Log.i("onDragEvent", String.valueOf(event.getAction()));

        if (event.getAction() == DragEvent.ACTION_DRAG_STARTED) {
            // And when user performs drop we change position of view
            setX(event.getX() - mPickPoint.x);
            setY(event.getY() - mPickPoint.y);
            return true;
        } else if (event.getAction() == DragEvent.ACTION_DROP) {
            setX(event.getX() - mPickPoint.x);
            setY(event.getY() - mPickPoint.y);
            return true;
        }
        return false;
    }

    @Override
    public boolean onDrag(View v, DragEvent event) {
        Log.i("onDrag", String.valueOf(event.getAction()));

        return onDragEvent(event);
    }
}
