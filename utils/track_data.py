import os
import json

def get_all_track_infos(track_dir="data/Tracks"):
    """
    Returns a list of dicts for each track JSON in the directory,
    with keys: filename, display_name, preview_image
    """
    tracks = []
    for fname in os.listdir(track_dir):
        if fname.lower().endswith(".json"):
            path = os.path.join(track_dir, fname)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                if data.get("complete"):
                    display_name = data.get("display_name", fname.rsplit('.',1)[0])
                    preview_img = data.get("preview_image", "assets/images/placeholder.png")
                    tracks.append({
                        "filename": fname,
                        "display_name": display_name,
                        "preview_image": preview_img,
                    })
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return tracks
