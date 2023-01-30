import asyncio
import json
import aiohttp

graphs = {
    "up": "◢ ",
    "down": "◣",
    "no_changes": "▸"
}

emoji_change = {
    "no_changes": "⏹",
    "up": "⬆️",
    "down": "⬇️",
}

string_scheme = """{emoji_change} {name}: {value_ton} Ton / ${value_dollar} | {graph} {percent_change}%
      ┗━ 📊 24h: {day_in_ton} TON\n"""


class Parser:
    def __init__(self):
        self.url = 'https://api.dedust.io/cmc/dex'
        self.ton_rate_url = 'https://min-api.cryptocompare.com/data/price?fsym=TON&tsyms=USD'

    async def ton_to_dollar(self, ton_price):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.ton_rate_url) as response:
                ton_rate = await response.json()
        dollar_price = round(ton_price * ton_rate["USD"], 8)
        return dollar_price

    async def get_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                return await response.text()

    async def read_config(self):
        with open('config.json') as json_file:
            data = json.load(json_file)
            return data

    async def save_config(self, config):
        with open('config.json', 'w') as json_file:
            # json_file.write(str(config))
            json.dump(config, json_file)

    async def message_scheme(self, **kwargs):
        if kwargs['old_last_price'] == kwargs['new_last_price']:
            emoji_change_1 = emoji_change['no_changes']
        elif kwargs['old_last_price'] > kwargs['new_last_price']:
            emoji_change_1 = emoji_change['down']
        elif kwargs['old_last_price'] < kwargs['new_last_price']:
            emoji_change_1 = emoji_change['up']
        if kwargs['old_quote_volume'] == kwargs['new_quote_volume']:
            emoji_change_2 = graphs['no_changes']
        elif kwargs['old_quote_volume'] > kwargs['new_quote_volume']:
            emoji_change_2 = graphs['down']
        elif kwargs['old_quote_volume'] < kwargs['new_quote_volume']:
            emoji_change_2 = graphs['up']

        coin_string = string_scheme.format(
            emoji_change=emoji_change_1,
            name=kwargs['name'],
            value_ton=kwargs['new_last_price'],
            value_dollar=kwargs['new_dollar'],
            graph=emoji_change_2,
            percent_change=round(
                ((kwargs['new_last_price'] - kwargs['old_last_price']) / kwargs['old_last_price']) * 100, 3),
            day_in_ton=kwargs['new_quote_volume']
        )
        return coin_string

    async def runner(self):
        message = ""

        api_data = await self.get_data()
        api_data = json.loads(api_data)
        config_data = await self.read_config()
        for coin in config_data["addresses"]:
            address = coin['address']
            api_address_data = api_data[address]

            old_last_price = coin['last_price']
            old_quote_volume = coin['quote_volume']
            new_last_price = round(float(api_address_data['last_price']), 8)
            new_quote_volume = round(float(api_address_data['quote_volume']), 8)
            new_dollar = await self.ton_to_dollar(new_last_price)
            message += await self.message_scheme(name=coin["name"], new_last_price=new_last_price,
                                                 old_last_price=old_last_price, new_dollar=new_dollar,
                                                 old_quote_volume=old_quote_volume,
                                                 new_quote_volume=new_quote_volume)
            coin['last_price'] = new_last_price
            coin['quote_volume'] = new_quote_volume
        await self.save_config(config_data)
        return message


if __name__ == '__main__':
    p = Parser()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(p.runner())
