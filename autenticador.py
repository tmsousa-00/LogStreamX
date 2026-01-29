# MODULO AUTENTICADOR
# DESENVOLVIDO EM PYTHON 3.10.9
#
# TRABALHO DE CONCLUSAO DE CURSO
# UNIVERSIDADE FEDERAL DE UBERLANDIA
# PÓS GRADUAÇÃO EM SEGURANÇA CIBERNÉTICA

import getpass, random, os, socket, hashlib, time, uuid, json
from threading import Thread
from datetime import datetime

from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential

LOG_ANALYTICS_DCE_ENDPOINT = url do dce criado no Azure 
LOG_ANALYTICS_DCR_RULE_ID = id do dcr que foi criado no Azure
LOG_ANALYTICS_DATA_STREAM_NAME = nome da tabela personalizada, por exemplo "Custom-NomeTabela_CL"

credential = DefaultAzureCredential()
log_ingestion_client = LogsIngestionClient(LOG_ANALYTICS_DCE_ENDPOINT, credential)

# armazena a porta que o módulo autenticador utilizará
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

# funçao que escolhe aleatoriamente um pais na lista para compor o log enviado para o Log Analytics
def paises():
   codPaises = ['BR','US','RU','KO','CH','AU','IN','FR','UK','IT']
   return random.choice(codPaises)

# funçao que gera endereços de IP aleatorios para compor o log enviado para o Log Analytics
def geraIP():
   nums_excluidos = {10, 127, 169, 172, 192, 224}
   oct1 = random.randint(1,251)
   while oct1 in nums_excluidos:
      oct1 = random.randint(1,251)   
   oct2 = random.randint(0,255)
   oct3 = random.randint(0,255)
   oct4 = random.randint(1,255)
   endIP = str(oct1) + '.' + str(oct2) + '.' + str(oct3) + '.' + str(oct4)
   return endIP

# funçao que imprime o banner do modulo
def print_menu():
   os.system('cls')
   print('----------------------------------------------')
   print('| * * * * * * * * LOGSTREAMX * * * * * * * * |')
   print('----------------------------------------------')
   print('|             MÓDULO AUTENTICADOR            |')
   print('----------------------------------------------')
   print('|  1. EFETUAR O LOGIN NO SISTEMA             |')
   print('|  2. FICAR VULNERAVEL A MFA FATIGUE ATTACKS |')
   print('|  3. SAIR                                   |')
   print('----------------------------------------------')

# variavel que armazena qual dos codigos MFA gerados é o que deverá ser inserido no modulo
# celular para que o login do usuario seja efetuado
numero_correto = ''

# o sistem deverá ficar vulneravel somente quando for selecionada a opção 2 do menu
vulneravel = False

# variaveis utilizadas no envio do log para o Azure
usuario = ''
numeroIP = ''
pais = ''
Correlation_Id = ''
Created_DateTime = ''

# define a quantidade de tentativas de senha antes de bloquear o usuario
max_tentativas = 5

# dicionario que contem os nomes dos usuarios e a quantidade de senhas erradas digitadas
bloqueios = {}

# valores possiveis do ResultType do log enviado ao Analytics:
login_ok = 0	# login efetuado com sucesso (usuario, senha e MFA corretos)
usrpwd_err = 50126	# usuario ou senha incorretos
mfa_err = 500121	# codigo MFA incorreto
mfa_neg = 500121	# usuario negou a autorizaçao em seu dispositivo movel
mfa_ign = 500121	# usuario ignorou a autorizaçao em seu dispositivo movel
usr_bloq = 50053	# o usuario digitou a senha errada varias vezes e a conta foi bloqueada   

# funcao que popula o dicionario de bloqueios, para que contenha os nomes de usuarios
# encontrados no arquivo de senhas juntamente com a quantidade inicial de senhas erradas
# digitadas, que no caso é 0
def popula_bloqueios():
   with open('senhas.txt', 'r') as arquivo:
      for line in arquivo:
         usr_arquivo, senha = line.strip().split(':')
         bloqueios[usr_arquivo] = 0

# funcao que retorna a quantidade de senhas erradas inseridas pelo usuario
def senhas_erradas(usuario):
   for nome in bloqueios.keys():
      if nome == usuario:
         return bloqueios[nome]

