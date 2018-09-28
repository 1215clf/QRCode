#二维码登录的问世，让人们更方便快捷的登录到pc端，简直是一个神奇的操作，带着崇敬之心，研究了下某宝的二维码登录，纯粹为了技术研究，如有不便，请联系作者，敬请谅解。
#copy一下百度上扫码登录流程
#扫码登录流程有以下几个步骤：

#1、非授信设备访问服务端生成token，并将token通过二维码展示在界面上；
#2、授信设备扫描展示在非授信设备上的二维码，获取到token；
#3、授信设备使用token访问服务端获取非授信设备的设备信息，并将非授信设备的设备信息展示在界面上，请用户确认；
#4、用户确认在授信设备上确认后，授信设备访问服务端，告知服务端该token已被用户确认可用来登录；
#5、非授信设备使用token登录。非授信设备并不知道用户何时会确认，所以需要轮询服务端，一直使用token尝试登录，直到成功；

import requests
import re,time

session = requests.session()

umid_token = 'HV01PAAZ0b887a7f65e60afe5bab23b900026d88'

headers = {}
# 请求头version=1，HTTP/1版本，else，HTTP/2版本
def getHeaders(version=1,method='GET',authority='',path='',referer='',scheme='https'):
    global headers
    if version == 1:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9'
        }
    else:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            # ':method':method,
            # ':authority':authority,
            # ':scheme':scheme,
            # ':path':path,
            'upgrade-insecure-requests': '1',
            'referer': referer,
        }
    return headers


def getPChome():
    url = 'https://login.taobao.com/member/login.jhtml'

    authority = 'login.taobao.com'
    scheme = 'https'
    path = '/member/login.jhtml'
    getHeaders(version=2,authority=authority,path=path,scheme=scheme)
    print(headers)

    result = session.get(url,headers = headers,verify =False)
    # print(result.content)



# 二维码登录
def generateQRCode(num):
    ksTs = getTimestamp() + '_'+ str(num)
    callback = 'jsonp' + str(num+1)
    url = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?adUrl=&adImage=&adText=&viewFd4PC=&viewFd4Mobile=&from=tb&appkey=00000000&umid_token=%s&_ksTS=%s&callback=%s'%(umid_token,ksTs,callback)
    result = session.get(url,headers=getHeaders(),verify=False)
    print(result.content)
    print(session.cookies)
    return re.findall(r'"lgToken":\"(.*?)\"',result.content.decode())[0]



    # magicString = '58EAFA5-E914-47DA-95CA-C5AB0DC85B11'
def qrCodeCheck(lgToken,num):
    i = 0
    header = getHeaders()
    header['Referer'] = 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
    while i < 100:
        ksTs = getTimestamp() + '_' + str(num)
        callback = 'jsonp' + str(num + 1)

        url = 'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=%s&defaulturl=http://world.taobao.com/&_ksTS=%s&callback=%s' % (
        lgToken, ksTs, callback)
        # session.cookies = requests.utils.cookiejar_from_dict(tbCookies)
        result = session.get(url, headers=header, verify=False)
        print(result.content.decode())
        code = re.findall(r'"code":\"(.*?)\"', result.content.decode())[0]
        print(code)
        if code == '10004':
            print('二维码失效')
            break
        elif code == '10006':
            print('确认登录')
            print(session.cookies)
            loginUrl = re.findall(r'"url":\"(.*?)\"', result.content.decode())[0]
            print(loginUrl)

            loginUrl = loginUrl.replace('http%3A%2F%2Fworld.taobao.com%2F', 'https://www.taobao.com/')

            QRCodeLogin(loginUrl+'&umid_token='+ umid_token)
            break
        elif code == '10001':
            print('扫描成功')
        i = i + 1
        time.sleep(1.5)


def getTimestamp():
    timeStamp = str(int(time.time()*1000))
    return timeStamp


def QRCodeLogin(url):
    result = session.get(url, headers=headers, verify=False)
    print(result.content.decode())
    print(result.cookies)



if __name__ == '__main__':
    getPChome()
    num = 29
    lgToken = generateQRCode(num)
    time.sleep(5)
    qrCodeCheck(lgToken, num)

    # print(getTimestamp())
