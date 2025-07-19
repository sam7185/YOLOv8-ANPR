def run_pipeline(video_path, entry_y, exit_y):
    import subprocess
    subprocess.run([
        'python3', 'main.py',
        '--video', video_path,
        '--entry_y', str(entry_y),
        '--exit_y', str(exit_y)
    ])
