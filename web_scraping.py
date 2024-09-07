import requests
from bs4 import BeautifulSoup
import io
from PIL import Image
import os
import math

# Defina a URL
url = "https://bcr.iphan.gov.br/wp-json/tainacan/v2/items/?perpage=96&order=ASC&orderby=date&exposer=html&paged=1"

# Função para baixar imagem a partir da URL
def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = os.path.join(download_path, file_name)

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print(f"Imagem {file_name} baixada com sucesso")
    except Exception as e:
        print(f'FALHA - {e}')

# Função para salvar descrição em um arquivo de texto
def save_description(download_path, file_name, description):
    try:
        file_path = os.path.join(download_path, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"Descrição salva com sucesso em {file_name}")
    except Exception as e:
        print(f'FALHA - {e}')

# Buscar os dados HTML
response = requests.get(url)

# Imprimir o status da resposta e o conteúdo para depuração
print(f"Código de Status da Resposta: {response.status_code}")
print("Conteúdo da Resposta:")
print(response.text[:500])  # Imprimir os primeiros 500 caracteres da resposta para inspeção

# Analisar HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Criar diretórios para salvar imagens e descrições se não existirem
download_path = "imgs/"
os.makedirs(download_path, exist_ok=True)

# Extrair URLs de imagens, títulos e descrições da tabela
table = soup.find('table', {'border': '1'})  # Encontrar a tabela pelo atributo border
if table:
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    rows = table.find('tbody').find_all('tr')
    
    image_counter = 0
    # Baixar todas as imagens
    max_images  = math.inf
    
    for row in rows:
        if image_counter >= max_images:
            break

        cells = row.find_all('td')
        data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
        
        # Extrair título e descrição (assumindo que título e descrição estão em colunas específicas)
        description = data.get('Descrição', 'Sem Descrição')
        title = data.get('Denominação', 'Sem Título')
        
        print(f"Título: {title}")
        print(f"Descrição: {description}")
        
        # Salvar descrição em um arquivo de texto
        description_filename = f"{title}.txt".replace('/', '_').replace(' ', '_')
        save_description(download_path, description_filename, description)
        
        # Extrair e visitar o link para a página de imagem detalhada
        link_column = cells[headers.index('Mídias')].find_all('a') if 'Mídias' in headers else []
        
        for link_tag in link_column:
            link_url = link_tag.get('href')
            if link_url and link_url.startswith('http'):
                # Visitar o link para encontrar a imagem detalhada
                image_page_response = requests.get(link_url)
                image_page_soup = BeautifulSoup(image_page_response.content, 'html.parser')
                
                # Encontrar a imagem na classe swiper-slide-content
                image_tag = image_page_soup.find('div', class_='swiper-slide-content').find('img')
                img_url = image_tag.get('src') if image_tag else None
                
                if img_url and img_url.startswith('http'):
                    # Gerar um nome de arquivo baseado no título e no índice da imagem
                    img_filename = f"{title}_{image_counter + 1}.jpg".replace('/', '_').replace(' ', '_')  # sanitizar nome do arquivo
                    download_image(download_path, img_url, img_filename)
                    image_counter += 1
                    if image_counter >= max_images:
                        break
                        
else:
    print("Tabela não encontrada no conteúdo HTML.")
