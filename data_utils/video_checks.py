import logging
import subprocess
import re

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_duration(duration_str):
    """
    Parse a duration string from ffmpeg (e.g., '00:04:00.00') into seconds.
    """
    h, m, s = map(float, duration_str.split(':'))
    return h * 3600 + m * 60 + s


def ensure_fps_resolution_duration(path, target_fps=25, target_resolution=(512, 512), min_duration=240, max_duration=300):
    """
    Ensure the video is 25 FPS, 512x512 resolution, and has a duration of 4-5 minutes.
    """
    logging.info(f'Checking and adjusting FPS, resolution, and duration for {path}')
    
    try:
        # Use ffprobe to get video properties in JSON format
        logging.info(f'Probing video file: {path}')
        probe_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=width,height,r_frame_rate,duration', '-of', 'default=noprint_wrappers=1', path
        ]
        result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f'ffprobe failed with error: {result.stderr}')
        
        output = result.stdout
        logging.debug(f'ffprobe output:\n{output}')

        # Extract resolution
        width = int(re.search(r'width=(\d+)', output).group(1))
        height = int(re.search(r'height=(\d+)', output).group(1))
        logging.debug(f'Original Resolution: {width}x{height}')
        
        # Extract FPS (r_frame_rate)
        fps_str = re.search(r'r_frame_rate=(\d+)/(\d+)', output).groups()
        fps = int(fps_str[0]) / int(fps_str[1])
        logging.debug(f'Original FPS: {fps}')
        
        # Extract duration
        duration = float(re.search(r'duration=([\d\.]+)', output).group(1))
        logging.debug(f'Original Duration: {duration} seconds')

        # Adjust FPS if necessary
        if fps != target_fps:
            logging.info(f'Adjusting FPS to {target_fps}')
            adjust_fps_cmd = ['ffmpeg', '-i', path, '-filter:v', f'fps=fps={target_fps}', f'{path}_adjusted_fps.mp4']
            subprocess.run(adjust_fps_cmd)
            path = f'{path}_adjusted_fps.mp4'

        # Adjust resolution if necessary
        if (width, height) != target_resolution:
            logging.info(f'Adjusting resolution to {target_resolution[0]}x{target_resolution[1]}')
            adjust_resolution_cmd = ['ffmpeg', '-i', path, '-vf', f'scale={target_resolution[0]}:{target_resolution[1]}', f'{path}_adjusted_resolution.mp4']
            subprocess.run(adjust_resolution_cmd)
            path = f'{path}_adjusted_resolution.mp4'

        # Check duration
        if not (min_duration <= duration <= max_duration):
            logging.warning(f'Video duration {duration} seconds is not within the target range of {min_duration}-{max_duration} seconds')

    except Exception as e:
        logging.error(f'Error processing video: {e}', exc_info=True)



# Example usage
if __name__ == '__main__':
    ensure_fps_resolution_duration('data/Asad/asad_2.mp4')