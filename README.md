# 🎾 Tennis Video Analysis

This app analyzes tennis videos to track **players**, **balls**, and **court lines** while providing **real-time statistics** and **visualizations**.

Built using modern computer vision techniques, it empowers **coaches**, **analysts**, and **players** to gain insights from match footage with minimal setup.

---

## 📁 Datasets Used

- **Tennis Court Detection Dataset**  
  `tennis_court_det_dataset.zip` (local)

- **Tennis Ball Detection Dataset (Roboflow)**  
  🔗 [https://universe.roboflow.com/viren-dhanwani/tennis-ball-detection](https://universe.roboflow.com/viren-dhanwani/tennis-ball-detection)

---

## 🧠 Training Notebooks

You can retrain or fine-tune the models using these Colab notebooks:

- 📝 `tennis_ball_detector_training.ipynb`  
  → Train the YOLOv8-based tennis ball detector

- 📝 `TennisCourtKeyPoint.ipynb`  
  → Run this to generate the keypoint-based court detection model

---

## 🚀 Features

✅ Player tracking and identification  
✅ Ball trajectory analysis  
✅ Court line detection  
✅ Speed calculations  
✅ Mini court visualization  
✅ Player performance statistics

---

## 🖥️ Usage Instructions

1. **Upload** an `.mp4` tennis video through the app interface  
2. **Wait** for processing (may take several minutes depending on video length and hardware)  
3. **View** the analyzed video with overlays (ball paths, player movement, court lines)  
4. **Download** the processed video with annotations for review or sharing  

---

## 🛠 Technologies Used

- **Python**
- **OpenCV**
- **YOLOv8 (Ultralytics)**
- **PyTorch**
- **Streamlit** (for the web frontend)
- **Roboflow** (for dataset hosting & model training)

---

## 📚 Citation

**Project:**

```bibtex
@misc{TennisAnalysis_project,
  title       = {Tennis Video Analysis Project},
  author      = {Anonymous Developer},
  howpublished= {\url{https://github.com/yourusername/tennis-video-analysis}},
  url         = {https://github.com/yourusername/tennis-video-analysis},
  year        = {2025},
  month       = {June},
  note        = {Accessed: 2025-06-22}
}
