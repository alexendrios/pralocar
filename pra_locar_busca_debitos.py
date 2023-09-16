from rich.console import Console
from rich.table import Table 
from rich import print 
from datetime import datetime
from time import sleep
from playwright.sync_api import sync_playwright
import pandas as pd
import shutil
import webbrowser, os


console = Console(record=False)
#Caminho objeto avo para a extração dos Dados
url="https://www.go.gov.br/servicos-digitais/detran/consulta-veiculos"

# Dados Referente as Registros Placa e Renavam
df= pd.read_csv('./data/carretinhas1.csv', sep=';')

print("\n[yellow][b]Pra Locar[/][/]\n[red]*********[/]")
with console.status('Configurando o sistema\n...'):
        sleep(3)
        
diretorio = './carretinhas/infracoes/'         
if(os.path.exists(diretorio)):
    shutil.rmtree(diretorio)
    
diretorio_resultData='./carretinhas/data/'
if(os.path.exists(diretorio_resultData)):
    shutil.rmtree(diretorio_resultData)

os.mkdir(diretorio_resultData)

def data_agora():
   data = datetime.now()
   data2 = data.strftime("%d/%m/%Y %H:%M:%S") 
   return data2

#Configuração
def navegar():
    playwright = sync_playwright().start()  
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    return page, browser, playwright

page, browser, playwright = navegar()
page.goto(url)

#variáveis Identificação dataSet
coluna_situacao = 'Situação'
coluna_quantidade = 'Quantidade'
coluna_valor = 'Valor (R$)'
coluna_valor_desconto ='Valor com Desconto (R$)'
vencida = 'Vencidas'
nao_vencidas = 'Não Vencida'
sob_judice ='Sob Judice'
parcelada ='Parcelada'
notificada ='Notificada'
sne ='SNE - Sistema de Notificação Eletrônica'

#Variável responsável para a ciação do doc .csv
info_infracoes = 'Placa;Quantidade;Valor (R$);Valor com Desconto (R$);Situação\n'

#Mapeamento
form_placa = "//html//body//app-root//app-raiz-servicos-digitais//body//div//div//div//div//lib-consultar-dados//div[2]//div//form/div[1]//div[1]//exui-input//div//mat-form-field//div//div[1]//div[3]//input"
form_renavan = "//html//body//app-root//app-raiz-servicos-digitais//body//div//div//div//div//lib-consultar-dados//div[2]//div//form//div[1]//div[2]//exui-input//div//mat-form-field//div//div[1]//div[3]//input"
btn_voltar=page.locator("//html[1]//body[1]//div[4]//div[2]//div[1]//mat-dialog-container[1]//lib-dialog-detalhe-infracao[1]//div[1]//div[1]//div[1]//div[1]//exui-outline-button[1]//div[1]")
btn_consultar= page.locator("form > div:nth-child(2) exui-button-primary  button")
menu_debitos_veiculos=page.locator("//span[contains(.,'Débitos do Veículo')]")
opcao_debitos_veiculos=page.locator("//h2[contains(.,'Débitos do Veículos')]")
tabela_debito_veiculo =page.locator("lib-debitos-veiculo  exui-accordion:nth-child(1) div.responsive_table.mat-container-table  table")
debitos_infracoes=page.locator("//h2[contains(.,'Débitos de Infrações')]")
paginacao =page.locator("ul.paginator-filtro")


def encerrar():
    browser.close()
    playwright.stop()  
    
def inicio_busca(placa, renavan): 
    page.locator(form_placa).fill(placa)
    page.locator(form_renavan).fill(renavan) 
   
    #Animação
    with console.status('\nCarregando Dados\n...'):
        sleep(3) 
         
    #Animação
    with console.status('[yellow]Buscando Veículo[/]\n...', spinner='earth'):
        sleep(3) 
    btn_consultar.click()
    sleep(3) 

#Métodos - Filtra os Dados e retorna a Soma
def soma_dataframe(df, condicao1, condicao2,condicao3):
    soma = df[df[condicao1] == condicao2]
    return sum(soma[condicao3])

#Método responsável para regulariar os Dados Monetários
def regularizar_dados(df, coluna):
    df[coluna]=(df[coluna].
        str.replace('.', '').
        str.replace(',', '.').
        astype(float)
    )

