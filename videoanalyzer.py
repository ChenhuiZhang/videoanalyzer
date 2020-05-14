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

def pyav_analyze(video):
    with av.open(video) as container:
        container.streams.video[0].thread_type = 'AUTO'

        video = container.streams.video[0]
        print(f'fps: {video.framerate} = {float(video.framerate)}')
        print(f'bit: {container.bit_rate}')

        rows = []
        pkt_size = []
        # df = pd.DataFrame[[f.time, f.dts] for f in container.decode(video=0)]
        for packet in container.demux(video=0):
            if packet.size != 0.0:
                pkt_size.append(packet.size)
            for frame in packet.decode():
                rows.append([frame.time, frame.pict_type])

        df = pd.DataFrame(rows, columns=["pkt_pts_time", "pict_type"])
        df["pkt_size"] = pkt_size

        return df

def ffmpeg_analyze(file):
    probe = ffmpeg.probe(file,
                         show_entries="frame=pkt_pts_time,pict_type,pkt_size",
                         select_streams="v:0")
    print(probe["format"]["bit_rate"])
    print(probe["streams"][0]["r_frame_rate"])

    df = pd.DataFrame.from_records(probe["frames"])
    df["pkt_size"] = pd.to_numeric(df["pkt_size"])
    df["pkt_pts_time"] = pd.to_numeric(df["pkt_pts_time"])
    return df

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

def plot_bitrate_and_frame(df):
    pts_I = np.array(df[df['pict_type'] == 'I']["pkt_pts_time"])
    pts_P = np.array(df[df['pict_type'] == 'P']["pkt_pts_time"])
    pts_B = np.array(df[df['pict_type'] == 'B']["pkt_pts_time"])
    pts_all = np.array(df["pkt_pts_time"])

    pkt_I = np.array(df[df['pict_type'] == 'I']["pkt_size"])
    pkt_P = np.array(df[df['pict_type'] == 'P']["pkt_size"])
    pkt_B = np.array(df[df['pict_type'] == 'B']["pkt_size"])

    # Setting up the plot surface
    fig = plt.figure(figsize=(10, 5))
    gs = GridSpec(nrows=2, ncols=1, height_ratios=[5, 1])  # First axes

    # Bitrate plot
    ax0 = fig.add_subplot(gs[0, 0])

    ax0.title.set_text('Bitrate')
    #ax0.ylabel('Damped oscillation')

    plt.vlines(pts_I, 0, pkt_I, color=frame_type_color['I'])
    plt.vlines(pts_P, 0, pkt_P, color=frame_type_color['P'])
    plt.vlines(pts_B, 0, pkt_B, color=frame_type_color['B'])

    # Frame  interval plot
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.title.set_text('Frames interval')
    ax1.plot(np.diff(pts_all))

    plt.show()

def main(file):
    plot_bitrate_and_frame(pyav_analyze(file))


if __name__ == "__main__":
    main(sys.argv[1])
