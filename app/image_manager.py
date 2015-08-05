__author__ = 'croxis'
import os.path

from PIL import Image

COLORS = {'white': 'w',
          'black': 'b',
          'blue': 'u',
          'green': 'g',
          'red': 'r',
          'colorless': 'c',
          'artifact': 'a'}
C = {v: k for k, v in COLORS.items()}


class ImageManager:
    def __init__(self,
                 root_path='app/card_parts/',
                 card_path='magic-new.mse-style/',
                 icon_path='magic-mana-beveled.mse-symbol-font/',
                 icon_text_path='magic-mana-small.mse-symbol-font/'):
        self.card_path = os.path.join(root_path, card_path)
        self.icon_path = os.path.join(root_path, icon_path)
        self.icon_text_path = os.path.join(root_path, icon_text_path)
        self.cards = {}
        self.icons = {}
        self.icons_text = {}

        for color in COLORS:
            self.cards[color] = Image.open(self.card_path + COLORS[color] + 'card.jpg')

        for name in ['w', 'b', 'u', 'g', 'r']:
            self.icons[C[name]] = Image.open(self.icon_path + 'mana_' + name + '.png')

        self.icons['tap'] = Image.open(self.icon_path + 'mana_t.png')
        self.icons['colorless'] = Image.open(self.icon_path + 'mana_circle.png')

        for icon in self.icons.values():
            icon.thumbnail((22, 22))

        for name in ['w', 'b', 'u', 'g', 'r']:
            self.icons_text[C[name]] = Image.open(self.icon_text_path + 'mana_' + name + '.png')

        self.icons_text['tap'] = Image.open(self.icon_text_path + 'mana_t.png')
        self.icons_text['colorless'] = Image.open(self.icon_text_path + 'mana_circle.png')

        for icon in self.icons_text.values():
            icon.thumbnail((18, 18))


    def get_background(self, color):
        return self.cards[color].copy()


    def get_icon(self, name):
        if name == 'colorless':
            return self.icons[name].copy()
        return self.icons[name]


    def get_icon_text(self, name):
        if name == 'colorless':
            return self.icons_text[name].copy()
        return self.icons_text[name]


