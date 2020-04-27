import web
import FRSHDataLakeCommandBase
import os
import base64
import zipfile
import time

urls = (
    '/getdl', 'getdownload',
    '/dl', 'download',
    '/doc', 'docdownload',
    '/sample', 'samplecode',
    '/', 'index'

)
render = web.template.render('html/')
global local_cache
local_cache = "C:\Temp"


class docdownload:
    def GET(self):
        return "Page in construction."


class samplecode:
    def GET(self):
        return "Page in construction."


class index:
    def GET(self):
        return render.index()


class getdownload:
    def GET(self):
        d = web.input()
        fp = FRSHDataLakeCommandBase.FRSHDataLakeCommandBase(None, None)
        if not d.path:
            return self.errormsg()
        try:
            fullpath = str(d.path).replace('\n', '').replace(" ", "").replace("\r\n", "")  # s3 full path
            fn = fp.getfilenamefrompath(fullpath)  # csv name
            sfdn = fn.split(".")[0]  # without .csv
            fdn = local_cache + os.path.sep + sfdn  # local dir full name
            if not os.path.exists(fdn):
                os.mkdir(fdn)
                fp.getfile(fullpath, fdn + os.path.sep + fn)
            url = "/dl?sfdn=%s" % base64.b64encode(sfdn.encode('utf-8'))
            return self.formata(url)
        except Exception as ext:
            return self.errormsg(ext.message)

    def formata(self, url):
        tpl = "<a href='%s'>Click to download</a>"
        rs = tpl % url
        return rs

    def errormsg(self, em=""):
        return "Fail to download the sample path you input, please check.<br /> %s" % em


class download:
    def GET(self):
        d = web.input()
        b64sfdn = d.sfdn
        b64fdn = local_cache + os.path.sep + b64sfdn
        sfdn = base64.b64decode(b64sfdn).decode("utf-8")
        fdn = local_cache + os.path.sep + sfdn
        if not os.path.exists(b64fdn):
            os.mkdir(b64fdn)
        if len(os.listdir(b64fdn)) == 0:
            with zipfile.ZipFile(time.strftime(b64fdn + os.path.sep + '%Y-%m-%d-%H-%M-%S.zip'), 'w') as target:
                for i in os.walk(fdn):
                    for n in i[2]:
                        target.write(''.join((i[0], '\\', n)), arcname=n)
        zipfullname = b64fdn + os.path.sep + os.listdir(b64fdn)[0]
        try:
            f = open(zipfullname, "rb")
            web.header('Content-Type', 'application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s.zip' % sfdn)
            while True:
                c = f.read(262144)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error'
        finally:
            if f:
                f.close()


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()