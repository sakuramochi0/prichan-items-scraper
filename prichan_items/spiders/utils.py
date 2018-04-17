import re

import requests
import zenhan


def create_note_dict():
    """
    アイテムのIDと、そのIDから適用されるノート情報の対応マップを生成する

    たとえば、プロモページ( https://prichan.jp/items/promotion.html )には
    「2018年4月発売　みらい＆えも プリチケセット」という note 情報が表示されているはずです。
    この情報は、そのヘッダ以降の1つ以上のアイテムに対する note 情報になっています。

    プリパラのアイテムページでは詳細ページにこのデータが記録されていたけれど、
    itemIDを表面化させるという謎の仕様変更とともにアイテム詳細ページには表示されなくなってしまいました(なぜ？)。

    このノート情報は、この関数に書かれたURLのJavaScriptで挿入位置をスクリプト中で(！)指定して、後から挿入されています。
    JavaScriptをレンダリングする方法がうまく行かなかったので、
    手動でパースして必要な情報が入ったディクショナリを作ることにしました。

    壊れやすそうだから、もっといい方法はないかな？

    返り値は次のような {コーデID: noto情報} という形式になっています。
        {
            'G-01': "Girl's Yell",
            'P-01': '2018年4月発売 みらい&えも プリチケセット',
            ...
        }
    """

    def z2h(text):
        return zenhan.z2h(text, mode=zenhan.ASCII | zenhan.DIGIT)

    url = 'https://prichan.jp/resources/js/script.js'
    r = requests.get(url)
    r.encoding = 'utf-8'
    id_note_pairs = re.findall(r''''#(.+?)'.+"-title">([^<]+)</div>''', r.text)
    return dict((k, z2h(v).replace('\\', '')) for k, v in id_note_pairs)
