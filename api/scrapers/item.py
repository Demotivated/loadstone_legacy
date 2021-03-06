import logging
import threading
from lxml import html
import requests
from api.constants import USER_AGENT
from api.exceptions import ParsingException
from api.models import Item

__author__ = 'sami'


def scrape_item_by_id(lodestone_id):
    """
    .. image:: ../images/item_lodestone_id.PNG

    >>> thyrus = scrape_item_by_id('d19447e548d')
    >>> thyrus.name
    'Thyrus Zenith'
    >>> thyrus.item_level
    90

    :param lodestone_id: Alpha-numeric ID in the URL of the item's Lodestone page
    :return: New / updated :class:`api.models.Item`
    :raise ParsingException: Unexpected errors while scraping the HTML will throw
    """
    logging.debug('Attempting to parse items from id {}'.format(lodestone_id))

    try:
        headers = {'User-Agent': USER_AGENT}
        uri = 'http://na.finalfantasyxiv.com/lodestone/playguide/db/item/{}/'.format(lodestone_id)
        page = requests.get(uri, headers=headers)
        assert page.status_code == 200

    except AssertionError:
        raise ParsingException('Invalid response from Lodestone')

    try:
        tree = html.fromstring(page.text)

        item, _ = Item.objects.get_or_create(lodestone_id=lodestone_id)
        item.name = tree.xpath('//title/text()')[0].split('|')[0].replace('Eorzea Database:', '').strip()
        header = tree.xpath('//div[@class="clearfix item_name_area"]/div[@class="box left"]/text()')
        item.item_type = header[2].strip()

        ilvl = int(tree.xpath('//div[@class="eorzeadb_tooltip_pt3 eorzeadb_tooltip_pb3"]/text()')[0].
                   replace('Item Level ', ''))
        if ilvl is not None:
            item.item_level = ilvl
        else:
            item.item_level = 0

        main_stats = tree.xpath('//div[@class="clearfix sys_nq_element"]/div/strong/text()')
        if main_stats:
            if item.item_type == "Shield":
                item.block_strength = int(main_stats[0])
                item.block_rate = int(main_stats[1])
            elif len(main_stats) == 2:
                item.defense = int(main_stats[0])
                item.magic_defense = int(main_stats[1])
            else:
                item.damage = int(main_stats[0])
                item.auto_attack = float(main_stats[1])
                item.delay = float(main_stats[2])

        basic_stats = tree.xpath('//ul[@class="basic_bonus"]/li/text()')
        for stat_string in basic_stats:
            stat_split = stat_string.split('+')
            stat = stat_split[0].strip()
            value = int(stat_split[1].strip())

            # TODO add the remaining stats
            if stat == 'Vitality':
                item.vitality = value

            elif stat == 'Mind':
                item.mind = value

            elif stat == 'Determination':
                item.determination = value

            elif stat == 'Spell Speed':
                item.spell_speed = value

            elif stat == 'Accuracy':
                item.accuracy = value

            elif stat == 'Critical Hit Rate':
                item.critical_hit_rate = value

            elif stat == 'Piety':
                item.piety = value

            else:
                logging.error('Unable to properly match the stat {}'.format(stat))

        item.save()

    except (IndexError, ValueError):
        raise ParsingException('Unable to parse item id {} from lodestone'.format(lodestone_id))

    return item


class ItemThread(threading.Thread):

    def __init__(self, item_id):
        threading.Thread.__init__(self)
        self.item_id = item_id
        self._item = None

    def run(self):
        self._item = scrape_item_by_id(self.item_id)

    def join(self, timeout=None):
        threading.Thread.join(self)
        return self._item

    def __repr__(self):
        return '<ItemThread item={}>'.format(
            self._item.__repr__()
        )
