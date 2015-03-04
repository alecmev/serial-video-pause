"""Send some data over serial and then play a video."""

import _thread
import argparse
import functools
import os
import threading
import time
import tkinter

import serial
import serial.tools.list_ports

import vlc


def async(f):
    """Run in a new thread decorator."""
    @functools.wraps(f)
    def wrapper(*args):
        _thread.start_new_thread(f, args)

    return wrapper


class Main():

    """Main class."""

    def __init__(self, args):
        """Constructor."""
        with open(args.meta) as metafile:
            self.meta = bytes.fromhex(''.join(metafile.read().split()))

        self.com = serial.Serial(args.port, 115200, writeTimeout=0)
        self.pause = args.pause
        self.short = args.short
        self.debug = time.time() if args.debug else False

        self.window = tkinter.Tk()
        self.window.config(bg='black')
        if args.windowed:
            self.window.geometry('640x480')
        else:
            self.window.attributes('-fullscreen', True)

        self.media_player = vlc.MediaPlayer(vlc.Instance('vlc'), args.video)
        self.media_player.set_hwnd(self.window.winfo_id())
        self.media_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerPlaying, self.meta_callback
        )
        self.media_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerBuffering, self.meta_callback
        )
        self.media_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self.end_reached_callback
        )
        if self.short:
            media = self.media_player.get_media()
            media.parse()
            self.short_time = media.get_duration() - 2000

        self.play_video()
        self.window.mainloop()

    @async
    def play_video(self):
        """Play video."""
        self.log('play_video')
        self.meta_sent = False
        self.media_player.play()
        if self.short:
            self.media_player.set_time(self.short_time)

    @async
    def meta_callback(self, event):
        """Video playing / buffering."""
        self.log('meta_callback')
        if self.meta_sent:
            self.log('nevermind, meta already sent')
            return

        try:
            self.meta_timer.cancel()
        except:
            pass

        self.meta_timer = threading.Timer(0.3, self.send_meta)
        self.meta_timer.start()

    @async
    def send_meta(self):
        """Send instructions."""
        self.log('send_meta')
        if self.meta_sent:
            self.log('nevermind, meta already sent')
            return

        self.meta_sent = True
        self.com.write(self.meta)
        self.log('meta sent')

    @async
    def end_reached_callback(self, event):
        """Video ended."""
        self.log('end_reached_callback')
        self.media_player.stop()
        time.sleep(self.pause)
        self.play_video()

    @async
    def log(self, text):
        """Log helper."""
        if self.debug:
            print(
                '[{:>10}] '.format(
                    round((time.time() - self.debug) * 1000)
                ) + text
            )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    def existing_file(arg):
        """Check if a file exists."""
        if not os.path.exists(arg):
            parser.error('The file %s does not exist!' % arg)
        else:
            return arg

    def existing_port(arg):
        """Check if a serial port exists."""
        arg = arg.upper()
        for port, _, _ in serial.tools.list_ports.comports():
            if port == arg:
                return arg

        parser.error('The port %s does not exist!' % arg)

    parser.add_argument(
        'video',
        metavar='<video>',
        type=existing_file,
        help='video file'
    )
    parser.add_argument(
        'meta',
        metavar='<meta>',
        type=existing_file,
        help='instruction file'
    )
    parser.add_argument(
        'port',
        metavar='<port>',
        type=existing_port,
        help='serial port to send instructions to'
    )
    parser.add_argument(
        'pause',
        metavar='<pause>',
        type=int,
        help='delay between playbacks, in seconds'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='enable debug output'
    )
    parser.add_argument(
        '-w', '--windowed',
        action='store_true',
        help='windowed mode'
    )
    parser.add_argument(
        '-s', '--short',
        action='store_true',
        help='play only last 2 seconds'
    )

    Main(parser.parse_args())
