#!/usr/bin/env python3
"""
Video rendering service for MathVerse animations.
Handles rendering Manim scenes to MP4 videos.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class MathVerseRenderer:
    def __init__(self, scenes_dir: str = "manim_scenes", output_dir: str = "output"):
        self.scenes_dir = Path(scenes_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def list_available_scenes(self) -> List[Dict]:
        """List all available scenes organized by educational level"""
        scenes = []
        
        for level_dir in self.scenes_dir.iterdir():
            if level_dir.is_dir():
                for py_file in level_dir.glob("*.py"):
                    try:
                        # Extract scene classes from file
                        scene_classes = self._extract_scene_classes(py_file)
                        for scene_class in scene_classes:
                            scenes.append({
                                "level": level_dir.name,
                                "file": py_file.name,
                                "scene": scene_class,
                                "path": str(py_file.relative_to(self.scenes_dir))
                            })
                    except Exception as e:
                        print(f"Error processing {py_file}: {e}")
        
        return scenes
    
    def _extract_scene_classes(self, file_path: Path) -> List[str]:
        """Extract scene class names from Python file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple regex to find class definitions inheriting from Scene
        import re
        pattern = r'class\s+(\w+)\s*\(\s*[^)]*Scene[^)]*\)'
        matches = re.findall(pattern, content)
        return matches
    
    def render_scene(self, scene_path: str, scene_class: str, 
                   quality: str = "m", preview: bool = False) -> Dict:
        """Render a specific scene to MP4"""
        
        full_path = self.scenes_dir / scene_path
        if not full_path.exists():
            raise FileNotFoundError(f"Scene file not found: {scene_path}")
        
        # Build manim command
        cmd = [
            "python", "-m", "manim",
            str(full_path),
            scene_class,
            f"-{quality}",  # Quality flag
            "--output_file", str(self.output_dir)
        ]
        
        if preview:
            cmd.append("-p")
        
        try:
            # Run manim command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.scenes_dir.parent)
            )
            
            if result.returncode == 0:
                # Find the output file
                output_file = self._find_output_file(scene_class)
                return {
                    "success": True,
                    "output_file": output_file,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_output_file(self, scene_class: str) -> Optional[str]:
        """Find the output video file for a scene"""
        for pattern in ["*.mp4", "*.mov"]:
            for file_path in self.output_dir.glob(pattern):
                if scene_class in file_path.name:
                    return str(file_path)
        return None
    
    def batch_render(self, scenes: List[Dict], quality: str = "m") -> List[Dict]:
        """Render multiple scenes in batch"""
        results = []
        for scene in scenes:
            result = self.render_scene(
                scene["path"], 
                scene["scene"], 
                quality
            )
            result["scene_info"] = scene
            results.append(result)
        return results
    
    def generate_thumbnail(self, video_path: str, time_offset: str = "00:00:05") -> str:
        """Generate thumbnail from video using ffmpeg"""
        import subprocess
        
        thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", time_offset,
            "-vframes", "1",
            "-q:v", "2",
            thumbnail_path,
            "-y"
        ]
        
        subprocess.run(cmd, capture_output=True)
        return thumbnail_path

def main():
    """CLI interface for the renderer"""
    renderer = MathVerseRenderer()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python render_video.py list                    # List available scenes")
        print("  python render_video.py render <scene> <class>  # Render specific scene")
        print("  python render_video.py batch                    # Batch render all scenes")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        scenes = renderer.list_available_scenes()
        print(json.dumps(scenes, indent=2))
    
    elif command == "render" and len(sys.argv) >= 4:
        scene_path = sys.argv[2]
        scene_class = sys.argv[3]
        result = renderer.render_scene(scene_path, scene_class)
        print(json.dumps(result, indent=2))
    
    elif command == "batch":
        scenes = renderer.list_available_scenes()
        results = renderer.batch_render(scenes)
        print(json.dumps(results, indent=2))
    
    else:
        print("Invalid command or missing arguments")

if __name__ == "__main__":
    main()