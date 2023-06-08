import requests
import json
import pytz

from datetime import datetime

# const
TZ = pytz.timezone("Asia/Shanghai")
TIME_NOW = datetime.now(TZ).strftime('%Y/%m/%d %H:%M:%S')

MESSAGE_TITLE = '发现香港身份证预约空位'
ITEM = "- 日期：{date}，办事处：{office_name}\n"
TEXT = f"## 请前往 https://www.gov.hk/en/apps/immdicbooking2.htm 预约\n\n"

EXCEPTION_MESSAGE = {
    "text": "remote Hong Kong Id reservation service busy",
    "desp": "retry later"
}

# bool value, True if found available
FOUND = False
QUOTA_G = 'quota-g'  # quota available flag


def send_message_fangtang(_item=None, _message=None, _d=None):
    PUSH_KEY = '<SENDKEY>'  #TODO 微信推送配置参考https://sct.ftqq.com/ 将key填入即可（去掉<>）
    _d = {
        "text": _message,
        "desp": _item + "### time: {}".format(TIME_NOW)
    } if not _d else _d
    response = requests.post(f"https://sc.ftqq.com/{PUSH_KEY}.send", data=_d)
    print("方糖：", response.text)


def get_reservation_info():
    """
    get the reservation infomation from the api
    :return:
    office_dict: {office_id: office_name]
    reserve_data: reservation data of each office
    """
    url = "https://eservices.es2.immd.gov.hk/surgecontrolgate/ticket/getSituation"
    payload = {}
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-AU,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://eservices.es2.immd.gov.hk/es/quota-enquiry-client/?l=en-US&appId=579',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    r = json.loads(response.text)
    # get the office id and name dictionary
    try:
        office_dict = {office['officeId']: office['cht']['officeName'] for office in r['office']}
        reserve_data = r['data']
        return office_dict, reserve_data
    except KeyError:
        send_message_fangtang(_d=EXCEPTION_MESSAGE)
        exit()


if __name__ == '__main__':
    office_dict, reserve_data = get_reservation_info()

    for data in reserve_data:
        if data['quotaR'] == QUOTA_G:
            office_name = office_dict[data['officeId']]
            TEXT += ITEM.format(date=data['date'], office_name=office_name)
            FOUND = True

    if FOUND:
        send_message_fangtang(TEXT, MESSAGE_TITLE)
