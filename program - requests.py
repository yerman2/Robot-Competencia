import time
import os
import re

import traceback
import datetime
import shutil
from math import ceil
import pandas as pd
import requests
import html
from PIL import Image
import imagehash

def compare_images(image1, image2):
    hash1 = imagehash.average_hash(Image.open(image1))
    hash2 = imagehash.average_hash(Image.open(image2))
    difference = hash1 - hash2
    return difference


'''
code = 'MCO1691238124'
difference = compare_images(f'Downloads\\{code}_AMZ.jpg', f'Downloads\\{code}_ML.jpg')
print(f"A diferença entre os hashes das imagens é: {difference}")
'''




#iguales:      https://www.mercadolibre.com.co/p/MCO22658909           https://articulo.mercadolibre.com.co/MCO-1348771371





try:
    print('Reading input data       ', end = '\r')
    #pegando dados dos arquivos txt
    with open('timeout.txt', 'r', encoding='utf8') as file:
        timeout = file.read()
    for i in [' ', '\t', '\n']:
        timeout = timeout.replace(i, '')
    timeout = float(timeout)




    paginas_a_consultar = input('Paginas a consultar: ')
    paginas_a_consultar = int(paginas_a_consultar)
    numero_ventas_minimo = input('Numero minimo de ventas (ex: 0, 1, 5, 25, 100): ')
    numero_ventas_minimo = int(numero_ventas_minimo)
    print('')




    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }



    #deletando arquivos que por ventura estejam na pasta de downloads
    for diretorio, subpastas, arquivos in os.walk('Downloads'):
        for arquivo in arquivos:
            name = os.path.join(diretorio, arquivo)
            name_file = os.getcwd() + '\\' + name
            try:
                os.remove(name_file)
            except:
                pass




    #lendo XLSX de inputs
    for diretorio, subpastas, arquivos in os.walk('Excel'):
        for file in arquivos:
            if file.count('.xls') != 0 or file.count('.xlsx') != 0:
                arquivo_XLSX = 'Excel/' + file
    df_inputs = pd.read_excel(arquivo_XLSX)
    n_rows = len(df_inputs[df_inputs.columns[0]])
    df = df_inputs


    results = 'AMZ URL\tML URL\tML title\tURLs\tDifference\n'
    for i in range(0, n_rows):
        url_orig = str(df_inputs[df_inputs.columns[0]][i])# + '_Desde_101'
        print(f'URL {i + 1}/{n_rows} - {url_orig}')
        code_list = []
        for page in range(1, 41):
            if page == 1:
                url = url_orig
            else:
                url = url_orig + f'_Desde_{50*(page - 1) + 1}'
            response = requests.get(url, headers=headers)
            time.sleep(timeout)
            text = response.text
            
            codes = text.split('meli_ga("set", "dimension49", "')[1].split('");')[0]
            code_list = code_list + codes.split(',')
            if page == 1:
                total_anuncios = text.split('meli_ga("set", "dimension22", "')[1].split('"')[0]
                total_pages = ceil(int(total_anuncios) / 50)
            print(f'\tExtracting articles from page {page}/{total_pages}', end = '\r')
            if page == total_pages or page == paginas_a_consultar:
                break
        print('')


            

        


        for code in code_list:
            print(f'\tProcessing article {code_list.index(code) + 1}/{len(code_list)} - {code}')#, end = '\r')

            for cicle in range(1, 2):
                try:
                    url = f'https://articulo.mercadolibre.com.co/{code[:3]}-{code[3:]}'
                    response = requests.get(url, headers=headers)
                    time.sleep(timeout)
                    text = response.text
                    
                    try:
                        sold = text.split('<span class="ui-pdp-subtitle">')[1].split('<')[0]
                        sold = re.findall(r'\d+', sold)[0]
                        sold = int(sold)
                    except:
                        sold = 0

                    try:
                        title = text.split('"dimension129", "')[1].split('"')[0]
                    except:
                        title = text.split('<meta property="og:title" content="')[1].split('"')[0]
                        title = title.rsplit(' - ', 1)[0]
                    title3 = str(title)
                    title2 = html.unescape(title3)
                    title = html.unescape(title2)

                    img_url_ML = text.split('<meta property="og:image" content="')[1].split('"')[0]



                    #baixando imagem do ML
                    resposta = requests.get(img_url_ML)
                    caminho_arquivo = f'Downloads\\{code}_ML.jpg'
                    with open(caminho_arquivo, 'wb') as arquivo:
                        arquivo.write(resposta.content)


                    print(f'\t\tTitle: {title}')
                    print(f'\t\tImage: {img_url_ML}')




                    





                    
                    

                    if sold >= numero_ventas_minimo:
                        print(f'\t\tSold: {sold}')



                        #buscando em google
                        url_google = f'https://www.google.com/search?q=site%3Aamazon.com%2F-%2Fes+{title}'
                        response = requests.get(url_google, cookies={"CONSENT":"YES+shp.gws-20210330-0-RC1.de+FX+412"})#, cookies={"CONSENT":"YES+shp.gws-20210330-0-RC1.de+FX+412"}, headers=headers
                        time.sleep(timeout)
                        text = response.text
                        #with open('aaaaaaaa.txt', 'w', encoding='utf8') as file:
                        #    file.write(text)

                        sp = text.split('href="/url?q=')
                        sp.pop(0)
                        links = []
                        URLs_text = ''
                        for ele in sp:
                            link = ele.split('&amp;sa=U&amp;', 1)[0]
                            link_temp = link.replace('www.', '')
                            link_temp = link_temp.replace('https://', '')
                            link_temp = link_temp.replace('http://', '')
                            if link.count('support.google.com') == 0 and link.count('accounts.google.com') == 0 and link.count('www.amazon.com/-/es/') > 0 and link.count('/dp/') > 0:
                                links.append(link)
                                URLs_text += link + '                            '
                                #print(f'\t\t\t{link}')
                        print(f'\t\tGoogle: {len(links)} matches')



                        #escojiendo url
                        for candidato in links:
                            title_candidato = candidato.split('amazon.com/-/es/')[1]
                        AMZ_URL = ''
                        if len(links) > 0:
                            AMZ_URL = links[0]

                        title_amz = title_candidato


                        difference = 100
                        #colectando imagen de AMZ
                        if AMZ_URL == '':
                            pass
                            #os.remove()
                        else:
                            headers_amz = {
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Cookie': 'lc-main=es_US; i18n-prefs=USD'
                            }
                            session = requests.Session()
                            response = session.get(AMZ_URL, headers=headers_amz)
                            #response = requests.get(url, headers=headers_amz)
                            time.sleep(timeout)
                            text = response.text



                            #images
                            text = text.split('ImageBlockATF')[1]
                            text = text.split('colorImages')[1]
                            text = text.split('\n')[0]
                            sp = text.split('"hiRes":"')
                            sp.pop(0)
                            urls_amz = []
                            for s in sp:
                                url_amz = s.split('"')[0]
                                urls_amz.append(url_amz)
                                
                                #baixando imagem para a pasta local
                                resposta = requests.get(url_amz)
                                caminho_arquivo = f'Downloads\\{code}_AMZ.jpg'
                                with open(caminho_arquivo, 'wb') as arquivo:
                                    arquivo.write(resposta.content)
                                break



                            #similaridade das imagens
                            difference = compare_images(f'Downloads\\{code}_AMZ.jpg', f'Downloads\\{code}_ML.jpg')
                            print(f"\t\t[Image difference: {difference}]")
                            

                        



                        #results
                        results += f'{AMZ_URL}\t{url}\t{title}\t{URLs_text}\t{difference}\n'
                        with open('results_temp.txt', 'w', encoding='utf8') as file:
                            file.write(results)
                        df = pd.read_csv('results_temp.txt', sep='\t', dtype='unicode', low_memory=False, on_bad_lines='skip')
                        df.to_excel('results.xlsx', 'Sheet1', index=False)  
                    else:
                        print(f'\t\tSold: {sold} (too few sales)')
                    break
                except:
                    if cicle == 0:
                        print('\t\t\tSome error ocurred, retrying...')
                    else:
                        print('\t\t\tSome error ocurred!')
                        print(traceback.format_exc())####
                    time.sleep(10)
except:
    print('\n\tSome error occurred... ')
    print(traceback.format_exc())

try:
    driver.quit()
except:
    pass
        

end = input('\n\nProgram finished! Press ENTER to close')
