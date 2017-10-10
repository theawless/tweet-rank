from sys import argv

from gi.repository import Gtk, Gdk

from common.mongo import get_tweets, annotations_collection
from common.utils import tweets_chunk_by_time


class Application(Gtk.Application):
    annotate_range = 5

    def __init__(self):
        super().__init__()
        self._setup_ui()

        self.tweet_index = 0
        self.hour = int(argv[1])
        self.left = int(argv[2])
        self.right = int(argv[3])
        self.tweets = tweets_chunk_by_time(get_tweets())[self.hour][self.left:self.right]
        self._update_tweet()

    def _setup_ui(self):
        self.ui = Gtk.Builder.new_from_file("data/annotate.glade")
        self.ui.connect_signals(self)
        self.window = self.ui.get_object("application_window")
        self.window.connect("key-release-event", self.key_released)

        self.tweet_index_label = self.ui.get_object("tweet_index_label")
        self.tweet_text_label = self.ui.get_object("tweet_text_label")
        self.button_box = self.ui.get_object("button_box")
        self.next_button = self.ui.get_object("next_button")
        self.previous_button = self.ui.get_object("previous_button")
        self.annotation_buttons = []

        for i in range(1, self.annotate_range + 1):
            button = Gtk.Button(label=str(i))
            self.annotation_buttons.append(button)
            button.connect("clicked", self.annotate_button_pressed, i)
            self.button_box.pack_start(button, False, False, 0)
            button.show()

    def _update_tweet(self):
        if not (0 <= self.tweet_index < len(self.tweets)):
            return
        tweet = self.tweets[self.tweet_index]
        self.tweet_text_label.set_label(tweet["text"])
        self.tweet_index_label.set_label("Index: " + str(self.tweet_index) + " " +
                                         "Out of: " + str(len(self.tweets)) + " " +
                                         "Tweet ID: " + tweet["id_str"])

    def next_button_pressed(self, _):
        self.tweet_index += 1
        self._update_tweet()

    def previous_button_pressed(self, _):
        self.tweet_index -= 1
        self._update_tweet()

    def annotate_button_pressed(self, _, i):
        tweet = self.tweets[self.tweet_index]
        annotation = {"tweet_id_str": tweet["id_str"], "annotation": str(i)}
        annotations_collection.update_one({"tweet_id_str": tweet["id_str"]}, {"$set": annotation}, upsert=True)

    def key_released(self, _, event_key):
        if event_key.keyval in (Gdk.KEY_N, Gdk.KEY_n):
            self.next_button.emit("activate")
            self.next_button_pressed(None)
        elif event_key.keyval in (Gdk.KEY_p, Gdk.KEY_P):
            self.previous_button.emit("activate")
            self.previous_button_pressed(None)
        elif 0 <= event_key.keyval - Gdk.KEY_1 <= self.annotate_range:
            self.annotation_buttons[event_key.keyval - Gdk.KEY_1].emit("activate")
            self.annotate_button_pressed(None, event_key.keyval - Gdk.KEY_0)

    def do_activate(self):
        self.window.set_application(self)
        self.window.present()


if __name__ == "__main__":
    application = Application()
    application.run()
