import pprint as pp
'''
'''
SNAPSHOTS = {'closest': {'status': '200', 'available': True,
                         'url': 'http://web.archive.org/web/20130103084334/https://www.lytro.com/', 'timestamp': '20130103084334'}}
CLOSEST = {'status': '200', 'available': True,
           'url': 'http://web.archive.org/web/20130103084334/https://www.lytro.com/', 'timestamp': '20130103084334'}

# pp.pprint(SNAPSHOTS)
# pp.pprint(CLOSEST)


done_urls = {2013: {'http://web.archive.org/web/20130103084334/https://www.lytro.com/': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/store': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/camera': 1, 'http://web.archive.org/web/20130103084334/https://pictures.lytro.com/': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/learn': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/users/sign_in': 1,
                    'http://web.archive.org/web/20130103084334/https://www.lytro.com/accessories': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/privacy': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/misc/Redline_Privacy_Policy_(October_9,_2012_versus_October_19,_2011).pdf': 0, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/legal/terms-of-use': 1, 'http://web.archive.org/web/20130103084334/https://www.lytro.com/misc/Redline_Terms_of_Use_(October_9,_2012_versus_October_19,_2011).pdf': 0}}

url = 'http://web.archive.org/web/20130103084334/https://www.lytro.com/'
# print(url in done_urls[2013])
pp.pprint(done_urls)
# print(len(done_urls[2013][0]))
# print(len(set(done_urls[2013][0])))


{2001: [['http://web.archive.org/web/123', 1, 'out/1018615691/2001/2/index.html'],
        ['http://web.archive.org/web/456', 1, 'out/1018615691/2001/7/index.html'],
        ['http://web.archive.org/web/789', 1, 'out/1018615691/2001/11/index.html']],
    2002: [['http://web.archive.org/web/123', 1, 'out/1018615691/2002/6/index.html'],
           ['http://web.archive.org/web/456', 1, 'out/1018615691/2002/11/index.html']]
 }

x = [1050192875, 1050086261, 1049296295, 1048362221, 1018615691, 659469,
     635633, 626443, 54662, 1004165561, 70156, 1045513901, 617413, 727900, 54763]
print(len(x))


response = [['timestamp'], ['20130614112713'], ['20140103102917'], ['20141218012058'], ['20160109191501'], ['20180104215319'], ['20181222211622'], ['20190614123339'], ['20200511050353'], ['20201112042918'], ['20210228195010'], ['20210316141729'], ['20210316143938'], ['20210316233115'], ['20210318190003'], ['20210420154746'], ['20210420174349'], ['20210612194451'], ['20210612194451'], ['20210612211822'], ['20210612211822'], ['20210713124456'], ['20210713130306'], ['20210713150130'], ['20210713180707'], ['20210806011623'], ['20210918161645'], ['20210922213602'], ['20210922225833'], ['20210928224309'], ['20211023164853'], ['20211130082930'], ['20211222204832'], ['20220122230718'], ['20220128080504'], [
    '20220225221123'], ['20220226054533'], ['20220325110747'], ['20220415170321'], ['20220428014459'], ['20220603162628'], ['20220603162823'], ['20220625140522'], ['20220627085800'], ['20220703045505'], ['20220720041940'], ['20220819112701'], ['20220823160208'], ['20220907160301'], ['20220926192801'], ['20220930133521'], ['20221020172508'], ['20221020203629'], ['20221024064245'], ['20221028155517'], ['20221129185509'], ['20221130094817'], ['20221130112844'], ['20221209023414'], ['20221210014634'], ['20230124190557'], ['20230128141242'], ['20230209222429'], ['20230319142828'], ['20230327134348'], ['20230327134349'], ['20230330201007'], ['20230330214324'], ['20230416045646'], ['20230425142803'], ['20230426034126']]
