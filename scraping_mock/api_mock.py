import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

API_URL = "https://www.binance.com/bapi/futures/v1/private/future/copy-trade/copy-portfolio/query-copy-portfolio-mock"
print("API_URL: " + API_URL)

if __name__ == "__main__":    
    
    headers = {
        # ':authority': 'www.binance.com',
        # ':method': 'POST',
        # ':path': '/bapi/futures/v1/private/future/copy-trade/copy-portfolio/query-copy-portfolio-mock',
        # ':scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,uk-UA;q=0.6,uk;q=0.5',
        'bnc-level': '0',
        'bnc-location': 'UA',
        'bnc-time-zone': 'Europe/Kiev',
        'bnc-uuid': '480b266a-90f3-4754-bb9e-de50f940918b',
        'clienttype': 'web',
        'content-length': '2',
        'content-type': 'application/json',
        'cookie': 'theme=dark; bnc-uuid=480b266a-90f3-4754-bb9e-de50f940918b; userPreferredCurrency=USD_USD; BNC_FV_KEY=3372fd2d2390a12f8cbd41e9a20f2a405b18cbd6; OptanonAlertBoxClosed=2025-01-15T18:18:30.928Z; _ga_MEG0BSW76K=GS1.1.1744125596.2.0.1744125596.0.0.0; se_sd=FZSEABR0VHVBwoZAMAVQgZZXQDRcLEVUloW9eW05lRXWgBVNWV8M1; se_gd=QtWCgWxAQQBDF0FFRD1ggZZD1VhMRBVU1UO9eW05lRXWgWlNWV4V1; se_gsd=dDAnK0JxNSAlGSMyIQM0MxcyUFVXDgZVUV9DWlxVV1RRVFNT1; currentAccount=; logined=y; fiat-prefer-currency=UAH; language=ru-UA; BNC-Location=UA; changeBasisTimeZone=; neo-theme=dark; language=en; lang=ru-UA; _gid=GA1.2.1106229383.1748532022; _gcl_au=1.1.1014950398.1744896673.1352275299.1748670440.1748670440; s9r1=9A825D35E042583C89DB806D092E435F; r20t=web.7F6742A4A2B9FE064E69BB4C4948DEE8; r30t=1; cr00=F0F02AE6766ED3FEBCE630C49B4A7802; d1og=web.1104413158.D44A4621B46A966118DD96EE4E8E7910; r2o1=web.1104413158.4C80022F4D96E9149A15077C54228B8A; f30l=web.1104413158.C98967E8B2D020C10DDEDA7ACC644717; p20t=web.1104413158.86F409B2F5D413AB3715D3684187B073; aws-waf-token=e59af699-a615-4aa5-b9ee-6ad1125fddb8:CgoAlF1FyjFvAAAA:pPYMNuhqa7Mj4eFshY0AK3nXx4kHcOxkasoy3sZM6qbmoP/znESFD3cg/gvd+nvnk4yMFlm3JOlHQf/5sBPLQOBDQqXg8i11GJ+fvv84Zb1+1Gdira68ktHm18NidrTy30hYTK9GT4rsmBLeLi0F7cAOzix2Yl44v+DbbbIR3P2bJCLSFFxCimun7ug9XnLr+dU=; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221104413158%22%2C%22first_id%22%3A%22192f735323e444-02ce6a55435a87e-26011951-1049088-192f735323f7ff%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjczNTMyM2U0NDQtMDJjZTZhNTU0MzVhODdlLTI2MDExOTUxLTEwNDkwODgtMTkyZjczNTMyM2Y3ZmYiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTA0NDEzMTU4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221104413158%22%7D%2C%22%24device_id%22%3A%22195d39c3ea57b-0f7b9adc12343c-26011a51-1049088-195d39c3ea6176%22%7D; futures-layout=pro; _uetsid=8a14d7403d7f11f08eaa6f72b12d5a6d; _uetvid=2a237f90d4ae11ef9b593b33c79e1949; BNC_FV_KEY_T=101-KLGXPYS2Q%2FMoWkDHoPInMjaX0hf2X001y8XVm36lP0e6ey9jYkpmmsZLis7bGmEsNKGKYj5S2WwJEYY44b1gVg%3D%3D-7KcDOICi5wBSMfl0J%2Fse%2FQ%3D%3D-7d; BNC_FV_KEY_EXPIRE=1749067270120; _gat_UA-162512367-1=1; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+04+2025+17%3A11%3A35+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=94a41464-617c-4a0e-ab67-e59c073a4778&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&intType=1&geolocation=PL%3B14; _ga_3WP50LGEEC=GS2.1.s1749045064$o296$g1$t1749046296$j45$l0$h0; _ga=GA1.1.1259565346.1730724313',
        'csrftoken': '80bd70ee23c7355824be79db110d4cb8',
        'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6Ijc2OCwxMzY2IiwiYXZhaWxhYmxlX3NjcmVlbl9yZXNvbHV0aW9uIjoiNzI4LDEzNjYiLCJzeXN0ZW1fdmVyc2lvbiI6IldpbmRvd3MgMTAiLCJicmFuZF9tb2RlbCI6InVua25vd24iLCJzeXN0ZW1fbGFuZyI6ImVuLVVTIiwidGltZXpvbmUiOiJHTVQrMDM6MDAiLCJ0aW1lem9uZU9mZnNldCI6LTE4MCwidXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMzcuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImxpc3RfcGx1Z2luIjoiUERGIFZpZXdlcixDaHJvbWUgUERGIFZpZXdlcixDaHJvbWl1bSBQREYgVmlld2VyLE1pY3Jvc29mdCBFZGdlIFBERiBWaWV3ZXIsV2ViS2l0IGJ1aWx0LWluIFBERiIsImNhbnZhc19jb2RlIjoiZTU0Y2QwMzMiLCJ3ZWJnbF92ZW5kb3IiOiJHb29nbGUgSW5jLiAoSW50ZWwpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoSW50ZWwsIEludGVsKFIpIEhEIEdyYXBoaWNzIEZhbWlseSAoMHgwMDAwMEExNikgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJFdXJvcGUvS2lldiIsImRldmljZV9uYW1lIjoiQ2hyb21lIFYxMzcuMC4wLjAgKFdpbmRvd3MpIiwiZmluZ2VycHJpbnQiOiIzYzk3MDA2NGI5MjY4NjY1ZTU2NzUwYWNiZDVmYzk4ZSIsImRldmljZV9pZCI6IiIsInJlbGF0ZWRfZGV2aWNlX2lkcyI6IiJ9',
        'fvideo-id': '3372fd2d2390a12f8cbd41e9a20f2a405b18cbd6',
        'fvideo-token': 'D9fiaAec18f9td+9hFyiCVNgnS4KkddE/bl4Wrf14vdsv61JuAWEjgGNvGPQAwfEMsE6MBRYJRQu0kQHqrNHJb9Wk8qoHhs6LcK90zH/1197I5fSHWz0MvSEoSERs0RP9FA7Jlzlmswlc9nMsXODm9fKeshW9ewvyVh7u80hthizNQtXWL+/IUcMib/MwSm/I=7e',
        'lang': 'ru-UA',
        'origin': 'https://www.binance.com',
        'priority': 'u=1, i',
        'referer': 'https://www.binance.com/ru-UA/copy-trading/copy-management',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'x-passthrough-token': '',
        'x-trace-id': '7bf7a4b4-0e61-46b8-8c2f-15015d5df45b',
        'x-ui-request-trace': '7bf7a4b4-0e61-46b8-8c2f-15015d5df45b'
    }

    payload = {}

    response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    json_response_data = response.json()
    print(json_response_data)
