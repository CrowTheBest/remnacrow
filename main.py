import asyncio

from remnacrow import RemnawaveClient
from remnacrow.enums import UserField, FilterMode, HwidField
from remnacrow.models import Filter, Sort

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiNGVhNzdkNzUtOTgxMC00YWRiLThjZWQtNWI4YjkyMTVhMjc0IiwidXNlcm5hbWUiOm51bGwsInJvbGUiOiJBUEkiLCJpYXQiOjE3NTk2ODAxMTEsImV4cCI6MTAzOTk1OTM3MTF9.uxGvWpLvzfkbuccdDbKVzeIe7sjt04yTuTCTSsI4J5U"

client = RemnawaveClient("admin.ktoygaday.xyz", TOKEN)


async def main() -> None:
        udid = '352528c7-c70e-4cb4-8fc6-40d73fe95e18'

        # print(((await client.users.get_users(start=50,
        #                                      size=10,
        #                                      filters=[Filter(UserField.TAG, 'PRIVATE')],
        #                                      sort=[Sort(UserField.TAG, desc=True),
        #                                            Sort(UserField.USERNAME)]))))

        # print(await client.users.get_users_by_telegram_id(telegram_id=946562779))
        print(await client.hwid.get_devices(filters=[
                Filter(HwidField.PLATFORM, 'android')
        ],
        sort=[Sort(HwidField.OS_VERSION)]))



asyncio.run(main())
