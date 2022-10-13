package com.example.myaccessibilityservice.ui.explore;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.myaccessibilityservice.R;

public class VideoListAdapter extends ArrayAdapter<String> {

    String [] video_name;
    int [] video_thumbnails;
    Context mContext;

    public VideoListAdapter(@NonNull Context context, String [] videoNames, int[] videoThumbnails) {
        super(context, R.layout.video_list_view);
        this.video_name = videoNames;
        this.video_thumbnails = videoThumbnails;
        this.mContext = context;
    }

    @Override
    public int getCount() {
        return video_name.length;
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        ViewHolder mViewHolder = new ViewHolder();
        if (convertView == null) {
            LayoutInflater mInflater = (LayoutInflater) mContext.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            convertView = mInflater.inflate(R.layout.video_list_view, parent, false);
            mViewHolder.mThumbnail = (ImageView) convertView.findViewById(R.id.video_thumbnail);
            mViewHolder.mName = (TextView) convertView.findViewById(R.id.video_name);

            convertView.setTag(mViewHolder);
        } else {
            mViewHolder = (ViewHolder) convertView.getTag();
        }
        mViewHolder.mThumbnail.setImageResource(video_thumbnails[position]);
        mViewHolder.mName.setText(video_name[position]);

        return convertView;
    }

    static class ViewHolder{
        ImageView mThumbnail;
        TextView mName;
    }
}