# funçao que envia os logs para o Log Analytics
def enviaLog(Created_DateTime, username, Result_Type, IP_Address, Local, Correlation_Id):
   log = {      
      "CreatedDateTime": Created_DateTime,
      "UserPrincipalName": username,
      "ResultType": Result_Type,
      "IPAddress": IP_Address,
      "Location": Local,
      "CorrelationId": Correlation_Id
   }

   try:
      log_ingestion_client.upload(
         rule_id=LOG_ANALYTICS_DCR_RULE_ID,
         stream_name=LOG_ANALYTICS_DATA_STREAM_NAME,
         logs=[log]
      )

   except Exception as e:
      print(f'Erro ao enviar log para o Azure: {e}')

# Funçao que fica na escuta por mensagens do modulo celular ou do atacante
def escutaMSG(cs):  

   global usuario, numeroIP, pais, Correlation_Id

   #inicializa as variaveis responsaveis por popular os logs

   log = {
      "CreatedDateTime": '',
      "UserPrincipalName": usuario,
      "ResultType": '99',
      "IPAddress": numeroIP,
      "Location": pais,
      "CorrelationId": Correlation_Id
   }

   while True:
      retorno = ''

      # recebe mensagens dos outros modulos e trata erros comuns
      try:       
         retorno = cs.recv(1024).decode()
      except ConnectionResetError:
         # se algum modulo se desconectar, nao fica mais na escuta por mensagens desse modulo
         break

      # recebe mensagem do modulo celular ou atacante, separando o nome do módulo com a mensagem enviada
      nome, msg = retorno.split('@')
             
      # trata as msgs recebidas de acordo com o modulo que as enviou  
      if nome == 'CELULAR':
         if msg.isdigit() == True: # se o retorno for um numero, verifica se é o numero correto
            if int(msg) == numero_correto:
               log['ResultType'] = login_ok
               print('Login efetuado com sucesso!')
            else:
               log['ResultType'] = mfa_err
               print('\nNumero selecionado incorreto!')
         else: # se nao for um numero, verifica se é N(egar) ou I(gnorar)
            if (msg.upper() == 'N'):
               log['ResultType'] = mfa_neg
               print('A autorização foi negada pelo usuario!')
            elif (msg.upper() == 'I'):
               log['ResultType'] = mfa_ign
               print('A autorização foi ignorada pelo usuario!')
         log['UserPrincipalName'] = usuario 
         log['IPAddress'] = numeroIP 
         log['Location'] = pais 
         horario = datetime.now()
         log['CreatedDateTime'] = horario.strftime("%m/%d/%Y, %H:%M:%S.%f") # atualiza o horario antes de enviar o log
         log['CorrelationId'] = Correlation_Id 
         enviaLog(log['CreatedDateTime'], log['UserPrincipalName'], log['ResultType'], log['IPAddress'], log['Location'], log['CorrelationId']) 

      elif nome == 'ATACANTE':
         msg = msg.replace("[","").replace("]","").replace("'","").replace(" ","")
         lista = msg.split(',')
         opcao = lista[0]
         usuario = lista[1]
         senha = lista[2] 

         # executa a opção selecionada no modulo atacante
         if opcao == '2':          
            fatigueattack(usuario, senha)
         elif opcao == '3':  
            fatigueattack(usuario, senha)

# funçao que verifica se o módulo está em execução e envia o indice do modulo na lista de sockets client_sockets
# se nao localizar retorna -1
def localizar(modulo):
   localizado = False
   for i in range(0, len(client_sockets)):
      if (client_sockets[i][1] == modulo.upper()):
         localizado = True
         return i
   # se o modulo nao estiver conectado, retorna -1
   return -1 

# funçao que envia mensagens para os modulos
def enviaMSG(mensagem, modulo): 
   localizado = localizar(modulo)
   client_sockets[localizado][0].send(mensagem.encode())

# funçao que conecta o módulo ao autenticador     
def conectar(socketCliente): 
    # a primeira mensagem recebida do módulo será sempre o nome que ele informou no momento da conexao
    nome = (socketCliente.recv(1024).decode()).upper()  
    # adiciona o socket do módulo na lista de sockets conectados
    client_sockets.append([socketCliente,nome])  

    # inicia uma thread diferente para cada módulo para poder escutar mensagens individualmente
    t = Thread(target=escutaMSG, args=(socketCliente,))
    # torna a thread um daemon para que finalize quando a thread principal finalizar
    t.daemon = True
    # inicia a thread
    t.start()