print(f"[green b]start:[/] {data_agora()}\nSoftware de Busca de [b]Débitos[n]\n[b][u]Carretinhas[/][/]\n\n[green][b]Detran - Goiás[/][/]")
print(f'Fonte das Buscas:\n{page.title()}')

# Referencias a quantidades de veículos
for index in range(len(df)): 
    placa = df['PLACA'][index]
    renavan = '0'+str(df['RENAVAN'][index])
    
    '''  * Registros - Débitos veículos'''
    
    inicio_busca(placa, renavan)   
    print(f"\n[yellow]Pesquisa Carretinha[/] - {index +1}\n")  
    sleep(5)  
    menu_debitos_veiculos.click()
    sleep(2)
    opcao_debitos_veiculos.click()
    sleep(2)
    
    x=tabela_debito_veiculo.text_content()
    tb = Table(title=f"Verificação - Débitos do Veículo - Carretinha - PLACA: {placa} - RENAVAN: {renavan}")
    tb.add_column(f'{x[0:17].strip()}')
    tb.add_column(f'{x[25:44].strip()}')
    tb.add_column(f'{x[54:80].strip()}')
    tb.add_column(f'{x[97:121].strip()}')
    tb.add_column(f'{x[130:153].strip()}')
    tb.add_column(f'{x[160:189].strip()}')
    tb.add_column(f'{x[190:226].strip()}')

    for i in range(1,2):        
        ano=page.locator(f"tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-anoExercicio.mat-column-anoExercicio.ng-star-inserted").text_content()
        ipva=page.locator(f"table tbody tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorIpva.mat-column-valorIpva.ng-star-inserted").text_content()
        licenciamento = page.locator(f"table tbody tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorLicenciamento.mat-column-valorLicenciamento.ng-star-inserted").text_content()   
        seg_obrigatorio = page.locator(f"table tbody tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorSeguro.mat-column-valorSeguro.ng-star-inserted").text_content()
        infracoes = page.locator(f"table tbody tr:nth-child({i})  td.mat-cell.cdk-cell.cdk-column-valorMulta.mat-column-valorMulta.ng-star-inserted").text_content()
        data_vencimento = page.locator(f"table tbody tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-dataVencimento.mat-column-dataVencimento.ng-star-inserted").text_content()
        valor_total = page.locator(f"table tbody tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorTotal.mat-column-valorTotal.ng-star-inserted").text_content()
        tb.add_row(ano, ipva, licenciamento, seg_obrigatorio, infracoes, data_vencimento, valor_total )
    
    #imprime Tabela Débitos Veículo
    console.print(tb)
    print('\n')
    
    opcao_debitos_veiculos.click()
    sleep(2)
    debitos_infracoes.click()
    sleep(2)
    
    ''' * Registros de Infrações '''
   
    #Registros da Tabela Infraçõess
    tb = Table(title=f"Resumo - Débitos de Infrações - Carretinha - PLACA: {placa} - RENAVAN: {renavan}")
    tb.add_column(coluna_situacao)
    tb.add_column(coluna_quantidade)
    tb.add_column(coluna_valor)
    tb.add_column(coluna_valor_desconto)
    
    valores = []
    for i in range(1,7):
        if(page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-quantidade.mat-column-quantidade.ng-star-inserted').is_visible()):
            qtd = int(page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-quantidade.mat-column-quantidade.ng-star-inserted').text_content())
            valores.append(qtd)
    if(sum(valores) == 0):
        print(f"CARRETINHA PLACA: [green b]{placa}[/] RENAVAN: [green b]{renavan}[/]\n[green blink b]:white_check_mark:\tSEM INFRAÇÕES[/]")
    else:
      
       for i in range(1,7):
           
           registro_situacao =f"{page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-situacao.mat-column-situacao.ng-star-inserted').text_content()}"
           regstro_quantidade=f"{page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-quantidade.mat-column-quantidade.ng-star-inserted').text_content()}"
           registro_valor=f"{page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorNormal.mat-column-valorNormal.ng-star-inserted').text_content()}"
           registro_valor_desconto=f"{page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-valorComDesconto.mat-column-valorComDesconto.ng-star-inserted').text_content()}"          
           valor_registro_valor=registro_valor.strip('R$').strip()
           
           #Valores Responsável para a criação do Arquivo .CSV
           valor_registro_valor_desconto = ''
           if(registro_valor_desconto == 'Sem Desconto'):
               valor_registro_valor_desconto = '0.00'
           else:
              valor_registro_valor_desconto = registro_valor_desconto.strip('R$').strip()
              
           info_infracoes += f'{placa};{regstro_quantidade};{valor_registro_valor};{valor_registro_valor_desconto};{registro_situacao}\n'
           
           tb.add_row(
                registro_situacao, 
                regstro_quantidade,
                registro_valor,
                registro_valor_desconto
                )
           
           qtd_registros = int(page.locator(f'tr:nth-child({i}) td.mat-cell.cdk-cell.cdk-column-quantidade.mat-column-quantidade.ng-star-inserted').text_content())   
           if(qtd_registros != 0):
               page.locator(f"//html/body//app-root//app-raiz-servicos-digitais//body//div//div//div//div//lib-detalhes-veiculo//div[2]//div//exui-abas-nav//div//div//exui-aba-nav[2]//div//lib-debitos-veiculo//div//exui-acordeons//exui-accordion[2]//div//div[2]//div//div//exui-table//table//tbody//tr[{i}]//td[5]//exui-icon//img").click()            
               n=1
               for i in range(1,(qtd_registros+1)):
                   numero_infracao = page.locator(f"(//td[contains(@class,'mat-cell cdk-cell cdk-column-autoInfracao mat-column-autoInfracao ng-star-inserted')])[{n}]").text_content()
                   page.locator(f"(//img[contains(@width,'24')])[{n}]").click()
                   sleep(2)
                   arquivo_captura = f'{diretorio}{placa}/{placa}_{renavan}_numero_infracao_{numero_infracao}.png'
                   page.locator("div[class='cdk-overlay-pane']").screenshot(path=arquivo_captura)
                   print(f'[#FF00FF]Realizando a captura da infração:[/]   [red b u]{numero_infracao}[/]')
                   btn_voltar.click()
                   sleep(2)
                   if((i+5)%5 == 0):
                      n=1
                      page.locator("//span[contains(.,'Próximo >')]").click()
                   else:
                       n+=1    
               page.go_back() 
               sleep(6)  
               menu_debitos_veiculos.click()
               sleep(3)
               debitos_infracoes.click()
               sleep(2)    
       
       #Imprimir tabela - Infrações 
       print('\n')       
       console.print(tb)
      
       print(f"\nCARRETINHA PLACA: [red b]{placa}[/] RENAVAN: [red b]{renavan}[/]\n:no_entry:\t[yellow on red blink b]INFRAÇÕES[/]\n")     

    debitos_infracoes.click()
    sleep(3) 
    page.go_back() 
    sleep(3) 
    
    #Animação  
    with console.status('Reiniciando os Dados\n...'):
         sleep(5)
#Animação
with console.status('Finalizando a Operação: Busca de Infrações\n...'):
         sleep(5)
         
encerrar()
print("[#7FFF00]\n\nPesquisa de Infrações Finalizadas[/]\n\n")

#Criação de um arquivo CSV - Consolidação das informações de Infrações
arquivo_csv = f"{diretorio_resultData}infracoes.csv"
with open(arquivo_csv, "w", encoding='utf-8') as arquivo:
	arquivo.write(info_infracoes)
 
sleep(2)

'''   * Criação do Report - Dados Gerais - Infrações'''

#criação do DataSet - Produto Resultante da aplicação
df2 = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8')

#Aplicando a normalização
regularizar_dados(df=df2, coluna=coluna_valor)
regularizar_dados(df=df2, coluna=coluna_valor_desconto)

#Soma - Quantidade
qtd_vencidas = soma_dataframe(df2, coluna_situacao, vencida, coluna_quantidade)
qtd_nao_vencidas= soma_dataframe(df2, coluna_situacao, nao_vencidas, coluna_quantidade)
qtd_sob_judice = soma_dataframe(df2, coluna_situacao, sob_judice, coluna_quantidade)
qtd_parcelada = soma_dataframe(df2, coluna_situacao, parcelada, coluna_quantidade)
qtd_notificada = soma_dataframe(df2, coluna_situacao, notificada, coluna_quantidade)
qtd_sne = soma_dataframe(df2, coluna_situacao, sne, coluna_quantidade)

#Soma Valor
valor_vencidas = soma_dataframe(df2, coluna_situacao, vencida, coluna_valor)
valor_nao_vencidas= soma_dataframe(df2, coluna_situacao, nao_vencidas, coluna_valor)
valor_sob_judice = soma_dataframe(df2, coluna_situacao, sob_judice, coluna_valor)
valor_parcelada = soma_dataframe(df2, coluna_situacao, parcelada, coluna_valor)
valor_notificada = soma_dataframe(df2, coluna_situacao, notificada, coluna_valor)
valor_sne = soma_dataframe(df2, coluna_situacao, sne, coluna_valor)

#Soma Valor Com Desconto
valor_desconto_vencidas = soma_dataframe(df2, coluna_situacao, vencida, coluna_valor_desconto)
valor_desconto_nao_vencidas= soma_dataframe(df2, coluna_situacao, nao_vencidas, coluna_valor_desconto)
valor_desconto_sob_judice = soma_dataframe(df2, coluna_situacao, sob_judice, coluna_valor_desconto)
valor_desconto_parcelada = soma_dataframe(df2, coluna_situacao, parcelada, coluna_valor_desconto)
valor_desconto_notificada = soma_dataframe(df2, coluna_situacao, notificada, coluna_valor_desconto)
valor_desconto_sne = soma_dataframe(df2, coluna_situacao, sne, coluna_valor_desconto)

#informações Gerais - Informações Consoliidadas
qtd_registro_careretinhas_infacoes= df2['Placa'].nunique()
qtd_reegistros_infracoes = sum(df2['Quantidade'])
valores_infracoes = sum(df2['Valor (R$)'])
valores_infracoes_desconto = sum(df2['Valor com Desconto (R$)'])

#Criação das Tabelas - Resumo dos Dados
tb1 = Table(title="Resumo Das Infrações - Dados Gerais")
tb1.add_column('QTD. Carretinhas com Infrações')
tb1.add_column('QTD. Infrações')
tb1.add_column('Total de Valores')
tb1.add_column('Total de Valores Com Desconto')

tb1.add_row(
        str(qtd_registro_careretinhas_infacoes),
        str(qtd_reegistros_infracoes),
        f'R$ {str(round(valores_infracoes, 2))}',
        f'R$ {str(round(valores_infracoes_desconto,2))}'        
         )

tb2 = Table(title="Resumo Das Infrações - Débitos das Infrações - Geral")
tb2.add_column(coluna_situacao) 
tb2.add_column(coluna_quantidade)
tb2.add_column(coluna_valor)
tb2.add_column(coluna_valor_desconto)

tb2.add_row(
    vencida,
    str(qtd_vencidas),
    f'R$ {str(round(valor_vencidas, 2))}',
    f'R$ {str(round(valor_desconto_vencidas,2))}'
)
tb2.add_row(
    nao_vencidas,
    str(qtd_nao_vencidas),
    f'R$ {str(round(valor_nao_vencidas, 2))}',
    f'R$ {str(round(valor_desconto_nao_vencidas,2))}'
)
tb2.add_row(
    sob_judice,
    str(qtd_sob_judice),
    f'R$ {str(round(valor_sob_judice, 2))}',
    f'R$ {str(round(valor_desconto_sob_judice,2))}'
)
tb2.add_row(
    parcelada,
    str(qtd_parcelada ),
    f'R$ {str(round(valor_parcelada, 2))}',
    f'R$ {str(round(valor_desconto_parcelada,2))}'
)
tb2.add_row(
    notificada,
    str(qtd_notificada),
    f'R$ {str(round(valor_notificada, 2))}',
    f'R$ {str(round(valor_desconto_notificada,2))}'
)
tb2.add_row(
    sne,
    str(qtd_sne),
    f'R$ {str(round(valor_sne, 2))}',
    f'R$ {str(round(valor_desconto_sne,2))}'
)

#Animação
with console.status('[yellow]Realizando Análise[/]\n...', spinner='earth'):
        sleep(3) 

print('\n\n[#FF8C00 b]Resultado da Análise dos Dados de Infrações- Consolidados[/]\n')
console.print(tb2)
print()
console.print(tb1)
webbrowser.open(os.path.realpath(diretorio))
print(f"[green b]finish:[/] {data_agora()}")