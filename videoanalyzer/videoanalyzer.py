"""This scrip will analyze the video file and plot the frame size with avrage
bitrate, and also will show the frames interval which can help to check if
there is frame dropped.
We have two backend to do the anlayze: pyav and ffmpeg. PyAV is quick but may
have problem with some video files. ffmpeg(ffprobe) has a good compatibility
but take a longer time.
"""

import sys
import av
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
import ffmpeg

frame_type_color = {
    # audio
    'A': 'red',
    # video
    'I': 'red',
    'P': 'green',
    'B': 'blue'
}

class PYAV:
    def __init__(self, file):
        with av.open(file) as container:
            container.streams.video[0].thread_type = 'AUTO'

            video = container.streams.video[0]
            print(f'fps: {video.framerate} = {float(video.framerate)}')
            print(f'bit: {container.bit_rate}')

            self.fps = float(video.framerate)
            self.bps = container.bit_rate / 1000 # in kbits

            rows = []
            pkt_size = []
            for packet in container.demux(video=0):
                if packet.size != 0.0:
                    pkt_size.append(packet.size)
                for frame in packet.decode():
                    rows.append([frame.time, frame.pict_type])

            self.df = pd.DataFrame(rows, columns=["pkt_pts_time", "pict_type"])
            self.df["pkt_size"] = pkt_size


class FFMPEG:
    def __init__(self, file):
        probe = ffmpeg.probe(file,
                             show_entries="frame=pkt_pts_time,pict_type,pkt_size",
                             select_streams="v:0")
        print(probe["streams"][0]["r_frame_rate"])
        print(probe["format"]["bit_rate"])

        fps = probe["streams"][0]["r_frame_rate"].split("/")
        self.fps = float(fps[0]) / float(fps[1])
        self.bps = float(probe["format"]["bit_rate"]) / 1000

        self.df = pd.DataFrame.from_records(probe["frames"])
        self.df["pkt_size"] = pd.to_numeric(self.df["pkt_size"])
        self.df["pkt_pts_time"] = pd.to_numeric(self.df["pkt_pts_time"])


def plot_bitrate(df):
    pts_I = np.array(df[df['pict_type'] == 'I']["pkt_pts_time"])
    pts_P = np.array(df[df['pict_type'] == 'P']["pkt_pts_time"])
    pts_B = np.array(df[df['pict_type'] == 'B']["pkt_pts_time"])

    pkt_I = np.array(df[df['pict_type'] == 'I']["pkt_size"])
    pkt_P = np.array(df[df['pict_type'] == 'P']["pkt_size"])
    pkt_B = np.array(df[df['pict_type'] == 'B']["pkt_size"])

    # Setting up the plot surface
    plt.vlines(pts_I, 0, pkt_I, color=frame_type_color['I'])
    plt.vlines(pts_P, 0, pkt_P, color=frame_type_color['P'])
    plt.vlines(pts_B, 0, pkt_B, color=frame_type_color['B'])

    plt.show()


def plot_bitrate_and_frame(df, fps, bps):
    pts_I = np.array(df[df['pict_type'] == 'I']["pkt_pts_time"])
    pts_P = np.array(df[df['pict_type'] == 'P']["pkt_pts_time"])
    pts_B = np.array(df[df['pict_type'] == 'B']["pkt_pts_time"])
    pts_all = np.array(df["pkt_pts_time"])

    # Convert the frame size (in Byte) to bitrate (in kbits)
    pkt_I = np.array(df[df['pict_type'] == 'I']["pkt_size"]) * 8 / 1000 * fps
    pkt_P = np.array(df[df['pict_type'] == 'P']["pkt_size"]) * 8 / 1000 * fps
    pkt_B = np.array(df[df['pict_type'] == 'B']["pkt_size"]) * 8 / 1000 * fps

    # Setting up the plot surface
    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(nrows=2, ncols=1, height_ratios=[5, 1])  # First axes

    # Bitrate plot
    ax0 = fig.add_subplot(gs[0, 0])

    ax0.title.set_text('Bitrate')
    ax0.set_xlabel('Time (sec)')
    ax0.set_ylabel('Frame Bitrate (kbit/s)')

    plt.vlines(pts_I, 0, pkt_I, color=frame_type_color['I'])
    plt.vlines(pts_P, 0, pkt_P, color=frame_type_color['P'])
    plt.vlines(pts_B, 0, pkt_B, color=frame_type_color['B'])

    # calculate mean line position (right 85%, above line)
    mean_text_x = 0.85
    mean_text_y = bps / np.max(pkt_I) + 0.03
    mean_text = "mean ({:.0f})".format(bps)

    # draw mean as think black line w/ text
    plt.hlines(bps, 0, np.max(pts_all), linewidth=2, color='black', label='mean')
    ax0.text(mean_text_x, mean_text_y, mean_text, size=12, ha="center", fontweight='bold', color='black', transform=ax0.transAxes)

    # Frame  interval plot
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.title.set_text('Frame interval')
    ax1.set_xlabel('Frames')
    ax1.set_ylabel('Time (sec)')
    ax1.plot(np.diff(pts_all))

    plt.show()


def main():
    obj = PYAV(sys.argv[1])
    # obj = FFMPEG(sys.argv[1])
    plot_bitrate_and_frame(obj.df, obj.fps, obj.bps)


if __name__ == "__main__":
    main()