# A funçao abaixo gera 3 numeros aleatorios a serem exibidos no celular após inserir a senha correta
# E tambem calcula aleatoriamente qual dos 3 numeros gerados o usuario precisara informar no celular
# Utiliza um parametro que define se o sistema está sendo alvo de ataque de fadiga MFA
def gerarMFA(attack_mode):
   global numeroIP, pais
   
   log = {
      "CreatedDateTime": Created_DateTime,
      "UserPrincipalName": usuario,
      "ResultType": '',
      "IPAddress": numeroIP,
      "Location": pais,
      "CorrelationId": Correlation_Id
   }

   # gera uma lista temporaria contendo numeros de 1 a 99
   lista_random = list(range(1,100)) 
   # seleciona 3 numeros aleatorios da lista criada acima
   numeros_unicos = random.sample(lista_random, 3)
   # gera aleatoriamente o indice dos numeros que foram gerados, que será o numero que deverá ser digitado no celular
   idx_numero_correto = random.randint(0,2)
   global numero_correto # tornar a variavel global permite que se altere o valor dela mesmo se tiver
                         # sido declarada fora da funçao
   numero_correto = numeros_unicos[idx_numero_correto]  
 
   # se estiver em modo ataque, apenas envia a msg para o celular pedindo para digitar o numero correto
   # se nao estiver, aparecerá no autenticador tambem o numero correto que deverá ser inserido no celular
   if attack_mode == False:
      print(f'\nSelecione o numero [{numero_correto:02d}] na solicitação de entrada em seu dispositivo móvel...')
   else:
      print(f'\nSelecione o numero [{numero_correto:02d}] na solicitação de entrada em seu dispositivo móvel...')
      log['ResultType'] = mfa_err
      enviaLog(log['CreatedDateTime'], log['UserPrincipalName'], log['ResultType'], log['IPAddress'], log['Location'], log['CorrelationId']) 
   mensagem = f'\nDigite o numero correto para entrar:   [ {numeros_unicos[0]:02d} ] [ {numeros_unicos[1]:02d} ]  [ {numeros_unicos[2]:02d} ]   [N]egar  [I]gnorar'
   enviaMSG(mensagem, 'CELULAR')

# converte a senha digitada para md5 e compara com o arquivo de senhas
def md5hash(texto):
   m = hashlib.md5()
   m.update(texto.encode())
   return(m.hexdigest())

# autentica o usuario usando como parametros o nome, a senha e outro parametro que identifica
# se o sistema está sendo alvo de ataque de fadiga MFA
def autenticar(usr, pwd, attack_mode):
   global numeroIP, pais, Correlation_Id, Created_DateTime  

   if attack_mode == False:
      numeroIP = geraIP()
      pais = paises()
  
   Correlation_Id = str(uuid.uuid4())
   horario = datetime.now()
   Created_DateTime = horario.strftime("%Y-%m-%d, %H:%M:%S.%f")

   log = {
      "CreatedDateTime": Created_DateTime,
      "UserPrincipalName": usr,
      "ResultType": '',
      "IPAddress": numeroIP,
      "Location": pais,
      "CorrelationId": Correlation_Id
   }

   usr_localizado = False 
   senha_correta = False
   # percorre o arquivo de senhas em busca do usuario
   # se o usuario for encontrado e nao estiver bloqueado
   # verifica se a senha está correta
   # se o usuario estiver bloqueado, apresenta um erro
   with open('senhas.txt', 'r') as arquivo:
      for line in arquivo:
         usr_correto, pwd_correto = line.strip().split(':')
         if usr == usr_correto: 
            if bloqueios[usr] == max_tentativas:
               print('O usuário está bloqueado! Solicite ao administrador o desbloqueio.')
               return -1
            else:
               usr_localizado = True 
               if md5hash(str(pwd)) == pwd_correto:
                  senha_correta = True
               break # se o usuario for encontrado no arquivo, nao procurar mais

   # Se usuario e senha estiverem corretos, zera o contador de senhas erradas
   # e gera os codigos MFA 
   # Se o usuario ou a senha estiverem incorretos, incrementa o contador de senhas erradas
   # caso o usuario exista e exibe um erro, se o usuario nao existir apenas exibe o erro
   if usr_localizado:
      if senha_correta == True:
         bloqueios[usr] = 0
         gerarMFA(attack_mode)
         if attack_mode != True:
            input()
      else:
         bloqueios[usr] += 1
         if bloqueios[usr] == max_tentativas:
            print(f'Senha incorreta informada {max_tentativas} vezes. USUÁRIO BLOQUEADO!')
            log['ResultType'] = usr_bloq
            enviaLog(log['CreatedDateTime'], usr, log['ResultType'], log['IPAddress'], log['Location'], log['CorrelationId']) 
         else:  
            log['ResultType'] = usrpwd_err  
            enviaLog(log['CreatedDateTime'], usr, log['ResultType'], log['IPAddress'], log['Location'], log['CorrelationId']) 
            print('\nUsuario não localizado ou senha incorreta!')
            return -1
   else:
      print('\nUsuario não localizado ou senha incorreta!') 
      return -1  
  
