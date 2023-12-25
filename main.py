from os.path import exists
from pathlib import Path

import aiohttp
import asyncio
import sys
import time


async def check_address(address: str) -> tuple:
    eligible = False
    tokens = 0

    async with aiohttp.ClientSession() as session:
        params = {
            "address": address.lower()
        }

        async with session.get(
            "https://starkrocket.xyz/api/check_wallet",
            params=params
        ) as resp:
            json_resp = await resp.json()

        body = json_resp["result"]
        if body["eligible"]:
            eligible = True
            tokens = body["points"]

        return eligible, tokens


async def main():

    filename = ""
    while filename == "":
        f = input("Введите имя файла (без расширения .txt): ")
        if not exists(Path.cwd().joinpath(f"{f}.txt")):
            print(f"Файл {f}.txt не был найден! Проверьте имя файла, затем повторите попытку!")
        else:
            filename = f"{f}.txt"

    with open(filename, "r") as file:
        addresses = [row.strip() for row in file]

    if len(addresses) == 0:
        print("Файл с адресами пуст! Добавьте хотя бы один адрес.", file=sys.stderr)
        exit(-1)

    addr_len = len(addresses)

    print("Собираю данные...\n"
          f"• кол-во адресов: {addr_len}\n")

    start = int(time.time())

    tasks = [check_address(address) for address in addresses]
    r = await asyncio.gather(*tasks)

    results = {address: result for address, result in zip(addresses, r)}

    end = int(time.time())
    print(f"Данные собраны за {end - start} сек.! Провожу подсчёт...")

    eligible = 0
    total = 0
    for data in results.values():
        if data[0]:
            eligible += 1
            total += data[1]

    print(f"Подсчёт окончен!\n"
          f"• кол-во адресов, которые получат токены: {eligible}\n"
          f"• кол-во адресов, не прошедшие отбор: {addr_len - eligible}\n"
          f"• суммарное кол-во токенов: {total} $STRKR")


if __name__ == "__main__":
    asyncio.run(main())
