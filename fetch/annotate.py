from gi.repository import Gtk, Gdk

import common.mongo
import common.settings
import common.tweets


class Application(Gtk.Application):
    def __init__(self):
        super().__init__()
        self.annotate_range = common.settings.annotate.getint("Range")
        self._setup_ui()

        left = common.settings.annotate.getint("Offset")
        right = left + common.settings.annotate.getint("Limit")
        self.tweets = common.mongo.get_tweets(hour=common.settings.annotate.getint("Hour"))[left:right]
        self.tweet_index = 0
        self._update_tweet()

    def _setup_ui(self):
        self.ui = Gtk.Builder.new_from_file("data/annotate.ui")
        self.ui.connect_signals(self)
        self.window = self.ui.get_object("application_window")
        self.window.connect("key-release-event", self.key_released)

        self.tweet_index_label = self.ui.get_object("tweet_index_label")
        self.tweet_text_label = self.ui.get_object("tweet_text_label")
        self.button_box = self.ui.get_object("button_box")
        self.help_button = self.ui.get_object("help_button")
        self.help_button.set_tooltip_text(common.settings.annotate.getstring("HelpText"))
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
        tweet = self.tweets[self.tweet_index]
        self.tweet_text_label.set_label(tweet["text"])
        self.tweet_index_label.set_label("Index: " + str(self.tweet_index) + " " +
                                         "Out of: " + str(len(self.tweets)) + " " +
                                         "Tweet ID: " + tweet["id_str"])

        for button in self.annotation_buttons:
            button.get_style_context().remove_class("suggested-action")
        annotation = common.mongo.annotations_collection.find_one({"id_str": tweet["id_str"]})
        if annotation is not None:
            index = annotation["annotation"] - 1
            if 0 <= index < self.annotate_range:
                self.annotation_buttons[index].get_style_context().add_class("suggested-action")

    def next_button_pressed(self, _):
        if self.tweet_index == len(self.tweets) - 1:
            return
        self.tweet_index += 1
        self._update_tweet()

    def previous_button_pressed(self, _):
        if 0 == self.tweet_index:
            return
        self.tweet_index -= 1
        self._update_tweet()

    def annotate_button_pressed(self, _, i):
        tweet = self.tweets[self.tweet_index]
        annotation = {"id_str": tweet["id_str"], "annotation": i, "tag": common.settings.annotate.getstring("Tag")}
        common.mongo.annotations_collection.update_one({"id_str": annotation["id_str"]}, {"$set": annotation},
                                                       upsert=True)
        self._update_tweet()

    def key_released(self, _, event_key):
        if event_key.keyval in (Gdk.KEY_N, Gdk.KEY_n):
            self.next_button_pressed(None)
        elif event_key.keyval in (Gdk.KEY_p, Gdk.KEY_P):
            self.previous_button_pressed(None)
        elif 0 <= event_key.keyval - Gdk.KEY_1 < self.annotate_range:
            self.annotate_button_pressed(None, event_key.keyval - Gdk.KEY_0)

    def do_activate(self):
        self.window.set_application(self)
        self.window.present()


if __name__ == "__main__":
    application = Application()
    application.run()