# executa o ataque de fadiga MFA utilizando como parametros o usuario, a senha e outro parametro que identifica
# se o sistema está sendo alvo de ataque de fadiga MFA
def fatigueattack(usuario, senha): 
   global numeroIP, pais

   numeroIP = geraIP()
   pais = paises()

   # executa o ataque somente se o sistema estiver vulneravel
   if vulneravel == True:
      # se usuario/senha estiverem corretos, efetua o ataque
      print_menu()
      print('\n\033[1m\033[31mA T E N Ç Ã O !!! S I S T E M A  S O B  A T A Q U E !!!\033[0m\n')
      for i in range(0,6):
         autenticar(usuario,senha,True)
         time.sleep(0.7)

def iniciar():

   global vulneravel # vamos precisar alterar o valor dessas variaveis, que foram declaradas fora da funçao,
   global usuario    # por isso utilizamos a palavra-chave global                  
  
   # inicia o modulo autenticador somente quando os outros dois modulos se conectarem no autenticador
   print('Aguardando inicialização dós módulos...')

   while localizar('CELULAR') == -1:
      client_socket, client_address = s.accept()
      conectar(client_socket)

   while localizar('ATACANTE') == -1:
      client_socket, client_address = s.accept()
      conectar(client_socket)

   # chama a função que popula o dicionario de usuarios e quantidade de senhas digitadas erradas
   popula_bloqueios()

   # chama a funçao que imprime o banner do modulo na tela
   print_menu()

   opcaoInvalida = True
   sair = False

   # caso o usuario digite uma opção invalida, mostra um erro e solicita que digite uma opção válida
   while opcaoInvalida:
      while sair == False:
         opcao = input('\nEscolha uma opção: ')
         if opcao == '1':
            opcaoInvalida = False
            usuario = input('\nDigite seu nome de usuário: ')
            senha = getpass.getpass('Digite a senha: ')
            autenticar (usuario, senha, False)
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

         elif opcao == '2':
            opcaoInvalida = False
            vulneravel = True
            print('\n\033[1m\033[31mO SISTEMA ESTÁ VULNERÁVEL A ATAQUES !!!\033[0m\n')
            input()
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()
            vulneravel = False

         elif opcao == '3':
            opcaoInvalida = False
            sair = True

         else:
            print('\nOpção invalida selecionada')
            input('\nPressione qualquer tecla para voltar ao menu...')
            print_menu()

if __name__ == "__main__":

   #limpa a tela
   os.system('cls')

   try:
      # inicializa a lista de sockets de usuarios conectados
      client_sockets = []
      # cria um socket TCP
      s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      # faz um bind do socket com o endereço especificado
      s.bind((SERVER_HOST, SERVER_PORT))
      # fica na escuta por conexões
      s.listen()
      iniciar()

   except ConnectionResetError:
      print('\nConexão perdida com o módulo!')
      print('\nPressione qualquer tecla para sair...')
      input()

   except KeyboardInterrupt:
      print('\n\nMódulo encerrado através do CTRL-C!')
      input()