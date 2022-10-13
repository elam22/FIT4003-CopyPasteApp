package com.example.myaccessibilityservice.ui.explore;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ListView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;

import com.example.myaccessibilityservice.R;
import com.example.myaccessibilityservice.databinding.FragmentExploreBinding;

public class ExploreFragment extends Fragment {

    private FragmentExploreBinding binding;

    //list of videos
    ListView videosListView;
    VideoListAdapter adapter;

    String[] videoNames = {"video #1", "video #2", "video #3", "video #4"};
    int[] videoThumbnail = {R.drawable.yt_placeholder, R.drawable.yt_placeholder, R.drawable.yt_placeholder, R.drawable.yt_placeholder};

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        ExploreViewModel exploreViewModel =
                new ViewModelProvider(this).get(ExploreViewModel.class);

        binding = FragmentExploreBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        videosListView = (ListView) root.findViewById(R.id.list_tutorial);
        adapter = new VideoListAdapter(getActivity().getApplicationContext(), videoNames, videoThumbnail);

        videosListView.setAdapter(adapter);

        return root;
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}