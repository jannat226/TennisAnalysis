# import streamlit as st
# from main import run_analysis
# import os
# import time  # for unique timestamp

# st.title("🎾 Tennis Video Analysis")

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# temp_dir = os.path.join(BASE_DIR, "temp")
# output_dir = os.path.join(BASE_DIR, "output_videos")
# os.makedirs(temp_dir, exist_ok=True)
# os.makedirs(output_dir, exist_ok=True)

# uploaded_file = st.file_uploader("Upload your tennis video (mp4)", type=["mp4"])

# if uploaded_file:
#     input_path = os.path.join(temp_dir, uploaded_file.name)
    
#     # Use timestamp to make output file unique
#     output_path = os.path.join(output_dir, f"streamlit_output_{int(time.time())}.mp4")

#     # Save uploaded file
#     with open(input_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     st.info("Running analysis... This might take a while depending on your video length.")
#     try:
#         with st.spinner("Processing video..."):
#             output_video_path = run_analysis(input_path, output_path)

#         if os.path.exists(output_video_path):
#             size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
#             st.success(f"Analysis complete! Output video size: {size_mb:.2f} MB")
#             st.video(output_video_path)  # Streamlit will serve fresh video
#         else:
#             st.error("Output video file not found after analysis.")
#     except Exception as e:
#         st.error(f"Error during analysis: {e}")
# else:
#     st.info("Please upload a tennis video file to get started.")
import streamlit as st
from main import run_analysis
import os
import time
import cv2

st.title("🎾 Tennis Video Analysis")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.join(BASE_DIR, "temp")
output_dir = os.path.join(BASE_DIR, "output_videos")
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)


def verify_video_file(video_path):
    """Verify that the video file is valid and playable"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, "Cannot open video file"
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        if frame_count == 0:
            return False, "Video has no frames"
        
        if duration == 0:
            return False, "Video has zero duration"
        
        return True, f"Video OK: {frame_count} frames, {fps:.2f} fps, {duration:.2f}s"
    
    except Exception as e:
        return False, f"Error reading video: {str(e)}"


uploaded_file = st.file_uploader("Upload your tennis video (mp4)", type=["mp4"])

if uploaded_file:
    input_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Use timestamp to make output file unique
    timestamp = int(time.time())
    output_path = os.path.join(output_dir, f"streamlit_output_{timestamp}.mp4")

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Verify input video
    st.info("🔍 Verifying uploaded video...")
    is_valid, message = verify_video_file(input_path)
    
    if not is_valid:
        st.error(f"❌ Video validation failed: {message}")
        st.stop()
    else:
        st.success(f"✅ {message}")

    st.info("🚀 Running analysis... This might take a while depending on your video length.")
    
    try:
        with st.spinner("Processing video..."):
            output_video_path = run_analysis(input_path, output_path)

        if output_video_path and os.path.exists(output_video_path):
            # Verify output video
            is_valid_output, output_message = verify_video_file(output_video_path)
            
            if is_valid_output:
                size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
                st.success(f"🎉 Analysis complete! Output video size: {size_mb:.2f} MB")
                st.info(f"📊 {output_message}")
                
                # Display video
                st.video(output_video_path)
                
                # Provide download option
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Processed Video",
                        data=file.read(),
                        file_name=f"tennis_analysis_{timestamp}.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error(f"❌ Output video validation failed: {output_message}")
                
                # Show file info for debugging
                if os.path.exists(output_video_path):
                    size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
                    st.error(f"Output file exists but is invalid. Size: {size_mb:.2f} MB")
                else:
                    st.error("Output video file was not created.")
        else:
            st.error("❌ Analysis failed - no output video was generated.")
            
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        
        # Show debugging info
        st.error("🔧 Debug Information:")
        st.code(str(e))
        
        # Check if partial output exists
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            st.info(f"Partial output file exists: {size_mb:.2f} MB")
else:
    st.info("📤 Please upload a tennis video file to get started.")
    
    # Add some usage instructions
    with st.expander("ℹ️ How to use this app"):
        st.markdown("""
        1. **Upload Video**: Choose an MP4 tennis video file
        2. **Wait for Processing**: The analysis can take several minutes
        3. **View Results**: Watch the processed video with:
           - Player tracking boxes
           - Ball tracking
           - Court line detection
           - Mini court visualization
           - Player statistics
        4. **Download**: Save the processed video to your device
        
        **Tips for best results:**
        - Use clear, well-lit tennis videos
        - Ensure players and ball are visible
        - MP4 format works best
        """)